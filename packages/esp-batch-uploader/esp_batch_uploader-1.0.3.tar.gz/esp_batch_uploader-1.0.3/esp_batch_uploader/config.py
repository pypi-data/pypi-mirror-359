import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch uploader configuration v1.0.3"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        choices=range(1, 21),
        metavar="[1-20]",
        help="Batch size (1–20). Default: 5"
    )

    parser.add_argument(
        "--http-port",
        type=int,
        default=8000,
        help="HTTP port (1–65535). Default: 8000"
    )

    parser.add_argument(
        "--udp-port",
        type=int,
        default=5757,
        help="UDP port (1–65535). Default: 5757"
    )

    parser.add_argument(
        "--directory",
        type=str,
        default=os.getcwd(),
        help="Directory to serve files from. Default: current working directory"
    )

    args = parser.parse_args()

    # Validate ports manually to give cleaner errors
    if not (1 <= args.http_port <= 65535):
        parser.error("HTTP port must be between 1 and 65535.")
    if not (1 <= args.udp_port <= 65535):
        parser.error("UDP port must be between 1 and 65535.")

    print(f"[INFO] Serving files from: {args.directory}")
    return args, args.directory
