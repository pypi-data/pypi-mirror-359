import uvicorn
import argparse


def main():
    parser = argparse.ArgumentParser(description="Run the Meridian 59 API server.")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        help="Set log level (default: info)",
    )

    args = parser.parse_args()

    print(f"\nAdmin API docs: http://{args.host}:{args.port}/docs")
    print(f"Example admin endpoint: http://{args.host}:{args.port}/api/v1/admin/status\n")


    uvicorn.run(
        "m59api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )
