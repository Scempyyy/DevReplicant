"""DevReplicant Command Line Interface."""

import argparse
import json
import sys
from devreplicant.collector import create_snapshot, generate_restore_script, generate_dockerfile
from devreplicant.server import start_replicant_server


def main():
    parser = argparse.ArgumentParser(
        prog="devreplicant",
        description="DevReplicant: Developer Environment Snapshotter & Re-hydration Engine.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # SNAPSHOT command
    snap_parser = subparsers.add_parser("snapshot", help="Capture machine environment snapshot")
    snap_parser.add_argument("-o", "--output", help="Write JSON manifest to file")
    snap_parser.add_argument("--export-script", help="Write restore.sh script to file")
    snap_parser.add_argument("--export-docker", help="Write Dockerfile to file")

    # SERVE command
    serve_parser = subparsers.add_parser("serve", help="Launch interactive snapshot web studio")
    serve_parser.add_argument("--port", type=int, default=8960, help="Port to bind (default: 8960)")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")

    args = parser.parse_args()

    if args.command == "serve" or args.command is None:
        port = getattr(args, "port", 8960)
        host = getattr(args, "host", "127.0.0.1")
        start_replicant_server(host=host, port=port)

    elif args.command == "snapshot":
        print("\n🧬 DevReplicant: Scanning system state and developer packages...")
        snap = create_snapshot()
        sys_info = snap.get("system", {})
        tools = snap.get("toolchains", {})
        pkgs = snap.get("packages", {})

        installed_tools = [k for k, v in tools.items() if v.get("installed")]

        print(f"OS:          {sys_info.get('os_pretty', 'Linux')} ({sys_info.get('machine', 'x86_64')})")
        print(f"Toolchains:  {len(installed_tools)} detected ({', '.join(installed_tools[:6])}...)")
        print(f"Package Mgrs: {', '.join(pkgs.keys())}")

        total_pkgs = sum(len(v) for v in pkgs.values())
        print(f"Total Items: {total_pkgs} items recorded.")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(snap, f, indent=2)
            print(f"✅ Manifest written to {args.output}")

        if args.export_script:
            script = generate_restore_script(snap)
            with open(args.export_script, "w", encoding="utf-8") as f:
                f.write(script)
            print(f"✅ Restoration script written to {args.export_script}")

        if args.export_docker:
            df = generate_dockerfile(snap)
            with open(args.export_docker, "w", encoding="utf-8") as f:
                f.write(df)
            print(f"✅ Dockerfile written to {args.export_docker}")

        if not (args.output or args.export_script or args.export_docker):
            print("\nRun with --output manifest.json or devreplicant serve for full export.")


if __name__ == "__main__":
    main()
