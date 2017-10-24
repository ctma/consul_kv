import sys
import pytest
import unittest
import mock
sys.path.append('.')
from python2_consul.consul import ConsulOperation


@pytest.fixture(scope='session')
def consul_obj():
    '''Return an ConsulOperation object'''
    return ConsulOperation('http://127.0.0.1:8500', 'mytoken', 0)


@pytest.fixture(scope='session')
def json():
    '''Return an yaml'''
    return {
                'apps':
                {
                    'path': 'apps/qa/space',
                    'values':
                    {
                        'hello': True
                    }
                }
            }


@pytest.fixture(scope='session')
def consul_json():
    '''Return an consul insert operation'''
    return {
                'KV':
                {
                    'Key': 'apps/qa/space/hello',
                    'Value': 'VHJ1ZQ==',
                    'Verb': 'set'
                }
            }


def test_base64_encode(consul_obj):
    '''Verify the string is base64 encoded'''
    assert consul_obj._base64_encode('test') == 'dGVzdA=='


def test_generate_payload(consul_obj, consul_json):
    '''Verify generated payload is in the right format'''
    assert (
        consul_obj._generate_payload(
            'apps/qa/space/hello', 'VHJ1ZQ==') == consul_json)


def test_parse_yaml(consul_obj, json, consul_json):
    '''Verify json is converted to consul formatted json'''
    assert consul_obj.parse_yaml(json) == [consul_json]


def test_exist(consul_obj):
    '''Check to see if kv exists in consul'''
    assert (consul_obj._exist(
        [{'Key': 'hello', 'Value': 'world'}], "hello", "world") == True)
    assert (consul_obj._exist(
        [{'Key': 'hello', 'Value': 'world'}], "no", "way") == False)


@mock.patch('python2_consul.consul.requests.get')
def test_get_consul_export(mock_get, consul_obj):
    mock_response = mock.Mock()
    expected_json = [
        {
            "key": "apps/qa/space/delete",
            "flags": 0,
            "value": "aHR0cDovL3FhLmdvb2dsZS5jb20="
        }
    ]
    mock_response.json.return_value = expected_json
    mock_get.return_value = mock_response
    response = consul_obj._get_consul_export()
    url = "http://127.0.0.1:8500/v1/kv/?recurse="
    mock_get.assert_called_once_with(url)
    assert response == expected_json
