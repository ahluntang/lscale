# Large-Scale Framework

## Prerequisites

Packages and libraries needed to run the framework

* build-essential
* python-dev
* libxml2-dev
* libxslt1-dev


```
aptitude install $(< apt-requires.txt)
```
Python libraries needed

* argparse
* lxml
* Pexpect (pexpect-u fork has support for python 3)
* netaddr
* jinja2
* markupsafe (optional, speeds up jinja2)

The libraries can be installed using pip-requirements.txt file.

```
pip install -r pip-requirements.txt
```

**NOTE**: LXC or LVM  specific packages can be installed using the configure option in the framework

## Overview

### config.ini
Setting up some basic stuff for the framework.

```
#!sh
[connection]
proxy = http://proxy.atlantis.ugent.be:8080/
```

### Generator usage


```
#!sh
./lscale.py generate [-h] [-f FILE] [-e EXAMPLE]
./lscale.py generate --example cityflow
./lscale.py generate --example cityring
./lscale.py generate --example citybus
./lscale.py generate --example citystar
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
    ./lscale.py emulate [-h] [-f FILE] [-i ID]
    ./lscale.py emulate --file topology.xml -id h001
```

| option          | Optional | Info                                                       |
| --------------- | -------- | ---------------------------------------------------------- |
| -h              | y        | gives a small help message                                 |
| -f or --file    | y        | path to the input file, absolute or relative to execution location (default: topology.xml)    |
| -i or --id      | y        | id of host elements should be created from (default: h001) |


### Configurator
Should run as root for most options.
```
./lscale.py configure [-h]
./lscale.py configure read
./lscale.py configure install --package all
./lscale.py configure lvm --name lxc --device /dev/sda --partition 4 --cache 30
./lscale.py configure create --name base --backingstore lvm --template ubuntu 
./lscale.py configure clone --original base --name c001 -s no
```

### Monitor
