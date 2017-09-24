import base64
import logging
import requests

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
            logging.error("Token: {} is invalid".format(token))
            exit(1)

    def set_consul_url(self, consul_url):
        '''
        Allows you to set the consul url
        args:
            consul_url: str (Default to http://127.0.0.1:8500)
        return:
            None
        '''
        if consul_url:
            self.consul_url = consul_url
        else:
            logging.error("Consul URL: {} is invalid".format(consul_url))
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
            logging.error("Retry: {} is invalid".format(retry))
            exit(1)

    def base64_encode(self, value):
        '''
        Base64 encode the value
        args:
            value: str
        return:
            return base64 str value
        '''
        return (base64.b64encode(str(value).encode('utf-8')).decode('ascii')
                if not isinstance(value, str)
                else base64.b64encode(value.encode('utf-8')).decode('ascii'))

    def submit_transaction(self, payload):
        '''
        Batch the transaction so it can be submitted to consul
        args:
            payload: list
        return:
            None
        '''
        payload_max_size = 5
        if len(payload) > payload_max_size:
            for i in range(0,len(payload) - 1, payload_max_size):
                logging.debug(payload[i:i+payload_max_size])
                self.execute_transaction(payload[i:i+payload_max_size])
        else:
            logging.debug("Transaction Payload: {}".format(payload))
            self.execute_transaction(payload)

    def execute_transaction(self,transaction):
        '''
        Submit the transactions via the consul api url
        args:
            transaction: batch of 64 operations
        return:
            requests object
        '''
        headers = {'X-Consul-Token': self.token}
        result = None
        attempt = 0
        while True:
            result = requests.put(self.consul_url + '/v1/txn', headers=headers, json=transaction)
            if result.status_code != 200 and attempt <= self.retry:
                attempt += 1
                continue
            else:
                break
        print("Transaction Status Code: {}".format(result.status_code))
        return result

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
        Parse the yaml and create an list of key-value consul formatted payload.
        args:
            yaml_input: json
        return:
            list of consul formatted payload
        '''
        data = []
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
                data.append(payload)
        return data
