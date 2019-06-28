# exec-plug-command

Webservice that downloads and executes code from a S3 bucket!

## usage

```
$ # aws configure...
$ pip install -r requirements.txt
$ python main.py
$ ./bump-plug.sh foo
$ curl http://localhost:5000/exec/foo/main
```

## Test.sh

Test.sh tries to provoke <plug> inconsistency by continuously curling the service while a background process is deploying new versions.

```
$ ./test.sh
```

> The <plug> used by the test script tries to verify their integrity by checking .VERSION for a bunch of modules, you can try to mess up the integrity of the test plug with something like `sed -i .bak 's/VERSION=.*/VERSION=666/' cache/foo/code/module1.py` if you want!
