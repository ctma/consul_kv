import base64
import requests

class ConsulOperation():

    def __init__(self,consul_url,token,retry):
        self.consul_url = consul_url
        self.token = token
        self.post_data = []
        self.retry = retry

    '''
    Allows you to set the consul token which grant you the proper authorization to update
    args:
        token: str (Default to "")
    return:
        None
    '''
    def set_token(self,token):
        if token:
            self.token = token
        else:
            print("Token: {} is invalid".format(token))
            exit(1)

    '''
    Allows you to set the consul url
    args:
        consul_url: str (Default to http://127.0.0.1)
    return:
        None
    '''
    def set_consul_url(self,consul_url):
        if consul_url:
            self.consul_url = consul_url
        else:
            print("Consul URL: {} is invalid".format(consul_url))
            exit(1)

    '''
    Allows you to set the operation retry
    args:
        retry: int (Default to 2)
    return:
        None
    '''
    def set_retry(self,retry):
        if retry and isinstance(retry,int):
            self.retry = retry
        else:
            print("Retry: {} is invalid".format(retry))
            exit(1)

    '''
    Base64 encode the value
    args:
        value: str
    return:
        return base64 str value
    '''
    def base64_encode(self, value):
        if not isinstance(value, str):
            return base64.b64encode(str(value))
        else:
            return base64.b64encode(value)

    '''
    Attempt to submit transaction to consul
    args:
        payload: list
    return:
        None
    '''
    def submit_transaction(self,payload):
        headers = {'X-Consul-Token': self.token}
        result = requests.put(self.consul_url + '/v1/txn', headers=headers, json=payload)
        attempt = 0
        while result.status_code != 200 and attempt <= self.retry:
            result = requests.put(self.consul_url + '/v1/txn', headers=headers, json=payload)
            attempt += 1
        if attempt > 2:
            print("Transaction failed to submit after attempting {} times.".format(attempt))
            print(result.raise_for_status())
            exit(1)
        else:
            del self.post_data[:]
            print("Transaction submmitted successfully")

    '''
    Attempt to add operations to a queue that will be process if we have 64 operations
    args:
        payload: str (massaged in the payload format from the generate_payload method)
    return:
        None
    '''
    def add_to_transaction(self,payload):
        # If number of operations is less than 63, continue to add to list
        # Consul support to 64 operations per transaction
        if len(self.post_data) <= 62:
            self.post_data.append(payload)
        # Submit the transaction to consul once we have 64 operations.
        elif len(self.post_data) == 63:
            try:
               self.submit_transaction(self.post_data)
            except:
               print("Transaction failed")
               del self.post_data[:]

    '''
    Generate the payload in the format consul requires
    args:
        key: str
        base64_value: str (base64 encoded)
    return:
        json
    '''
    def generate_payload(self,key,base64_value):
        return  {
                    "KV": {
                        "Verb": "set",
                        "Key": key,
                        "Value": base64_value
                    }
                }

    '''
    Parse the json object and add it to the transaction queue.
    args:
        yaml_input: json
    return:
        None
    '''
    def parse_yaml(self, yaml_input):
        for k,v in yaml_input.iteritems():
            if 'path' in v:
                path = v['path']
            else:
                print("No path")
            if 'values' in v:
                values = v['values']
            else:
                print("No Values")
            for key,value in values.iteritems():
                encoded_value = self.base64_encode(value)
                full_path = path + '/' + key
                payload = self.generate_payload(full_path, encoded_value)
                self.add_to_transaction(payload)
        if len(self.post_data) != 0:
        # If the number of transaction is less than 64, go ahead and submit it
            self.submit_transaction(self.post_data)