import os
import fnmatch
import logging
import yaml

class File:
    '''

    '''
    def _read_file_content(self, file):
        '''Attempts to open the file and return the content

        Args:
            file (str): The path to the file
        Returns:
            str object of the file's content
            None object if the file is invalid
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
        '''Validate if the file contains valid yaml

        Args:
            file_content (str): File content
        Returns:
            bool: True if valid, False otherwise
        '''
        yaml_file = None
        try:
            yaml_file = yaml.load(file_content)
        except yaml.scanner.ScannerError:
            logging.error("File {} contains invalid yaml".format(file_content))
        return True if yaml_file else False

    def _glob_yaml_file(self, user_input):
        '''If user's input is a directory, scan for all the yaml file

        Args:
            user_input (str): Path to a directory or file
        Returns:
            List of str object of file path
            None if nothing is found
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
        '''Check to see if the user's input is a file

        Args:
            user_input (str): Path to a file or directory
        Returns:
            bool: True if it is, False otherwise
        '''
        return os.path.isdir(user_input)

    def is_file(self, user_input):
        '''Check to see if the user's input is a directory

        Args:
            user_input (str): Path to a file or directory
        Returns:
            bool: True if it is, False otherwise
        '''
        return os.path.isfile(user_input)

    def parse_yaml(self, file_content):
        '''Parse the yaml file and return a json

        Args:
            file_content (str): File's content
        Returns:
            json object if valid
            None if invalid
        '''
        return yaml.load(file_content) if self._is_yaml_file(file_content) else None

    def process_file(self, file):
        '''Process the file content and return a list

        Args:
            file (str): Path to a file
        Returns:
            List of json objects
            None if invalid
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
        '''Process each file and load it into a list of dict

        Args:
            directory (str): Path to a directory
        Returns:
            List of json objects
            None if invalid
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
