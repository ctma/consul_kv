import argparse
import fnmatch
import re
import os
import yaml
import validators

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
    args = parser.parse_args()
    yaml_data = None
    if validators.url(args.url):
        syntax = re.compile(':\d+$')
        if not syntax.search(args.url):
            args.url = args.url + ':8500'
    else:
        print("{} is an invalid url".format(args.url))
        exit(1)
    if args.file is None and args.directory is None:
        print("Exiting... Missing file or directory argument. Use '-h' to view options")
        exit(1)
    elif args.file:
        try:
            yaml_file = open(args.file)
        except IOError:
            print("File {} does not exist or path is invalid".format(args.file))
            exit(1)
        yaml_data = yaml.load(yaml_file)
        consul = ConsulOperation(args.url, args.token, args.retry)
        consul.parse_yaml(yaml_data)
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
                print("Skipping... File {} does not exist or is invalid".format(file))
                continue
            yaml_data = yaml.load(yaml_file)
            print("Processing {}".format(file))
            consul = ConsulOperation(args.url, args.token, args.retry)
            consul.parse_yaml(yaml_data)
            