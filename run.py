"""
run.py — Smart development server launcher.

Finds a free port starting from the preferred port and starts uvicorn.
Avoids the [Errno 48] Address already in use error automatically.

Usage:
    python run.py              # starts on first free port from 8000
    python run.py --port 9000  # starts on first free port from 9000
    python run.py --reload     # enable auto-reload (development mode)
"""

import argparse
import socket
import subprocess
import sys


def find_free_port(start: int = 8000, max_attempts: int = 10) -> int:
    """
    Find the first available TCP port starting from `start`.

    Args:
        start: Port number to begin scanning from.
        max_attempts: How many ports to try before giving up.

    Returns:
        First available port number.

    Raises:
        RuntimeError: If no free port is found within max_attempts.
    """
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # SO_REUSEADDR ensures we don't get false negatives from TIME_WAIT
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", port))
                return port  # bind succeeded — port is free
            except OSError:
                print(f"  Port {port} is in use, trying next...")

    raise RuntimeError(
        f"No free port found in range {start}–{start + max_attempts - 1}. "
        "Free a port manually and try again."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the Instruction Clarity Agent API")
    parser.add_argument("--port", type=int, default=8000, help="Preferred port (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    # Find a free port starting from the preferred one
    port = find_free_port(start=args.port)

    if port != args.port:
        print(f"⚠  Port {args.port} is busy — using port {port} instead.")
    else:
        print(f"✓  Port {port} is available.")

    # Build the uvicorn command
    cmd = [
        sys.executable, "-m", "uvicorn",
        "api.main:app",
        "--host", args.host,
        "--port", str(port),
    ]

    if args.reload:
        cmd.append("--reload")

    print(f"\n🚀  Starting server at http://{args.host}:{port}")
    print(f"    Docs: http://127.0.0.1:{port}/docs\n")

    # Replace current process with uvicorn (clean signal handling)
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Server exited with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
