#!/usr/bin/env python3

import sys
import subprocess

def main():
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("input_file")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            input_text = f.read().strip()
    except FileNotFoundError:
        print(f"File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # SSH command equivalent to your Bash
    ssh_command = [
        "ssh",
        "akash@40.82.146.82",
        f'python3 /m.py "{input_text}"'
    ]

    try:
        # Run SSH command and capture output
        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout.strip())

    except subprocess.CalledProcessError as e:
        print("Error:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
