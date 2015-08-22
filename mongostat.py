#!/usr/bin/env python

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monitor basic MongoDB server statistics.")
    parser.add_argument("--version", help="print the tool version and exit", action="store_true")
    parser.add_argument("--host", help="mongodb host to connect to")
    parser.add_argument("--port", help="server port (can also use --host HOSTNAME:PORT)", type=int)
    parser.add_argument("-u", "--username", help="username for authentication")
    parser.add_argument("-p", "--password", help="password for authentication")
    parser.add_argument("--noheaders", help="don't output column names", action="store_true")
    parser.add_argument("-n", "--rowcount", help="number of stats lines to print (0 for indefinite)", type=int)
    parser.add_argument("--json", help="output as JSON rather than a formatted table", action="store_true")

    arguments = parser.parse_args()
