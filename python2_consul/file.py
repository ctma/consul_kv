import os
import fnmatch
import logging
import yaml

class File:

    def _read_file_content(self, file):
        '''
        Attempts to open the file and return the content
        args:
            file: str
        return
            str
        '''
        logging.info("Attempting to read content from file: {}".format(file))
        file_handler = None
        try:
            file_handler = open(file)
        except FileNotFoundError:
            logging.error("File {} does not exist")
            exit(1)
        content = file_handler.read()
        file_handler.close()
        return content

    def _is_yaml_file(self, file_content):
        '''
        Check to see if the content of the file is valid yaml
        args:
            file_content: str
        return
            boolean
        '''
        yaml_file = None
        try:
            yaml_file = yaml.load(file_content)
        except yaml.scanner.ScannerError:
            logging.error("File {} contains invalid yaml".format(file_content))
        return True if yaml_file else False

    def _glob_yaml_file(self, user_input):
        '''
        If file_handler is a directory, scan for all *yaml and return a list of file
        args:
            user_input: str
        return
            list of str
        '''

        # Credit:
        # https://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
        files = []
        for root, dirnames, filenames in os.walk(user_input):
            for filename in fnmatch.filter(filenames, '*.yaml'):
                files.append(os.path.join(root, filename))
        # End Credit
        return files

    def is_directory(self, user_input):
        '''
        Check to see if the input is a file
        args:
            user_input: str
        return
            boolean
        '''
        return os.path.isdir(user_input)

    def is_file(self, user_input):
        '''
        Check to see if the input is a directory
        args:
            user_input: str
        return
            boolean
        '''
        return os.path.isfile(user_input)

    def parse_yaml(self, file_content):
        '''
        Parse the yaml file and return a json if valid otherwise None
        args:
            file_content: str
        return:
            json
        '''
        return yaml.load(file_content) if self._is_yaml_file(file_content) else None

    def process_file(self, file):
        '''
        Process the file content and return a list
        args:
            file: dict
        return
            list of dict
        '''
        yaml_data = []
        logging.debug("Processing content from file: {}".format(file))
        file_content = self._read_file_content(file)
        if file_content:
            logging.debug("Parsing yaml content from file {}".format(file))
            data = self.parse_yaml(file_content)
            if data:
                logging.debug("YAML in file {} is: \n{}".format(file, data))
                yaml_data.append(data)
            else:
                logging.error("File {} does not contain valid yaml".format(file))
        return yaml_data

    def process_directory(self, directory):
        '''
        Process each file and load it into a list of dict
        args:
            directory: str
        return
            list of json
        '''
        yaml_data = []
        files = self._glob_yaml_file(directory)
        if files:
            for file in files:
                yaml_data += self.process_file(file)
            #logging.debug("Valid yaml data: {}".format(yaml_data))
        else:
            logging.info("Directory {} contains no file with extension .yaml".format(directory))
        return yaml_data
