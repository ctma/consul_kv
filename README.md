## Synopsis
This tool attempts to load your defined key-value into consul. The key-value are formatted in yaml to allow readability.
## Code Example

	python update_consul.py -f file1.yml	
	python update_consul.py -d path_to_dir_of_yaml_files
	
## Defaulted Value
	Url: http://127.0.0.1
	Port: 8500
	Token:
	Retry: 2
	Directory: current directory

## Motivation

At my previous company, we were loading key-value into consul inefficiently. Some of the issues were:

 	1. We were updating each key value one at a time and were not taking advantage of [consul transactions](https://www.consul.io/api/txn.html)
	2. The format we were defining the kv in was unreadable once there were too many lines.
	3. There was no validation on whether the key value made it into consul

## Installation

 TBA

## YAML Format
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
		

## Tests

 TBA

## Contributors

 TBA

## License
 
The MIT License