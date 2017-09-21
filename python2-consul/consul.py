import base64
import logging
import requests
logging.basicConfig(level=logging.DEBUG)

class ConsulOperation():

    def __init__(self, consul_url, token, retry):
        self.consul_url = consul_url
        self.token = token
        self.post_data = []
        self.retry = retry

    def set_token(self, token):
        '''
        Allows you to set the consul token which grant you the proper authorization to update
        args:
            token: str (Default to "")
        return:
            None
        '''
        if token:
            self.token = token
        else:
            logging.debug("Token: {} is invalid".format(token))
            exit(1)

    def set_consul_url(self, consul_url):
        '''
        Allows you to set the consul url
        args:
            consul_url: str (Default to http://127.0.0.1)
        return:
            None
        '''
        if consul_url:
            self.consul_url = consul_url
        else:
            logging.debug("Consul URL: {} is invalid".format(consul_url))
            exit(1)

    def set_retry(self, retry):
        '''
        Allows you to set the operation retry
        args:
            retry: int (Default to 2)
        return:
            None
        '''
        if retry and isinstance(retry,int):
            self.retry = retry
        else:
            logging.debug("Retry: {} is invalid".format(retry))
            exit(1)

    def base64_encode(self, value):
        '''
        Base64 encode the value
        args:
            value: str
        return:
            return base64 str value
        '''
        if not isinstance(value, str):
            return base64.b64encode(str(value).encode('utf-8')).decode('ascii')
        else:
            return base64.b64encode(value.encode('utf-8')).decode('ascii')

    def submit_transaction(self, payload):
        '''
        Attempt to submit transaction to consul
        args:
            payload: list
        return:
            None
        '''
        headers = {'X-Consul-Token': self.token}
        result = requests.put(self.consul_url + '/v1/txn', headers=headers, json=payload)
        attempt = 0
        while result.status_code != 200 and attempt <= self.retry:
            result = requests.put(self.consul_url + '/v1/txn', headers=headers, json=payload)
            attempt += 1
        if attempt > 2:
            logging.debug("Transaction failed to submit after attempting {} times.".format(attempt))
            logging.debug(result.raise_for_status())
            exit(1)
        else:
            del self.post_data[:]
            logging.debug("Transaction submmitted successfully")

    def add_to_transaction(self, payload):
        '''
        Attempt to add operations to a queue that will be process if we have 64 operations
        args:
            payload: str (massaged in the payload format from the generate_payload method)
        return:
            None
        '''
        # If number of operations is less than 63, continue to add to list
        # Consul support to 64 operations per transaction
        if len(self.post_data) <= 62:
            self.post_data.append(payload)
        # Submit the transaction to consul once we have 64 operations.
        elif len(self.post_data) == 63:
            try:
                self.submit_transaction(self.post_data)
            except:
                logging.debug("Transaction failed")
                del self.post_data[:]


    def generate_payload(self, key, base64_value):
        '''
        Generate the payload in the format consul requires
        args:
            key: str
            base64_value: str (base64 encoded)
        return:
            json
        '''
        return  {
                    "KV": {
                        "Verb": "set",
                        "Key": key,
                        "Value": base64_value
                    }
                }

    def parse_yaml(self, yaml_input):
        '''
        Parse the json object and add it to the transaction queue.
        args:
            yaml_input: json
        return:
            None
        '''
        for k, v in yaml_input.items():
            if 'path' in v:
                path = v['path']
            else:
                logging.debug("No path")
            if 'values' in v:
                values = v['values']
            else:
                logging.debug("No Values")
            for key, value in values.items():
                encoded_value = self.base64_encode(value)
                full_path = path + '/' + key
                payload = self.generate_payload(full_path, encoded_value)
                self.add_to_transaction(payload)
        if self.post_data:
        # If the number of transaction is less than 64, go ahead and submit it
            self.submit_transaction(self.post_data)
