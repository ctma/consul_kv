import base64
import logging
import requests


class ConsulOperation:
    '''

    '''
    def __init__(self, consul_url, token, retry):
        self.consul_url = consul_url
        self.token = token
        self.retry = retry

    def _base64_encode(self, value):
        '''Base64 encode the value

        Args:
            value (str): Value you want to encode
        Returns:
            str object of the base64 value
        '''
        return (base64.b64encode(str(value).encode('utf-8')).decode('ascii')
                if not isinstance(value, str)
                else base64.b64encode(value.encode('utf-8')).decode('ascii'))

    def _execute_transaction(self, transaction):
        '''Submit the transactions via the consul api url

        Args:
            transaction (list): List of json objects
        Returns:
            int object of http response code
        '''
        headers = {'X-Consul-Token': self.token}
        result = None
        attempt = 0
        while True:
            result = requests.put(self.consul_url + '/v1/txn',
                                  headers=headers, json=transaction)
            if result.status_code != 200 and attempt <= self.retry:
                attempt += 1
                continue
            else:
                break
        logging.info("Transaction Status Code: {}".format(result.status_code))
        return result

    def _generate_payload(self, key, base64_value):
        '''Generate the payload in the format consul requires

        Args:
            key (str): Consul path to where the value should be stored
            base64_value (str): Base64 encoded value
        Returns:
            json object of consul formatted payload
        '''
        return {
                    "KV": {
                        "Verb": "set",
                        "Key": key,
                        "Value": base64_value
                    }
               }

    def _exist(self, existing_kv, key, value):
        '''Check if the key-value matches the response from consul

        Args:
            existing_kv: list of json objects
                [
                    {
                        "key": "hello",
                        "flags": 0,
                        "value": "d29ybGQ="
                    }
                ]
            key (str): Consul path to the value
            value (str): Base64 value
        return:
            boolean
        '''
        found = False
        for i in existing_kv:
            if i['Key'] == key and i['Value'] == value:
                found = True
        return found

    def _get_consul_export(self):
        '''Export all the key-value from consul

        Returns:
            list of json objects
                [
                    {
                        "key": "hello",
                        "flags": 0,
                        "value": "d29ybGQ="
                    }
                ]
        '''
        result = requests.get(self.consul_url + '/v1/kv/?recurse=')
        try:
            result.raise_for_status()
            return result.json()
        except requests.exceptions.HTTPError:
            logging.error("Unable to obtain any key-value from the server")
            exit(1)

    def parse_yaml(self, yaml_input):
        '''Parse the yaml and create an list of key-value.

        Args:
            yaml_input (json): File content of a yaml file
        Returns:
            list of json object
        '''
        data = []
        for k, v in yaml_input.items():
            if 'path' in v:
                path = v['path']
            if 'values' in v:
                values = v['values']
            if isinstance(values, dict):
                for key, value in values.items():
                    encoded_value = self._base64_encode(value)
                    full_path = path + '/' + key
                    payload = self._generate_payload(full_path, encoded_value)
                    data.append(payload)
            else:
                encoded_value = self._base64_encode(values)
                payload = self._generate_payload(path, encoded_value)
                data.append(payload)
        return data

    def validate_kv(self, payload):
        '''Validate if the key-value exist in consul

        Args:
            payload (list): List of consul transaction
        Returns:
            bool: True if key-value exist in consul, otherwise False
        '''
        logging.info("Attempting to validate if key-value made it into consul")
        not_exist = []
        existing_kv = self._get_consul_export()
        for KV in payload:
            key = KV['KV']['Key']
            value = KV['KV']['Value']
            if not self._exist(existing_kv, key, value):
                not_exist.append(dict(key=value))
        if len(not_exist) != 0:
            logging.info("{} was not found on consul".format(not_exist))
        return (True if len(not_exist) == 0 else False)

    def submit_transaction(self, payload):
        '''Batch the transaction so it can be submitted to consul

        Args:
            payload (list): List of consul transaction to submit to consul
        '''
        payload_max_size = 64
        logging.debug("Payload size is currently {}".format(len(payload)))
        if len(payload) > payload_max_size:
            for i in range(0, len(payload) - 1, payload_max_size):
                logging.debug(payload[i:i+payload_max_size])
                self._execute_transaction(payload[i:i+payload_max_size])
        else:
            logging.debug("Key-value Payload: {}".format(payload))
            self._execute_transaction(payload)
