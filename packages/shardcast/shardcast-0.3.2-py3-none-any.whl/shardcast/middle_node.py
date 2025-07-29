"""Middle node for the shardcast package."""

import os
import time
import argparse
import threading
import shutil
from typing import List, Dict, Set
from pathlib import Path
import shardcast.server as server
from shardcast.client import ShardDownloader
from shardcast.envs import (
    SHARDCAST_HTTP_PORT,
    SHARDCAST_DISTRIBUTION_FILE,
    SHARDCAST_HTTP_TIMEOUT,
    SHARDCAST_VERSION_PREFIX,
)
from shardcast.utils import (
    ensure_dir,
    logger,
)


class MiddleNode:
    """Middle node for downloading and re-serving shards."""

    def __init__(
        self,
        upstream_servers: List[str],
        data_dir: str,
        port: int = SHARDCAST_HTTP_PORT,
        check_interval: int = 30,
    ):
        """Initialize the middle node.

        Args:
            upstream_servers: List of upstream server URLs or IP addresses
            data_dir: Directory to store and serve shards from
            port: HTTP port to listen on
            check_interval: Interval in seconds to check for new versions
        """
        self.upstream_servers = upstream_servers
        self.data_dir = os.path.abspath(data_dir)
        self.port = port
        self.check_interval = check_interval

        # Create downloader for fetching from upstream servers
        self.downloader = ShardDownloader(upstream_servers, SHARDCAST_HTTP_TIMEOUT)

        # Track which versions we have already processed
        self.processed_versions: Set[str] = set()

        # Track known shards per version
        self.known_shards: Dict[str, int] = {}

        # Processing lock
        self.lock = threading.Lock()

        # Shutdown event
        self.shutdown_event = threading.Event()

        # Ensure data directory exists
        ensure_dir(self.data_dir)

        # Start HTTP server
        self.http_server, self.server_thread = server.run_server(self.data_dir, self.port, self.shutdown_event)

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_upstream)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def _monitor_upstream(self) -> None:
        """Monitor upstream servers for new versions."""
        while not self.shutdown_event.is_set():
            try:
                # Download and parse distribution file
                if self.downloader.download_file(
                    SHARDCAST_DISTRIBUTION_FILE,
                    os.path.join(self.data_dir, SHARDCAST_DISTRIBUTION_FILE),
                    update_metrics=False,
                    retries=1,
                    log_error_on_failure=False,
                ):
                    with open(os.path.join(self.data_dir, SHARDCAST_DISTRIBUTION_FILE), "r") as f:
                        distribution_content = f.read()
                else:
                    if os.path.exists(os.path.join(self.data_dir, SHARDCAST_DISTRIBUTION_FILE)):
                        logger.warning("Failed to download distribution file, attempting to delete")
                        os.unlink(os.path.join(self.data_dir, SHARDCAST_DISTRIBUTION_FILE))
                    distribution_content = None

                if distribution_content:
                    # Parse the distribution file into a dictionary
                    distribution = {}
                    for line in distribution_content.strip().split("\n"):
                        if line and ":" in line:
                            version, info = line.strip().split(":", 1)
                            distribution[version.strip()] = info.strip()

                    # Process each version
                    for version, info in distribution.items():
                        self._process_version(version, info)

                    # Remove old versions if necessary
                    for version in Path(self.data_dir).glob(f"{SHARDCAST_VERSION_PREFIX}*"):
                        if version.stem not in distribution:
                            shutil.rmtree(os.path.join(self.data_dir, version.stem))
                            logger.info(f"Removed old version: {version.stem}")

            except Exception as e:
                import traceback

                traceback.print_exc()
                logger.error(f"Error monitoring upstream servers: {str(e)}")

            # Wait before checking again
            time.sleep(self.check_interval)

    def _process_version(self, version: str, info: str) -> None:
        """Process a version by downloading and serving its shards.

        Args:
            version: Version folder name (e.g., "v1")
            info: Information string with checksum and optionally shard count
        """
        # Skip if we've already processed this version
        if version in self.processed_versions:
            return
        with self.lock:
            # Extract checksum and possibly shard count from info
            checksum, _, shard_count = info.partition("|")
            if shard_count is None:
                raise ValueError(f"Shard count not found for version {version}")
            shard_count = int(shard_count)
            version_dir = os.path.join(self.data_dir, version)
            ensure_dir(version_dir)

            # If we know the exact number of shards, download them directly
            logger.info(f"Distribution file indicates {shard_count} shards for version {version}")

            # Start timer for total file download
            start_time = time.time()
            total_size = 0

            # Download all shards in parallel
            shards = self.downloader.download_shards(version, shard_count, version_dir)

            # Calculate download time and speed
            total_size = sum(os.path.getsize(shard) for shard in shards if os.path.exists(shard))
            download_time = time.time() - start_time
            download_speed_bps = total_size / max(download_time, 0.001)
            download_speed_mbps = download_speed_bps / (1024 * 1024)

            logger.info(f"Downloaded {total_size / (1024 * 1024):.2f} MB in {download_time:.2f} seconds")
            logger.info(f"Average download speed: {download_speed_mbps:.2f} MB/s")

            # Set as processed and store shard count
            self.known_shards[version] = shard_count
            self.processed_versions.add(version)
            logger.info(f"Finished downloading all {shard_count} shards for version {version}")
            return

    def shutdown(self) -> None:
        """Shutdown the middle node."""
        logger.info("Shutting down middle node...")
        self.shutdown_event.set()

        # Give threads a chance to exit cleanly
        time.sleep(0.5)

        if self.monitor_thread.is_alive():
            logger.warning("Monitor thread did not exit cleanly")

        if self.server_thread.is_alive():
            logger.warning("Server thread did not exit cleanly")


def main():
    """Run the middle node as a standalone script."""
    parser = argparse.ArgumentParser(description="Shardcast Middle Node")
    parser.add_argument(
        "--upstream",
        help="Comma-separated list of upstream server URLs or IP addresses (optional if IP_ADDR_LIST env var is set)",
    )
    parser.add_argument(
        "--data-dir",
        default="./middle_data",
        help="Directory to store and serve shards from",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=SHARDCAST_HTTP_PORT,
        help=f"HTTP port to listen on (default: {SHARDCAST_HTTP_PORT})",
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=30,
        help="Interval in seconds to check for new versions (default: 30)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    # Set log level
    logger.setLevel(args.log_level)

    # Check if IP_ADDR_LIST environment variable is set
    import os
    import re

    upstream_servers = []

    if args.upstream:
        # Parse from command-line argument
        upstream_servers = [s.strip() for s in args.upstream.split(",") if s.strip()]
    else:
        # Try to get from environment variable
        ip_addr_list = os.environ.get("IP_ADDR_LIST")
        if not ip_addr_list:
            logger.error("IP_ADDR_LIST environment variable not set and --upstream not provided")
            logger.error("Set IP_ADDR_LIST='ip1 ip2 ip3' or use --upstream parameter")
            return 1

        # Parse the environment variable - expected format: ("ip1" "ip2" "ip3")
        # Remove parentheses if present
        ip_addr_list = ip_addr_list.strip()
        if ip_addr_list.startswith("(") and ip_addr_list.endswith(")"):
            ip_addr_list = ip_addr_list[1:-1].strip()

        # Extract IPs within quotes
        quoted_ips = re.findall(r'"([^"]+)"', ip_addr_list)
        if quoted_ips:
            upstream_servers = quoted_ips
        else:
            # If no quoted IPs found, try space-separated format
            upstream_servers = [s.strip() for s in ip_addr_list.split() if s.strip()]

    if not upstream_servers:
        logger.error("No upstream servers specified")
        return 1

    logger.info(f"Using upstream servers: {upstream_servers}")

    # Start the middle node
    node = MiddleNode(
        upstream_servers=upstream_servers,
        data_dir=args.data_dir,
        port=args.port,
        check_interval=args.check_interval,
    )

    try:
        logger.info(f"Middle node running at http://{server.get_local_ip()}:{args.port}")
        logger.info(f"Serving files from {os.path.abspath(args.data_dir)}")
        logger.info(f"Monitoring upstream servers: {', '.join(upstream_servers)}")
        logger.info("Press Ctrl+C to exit")

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        node.shutdown()

    return 0


if __name__ == "__main__":
    exit(main())
