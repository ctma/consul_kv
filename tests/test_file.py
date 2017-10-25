import sys
import pytest
import yaml
sys.path.append('.')
from python2_consul.file import File

@pytest.fixture(scope='session')
def valid_yaml_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp('temp_dir').join('valid.yaml')
    fn.write("key: value")
    return str(fn)

@pytest.fixture(scope='session')
def directory_of_yaml(tmpdir_factory):
    fn = tmpdir_factory.mktemp("test_file",numbered=False)
    file1 = fn.join('valid1.yaml')
    file2 = fn.join('valid2.yaml')
    file1.write("key1: value1")
    file2.write("key2: value2")
    return str(fn)

def test_is_directory(tmpdir):
    temp_dir = tmpdir.mkdir("test_dir")
    assert File().is_directory(temp_dir) == True

def test_is_file(valid_yaml_file):
    assert File().is_file(valid_yaml_file) == True

def test_read_file_content(valid_yaml_file):
    assert File()._read_file_content(valid_yaml_file) == "key: value"

def test_is_yaml_file(valid_yaml_file):
    assert File()._is_yaml_file(valid_yaml_file) == True
    assert File()._is_yaml_file("") == False

def test_parse_yaml(valid_yaml_file):
    assert File().parse_yaml(open(valid_yaml_file).read()) == {'key': 'value'}

def test_glob_yaml_file(tmpdir):
    temp_dir = tmpdir.mkdir("test_dir")
    temp_file = temp_dir.join("file.yaml")
    temp_file.write("")
    assert File()._glob_yaml_file(temp_dir) == list(temp_dir.listdir())

def test_process_file(valid_yaml_file):
    assert File().process_file(valid_yaml_file) == [{'key': 'value'}]

def test_process_directory(directory_of_yaml):
    assert File().process_directory(directory_of_yaml) == [{'key1': 'value1'}, {'key2': 'value2'}]
