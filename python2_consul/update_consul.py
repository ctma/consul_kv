#!/usr/bin/env python
import argparse
import re
import validators
import logging
from file import File
from consul import ConsulOperation

if __name__ == "__main__":
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
    logging.basicConfig(level=args.loglevel.upper())

    if validators.url(args.url):
        syntax = re.compile(':\d+$')
        if not syntax.search(args.url):
            args.url = args.url + ':' + str(args.port)
    else:
        print("{} is an invalid url".format(args.url))
        exit(1)
    consul = ConsulOperation(args.url, args.token, args.retry)
    payload = None
    if args.file is None:
        print("""Exiting... Missing file or directory argument.
              Use '-h' to view options""")
        exit(1)
    elif args.file:
        if File().is_directory(args.file):
            data_set = File().process_directory(args.file)
            payload = []
            for data in data_set:
                logging.debug("Extracting kv: {}".format(data))
                payload += consul.parse_yaml(data)
        elif File().is_file(args.file):
            data = File().process_file(args.file)
            payload = consul.parse_yaml(data[0])
        if payload:
            consul.submit_transaction(payload)
            consul.validate_kv(payload)
