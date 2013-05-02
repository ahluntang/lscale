# Large-Scale Framework

## Prerequisites

Python libraries needed

* argparse
* lxml
* Pexpect (pexpect-u fork has supprt for python 3)
* netaddr
* jinja2
* markupsafe (optional, speeds up jinja2)

```
pip install argparse lxml pexpect-u netaddr jinja2 markupsafe
```

**Note**: to install some of the libraries (such as lxml) you will need gcc compiler and Python headers, in debian, you can get the required packages from `build-essential` and `python-dev`.
lxml itself also requires `libxml2-dev` and `libxslt1-dev` 

```
apt-get install build-essential python-dev libxml2-dev libxslt1-dev
```

## Overview

### Generator usage


```
#!sh
    ./lscale.py {generate|emulate} [-h] [-f FILE] [-e EXAMPLE]
    ./lscale.py generate -e cityflow
    ./lscale.py generate -e cityring
    ./lscale.py generate -e citybus
    ./lscale.py generate -e citystar
```

| option          | Optional | Info                                                     |
| --------------- | -------- | -------------------------------------------------------- |
| -h              | y        | gives a small help message                               |
| -f or --file    | y        | location and name of output file (default: topology.xml) |
| -e or --example | y        | load example topology (default: cityflow)                |

**Examples** are loaded from the examples package, see these examples for detailed information on how to create topologies.


### Emulator usage

Should run as root.

```
#!sh
    ./lscale.py {generate|emulate} [-h] [-f FILE] [-i ID]
    ./lscale.py emulate -f topology.xml -i h001
```

| option          | Optional | Info                                                       |
| --------------- | -------- | ---------------------------------------------------------- |
| -h              | y        | gives a small help message                                 |
| -f or --file    | y        | path to the input file, absolute or relative to execution location (default: topology.xml)    |
| -i or --id      | y        | id of host elements should be created from (default: h001) |
