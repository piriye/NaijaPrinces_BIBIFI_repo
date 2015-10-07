#!/usr/bin/env/python

import argparse
import json
from netmsg import NetMsg
import os
import sys
import SocketServer

auth_key = ""


class Account:
    card_file = 0
    account_name = ""
    balance = 0

    def __init__(self, card_file, name, balance):
        self.card_file = card_file
        self.account_name = name
        self.balance = balance
        json_out = {}
        json_out["account"] = self.account_name
        json_out["initial_balance"] = self.balance
        print json.dumps(json_out)

    def deposit(self, amount):
        self.balance = self.balance + amount
        json_out = {}
        json_out["account"] = self.account_name
        json_out["deposit"] = self.balance
        print json.dumps(json_out)

    def withdraw(self, amount):
        self.balance = self.balance - amount
        json_out = {}
        json_out["account"] = self.account_name
        json_out["withdraw"] = self.balance
        print json.dumps(json_out)

    def current_balance(self):
        json_out = {}
        json_out["account"] = self.account_name
        json_out["balance"] = self.balance
        print json.dumps(json_out)


class Bank(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    accounts = []

    def parse_request(self, data):
        try:
            # decrypt message
            net_msg = json.load(NetMsg.decryptJson(auth_key))
            request = net_msg["request"]

            if request["action"] is "new":
                new_account = Account(request[""])
        except ValueError:
            sys.stderr.write(255)
            sys.exit(255)

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        self.parse_request(self.data)

        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


def parse_cmd_line():
    parser = argparse.ArgumentParser(description='bank is a server than \
                                    simulates a bank, whose job is to keep \
                                    track of the balance of its customers. ')
    parser.add_argument('-p', '--port', help='Description for foo argument',
                        required=True)
    parser.add_argument('-s', '--auth_file', help='Description for bar \
                        argument', required=True)

    try:
        args = vars(parser.parse_args())
    except SystemExit:
        sys.exit()

    return args


#TODO: Generate auth file once
def generate_auth_file(auth_file):
    global auth_key
    if not os.path.isfile(auth_file):
        f = open(auth_file, "wb")
        json_out = {}
        json_out["Secret_Key"] = NetMsg.generateKey()
        auth_key = json_out["Secret_Key"]
        f.write(json.dumps(json_out))
        f.close()
        print "created"
    else:
        sys.exit(255)


def main():
    args = parse_cmd_line()

    # Create the server, binding to localhost on port 9999
    generate_auth_file(args["auth_file"])
    server = SocketServer.TCPServer(("localhost", int(args['port'])), Bank)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


if __name__ == '__main__':
    main()
