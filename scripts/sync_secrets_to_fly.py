#!/usr/bin/env python3
"""
Sync .env variables to Fly.io secrets.
Reads .env, optionally overrides for production, and runs `fly secrets import`.

Usage:
    python scripts/sync_secrets_to_fly.py [--dry-run]
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def parse_env(content: str) -> dict[str, str]:
    """Parse .env content into key=value dict. Handles quoted values."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Match KEY=VALUE (value may be quoted)
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("\\'", "'")
        if value:
            result[key] = value
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync .env to Fly.io secrets")
    parser.add_argument("--dry-run", action="store_true", help="Print vars without uploading")
    parser.add_argument("--app", default="sally-love-voice-agent", help="Fly app name")
    args = parser.parse_args()

    if not ENV_FILE.exists():
        print(f"Error: {ENV_FILE} not found", file=sys.stderr)
        sys.exit(1)

    content = ENV_FILE.read_text()
    vars = parse_env(content)

    # Production overrides
    vars["ENVIRONMENT"] = "production"
    vars["LOG_FILE"] = "/dev/stdout"

    lines = [f"{k}={v}" for k, v in sorted(vars.items())]
    secrets_content = "\n".join(lines)

    if args.dry_run:
        print("Would set the following secrets:")
        for line in lines:
            # Mask sensitive values for display
            if "=" in line:
                k, v = line.split("=", 1)
                display = v[:4] + "***" if len(v) > 8 and k in (
                    "VAPI_API_KEY", "TWILIO_AUTH_TOKEN", "BOLDTRAIL_API_KEY",
                    "SMTP_PASSWORD", "BOLDTRAIL_ZAPIER_KEY"
                ) else v
                print(f"  {k}={display}")
        return

    result = subprocess.run(
        ["fly", "secrets", "import", "--app", args.app],
        input=secrets_content.encode(),
        capture_output=True,
    )

    if result.returncode != 0:
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(result.returncode)

    print(result.stdout.decode())
    print(f"✅ Synced {len(vars)} secrets to {args.app}")


if __name__ == "__main__":
    main()
