#!/usr/bin/env python
import argparse
import re
import validators
import logging
from file import File
from consul import ConsulOperation


def get_Arguments():
    parser = argparse.ArgumentParser("python update_consul.py -f blah.yaml")
    parser.add_argument("-f", "--file",
                        help="Relative path to the file or directory",
                        required=True)
    parser.add_argument("-r", "--retry",
                        help="Number of retry you wish to perform",
                        default=2)
    parser.add_argument("-u", "--url",
                        help="Consul url including the port.",
                        default="http://127.0.0.1:8500")
    parser.add_argument("-t", "--token",
                        help="Provide the consul token",
                        default="")
    parser.add_argument("-p", "--port",
                        help="Provide the consul port",
                        default=8500)
    parser.add_argument("-l", "--loglevel",
                        help="INFO, DEBUG, ERROR, WARNING, CRITICAL",
                        default="INFO")
    args = parser.parse_args()
    return parser.parse_args()

def check_consul_url(url):
    if validators.url(args.url):
        syntax = re.compile(':\d+$')
        if not syntax.search(args.url):
            args.url = args.url + ':' + str(args.port)
    else:
        print("{} is an invalid url".format(args.url))
        exit(1)

if __name__ == "__main__":
    args = get_Arguments()
    logging.basicConfig(level=args.loglevel.upper())
    check_consul_url(args)
    consul = ConsulOperation(args.url, args.token, args.retry)
    payload = None
    if args.file is None:
        print("""Exiting... Missing file or directory argument.
              Use '-h' to view options""")
        exit(1)
    elif args.file:
        data = File().process_args_file(args.file)
        payload = consul.parse_yaml(data)
        if payload:
            consul.submit_transaction(payload)
            consul.validate_kv(payload)
