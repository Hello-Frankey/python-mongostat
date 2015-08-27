#!/usr/bin/env python
import argparse

from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

# Version number
PYTHON_MONGOSTAT_VERSION = "0.0.1"

# Not authorized error
MONGO2_NOT_AUTH = "unauthorized"
MONGO3_NOT_AUTH = "not authorized"

# Authentication failure message
MONGO3_AUTH_FAILUR = "Authentication failed"

class MongoInstance():
    'Class for mongodb instance'

    def __init__(self, host, port, username, password):
        'Initialize the mongodb instance information and create connection to it.'

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.stats_info = {}

        # Create connection to mongodb server
        try:
            self.connection = MongoClient(self.host, self.port)
        except ConnectionFailure:
            print "Connection error: create connection to mongodb instance failed."
            exit(1)

        # Get the mongodb version
        try:
            server_info = self.connection.server_info()
            self.version = server_info['version']
        except ServerSelectionTimeoutError:
            print "Timeout error: get server information of mongodb instance timeout."

        return


    def try_stats_command(self):
        'Try to execute the serverStatus command to see if authentication required.'
        
        # Execute the serverStatus command at first and handle possible exceptions
        errmsg = server_status = {}
        admin = self.connection.admin
        try:
            server_status = admin.command({"serverStatus":1})
        except OperationFailure, op_failure:
            errmsg = op_failure.details
        except:
            print "Execution error: get server status of mongodb instance failed."
            exit(1)

        # Check to see if the mongodb server enables authentication
        if errmsg != {}:
            if errmsg['errmsg'].find(MONGO2_NOT_AUTH) == -1 and errmsg['errmsg'].find(MONGO3_NOT_AUTH) == -1:
                print "Execution error: %s." % errmsg['errmsg']
                exit(1)
            else:
                # Authenticate with the given username and password
                try:
                    admin.authenticate(self.username, self.password)
                except OperationFailure, op_failure:
                    print "Execution error: authenticate to mongodb instance failed."
                    exit(1)
                # Try to execute the serverStatus command again
                try:
                    server_status = admin.command({"serverStatus":1})
                except OperationFailure, op_failure:
                    print "Execution error: %s." % op_failure.details['errmsg']
                    exit(1)
        
        # Set the mongodb storage engine type if mongodb version is 3.0 or later
        if self.version >= "3.0":
            self.storage_engine = server_status['storageEngine']['name']

        return


def mongostat_arg_check(args):
    'Check the given arguments to make sure they are valid.'

    # Make sure the rowcount not negative integer
    if args.rowcount and args.rowcount < 0:
        return False, "number of stats line to print can not be negative."

    # Make sure both username and password should be given, or neither
    if args.username and not args.password:
        return False, "only username given, without password."
    if not args.username and args.password:
        return False, "only password given, without username."

    # Make sure the hostname is valid
    if args.host:
        hostinfo = args.host.split(':')
        if len(hostinfo) > 2:
            return False, "invalid mongodb host, only HOSTNAME of HOSTNAME:PORT acceptable."
        if len(hostinfo) == 2:
            try:
                port = int(hostinfo[1])
                if args.port and args.port != port:
                    return False, "ports given by port option and host option not match."
            except ValueError:
                return False, "invalid mongodb host, the port part not integer."

    return True, None

def mongostat_start(host, port, username, password, rowcount, noheaders, json):
    'Start monitor the mongodb server status and output stats one time per second.'

    # Create mongodb instance and make sure we can execute the serverStatus command correctly
    mongo_instance = MongoInstance(host, port, username, password)
    mongo_instance.try_stats_command()
    # print mongo_instance.host, mongo_instance.port, mongo_instance.version, mongo_instance.storage_engine

if __name__ == '__main__':
    # Default configurations
    hostname, username, password    = 'localhost', '', ''
    port, rowcount                  = 27017, 0
    noheaders, json                 = False, False 

    # Define a argument parser for all possible options
    parser = argparse.ArgumentParser(description="Monitor basic MongoDB server statistics.")
    parser.add_argument("--version", help="print the tool version and exit", action="store_true")
    parser.add_argument("--host", help="mongodb host to connect to")
    parser.add_argument("--port", help="server port (can also use --host HOSTNAME:PORT)", type=int)
    parser.add_argument("-u", "--username", help="username for authentication")
    parser.add_argument("-p", "--password", help="password for authentication")
    parser.add_argument("--noheaders", help="don't output column names", action="store_true")
    parser.add_argument("-n", "--rowcount", help="number of stats lines to print (0 for indefinite)", type=int)
    parser.add_argument("--json", help="output as JSON rather than a formatted table", action="store_true")

    # Parse all the given options and make sure they are valid
    arguments = parser.parse_args()
    if arguments.version:
        print "Python mongostat version: %s" % PYTHON_MONGOSTAT_VERSION
        exit(0)
    ok, errmsg = mongostat_arg_check(arguments)
    if ok == False:
        print "Argument error: %s" % errmsg
        exit(1)
    
    # Get the given arguments
    if arguments.host:
        hostinfo = arguments.host.split(':')
        hostname = hostinfo[0]
        if len(hostinfo) == 2:
            port = int(hostinfo[1])
    if arguments.port:
        port = arguments.port
    if arguments.username:
        # We make sure username and password must both given or neither in mongostat_arg_check
        username = arguments.username
        password = arguments.password
    if arguments.rowcount:
        rowcount = arguments.rowcount
    if arguments.noheaders:
        noheaders = True
    if arguments.json:
        json = True

    # Start the mongostat
    mongostat_start(hostname, port, username, password, rowcount, noheaders, json)
