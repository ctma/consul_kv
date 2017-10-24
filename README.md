![Build Status](https://circleci.com/gh/ctma/consul_kv/tree/master.svg?style=shield&circle-token=3cc31d908a9fddd8e7ccb4a0aee6919eb1bb9fd4)
## Synopsis
This tool attempts to load your defined key-value into consul. The key-value are formatted in yaml to allow readability.
## Code Example
	#If you want to load one file
	python update_consul.py -f file1.yml
	
	#If you want to load multiple *.yaml files in a directory	
	python update_consul.py -d path_to_dir_of_yaml_files
	
## Defaulted Value
	Url: http://127.0.0.1
	Port: 8500
	Token:
	Retry: 2
	Directory: current directory

## Motivation

At my previous company, we were loading key-value into consul inefficiently. Some of the issues were:

 	1. We were updating each key value one at a time and were not taking advantage of consul transaction.
	2. The format we were defining the kv in was unreadable once there were too many lines.
	3. There was no validation on whether the key value made it into consul

## Installation

 	python setup.py install

## YAML
See [example1.yaml](examples/example1.yaml)

	var1:
		path: app/env1
		values:
			api_key: xxx-xxx-xxx-xxx
			google_auth: yyy-yyy-yyy
	var2:
		path: app/env2
		values:
			db_url: easy123
			db_user: hello_db
	var3:
		path: default/httpd
		values: |
			a: a1
			b: b2
			c: c1
		

## Tests

 	python setup.py test
 	
## Requirements
	python3
	consul 0.8.5 & up

## Contributors

 TBA

## License
 
The MIT License
