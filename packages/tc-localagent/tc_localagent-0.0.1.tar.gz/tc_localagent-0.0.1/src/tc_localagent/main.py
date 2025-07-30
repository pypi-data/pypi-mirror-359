def main():
    import argparse
    import sys
    from tc_localagent.server import start_server

    parser = argparse.ArgumentParser(description="Local AI QA Agent CLI")
    parser.add_argument("--port", type=int, default=43449, help="Port to run the server on")
    parser.add_argument("--env", type=str, default=".env.staging", help="Path to env file")
    parser.add_argument("--browser-mode", type=str, default="cdp", help="Browser mode: cdp or launch")
    parser.add_argument("--cdp-url", type=str, required=False, help="CDP WebSocket URL")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP stdin server (future)")

    args = parser.parse_args()

    if args.mcp:
        print("MCP mode is not yet implemented.")
        sys.exit(1)
    else:
        start_server(args)

if __name__ == "__main__":
    main()