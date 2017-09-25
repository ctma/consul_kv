import argparse
import fnmatch
import re
import os
import yaml
import validators
import logging
from consul import ConsulOperation

if __name__ == "__main__":
    parser = argparse.ArgumentParser("python update_consul.py -f blah.yaml")
    parser.add_argument("-f", "--file", help="Read from a particular yaml file")
    parser.add_argument("-d", "--directory", help="Provide the directory to glob for *.yml")
    parser.add_argument("-r", "--retry", help="Provide the number of retry you wish to perform",
                        default=2)
    parser.add_argument("-u", "--url", help="Provide the consul url including the port.",
                        default="http://127.0.0.1:8500")
    parser.add_argument("-t", "--token", help="Provide the consul token", default="")
    parser.add_argument("-l", "--loglevel",
                        help="Provide the log level: INFO, DEBUG, ERROR, WARNING, CRITICAL",
                        default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    if validators.url(args.url):
        syntax = re.compile(':\d+$')
        if not syntax.search(args.url):
            args.url = args.url + ':8500'
    else:
        logging.error("{} is an invalid url".format(args.url))
        exit(1)
    consul = ConsulOperation(args.url, args.token, args.retry)
    yaml_data = None
    payload = None
    if args.file is None and args.directory is None:
        logging.error("Exiting... Missing file or directory argument. Use '-h' to view options")
        exit(1)
    # Pass the file object to a method and let it handle the processing
    # These last two statements is not DRY. Need to rewrite it
    elif args.file:
        try:
            yaml_file = open(args.file)
        except IOError:
            logging.error("File {} does not exist or path is invalid".format(args.file))
            exit(1)
        yaml_data = yaml.load(yaml_file)
        payload = consul.parse_yaml(yaml_data)
        logging.debug("Consul payload: {}".format(payload))
        consul.submit_transaction(payload)
        consul.validate_kv(payload)
    elif args.directory:
        # Credit:
        # https://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
        files = []
        for root, dirnames, filenames in os.walk(args.directory):
            for filename in fnmatch.filter(filenames, '*.yaml'):
                files.append(os.path.join(root, filename))
        # End Credit
        for file in files:
            try:
                yaml_file = open(file)
            except IOError:
                logging.error("Skipping... File {} is not a valid yaml".format(file))
                continue
            yaml_data = yaml.load(yaml_file)
            logging.info("Processing {}".format(file))
            payload = consul.parse_yaml(yaml_data)
            logging.debug("Consul payload: {}".format(payload))
            consul.submit_transaction(payload)
            consul.validate_kv(payload)
