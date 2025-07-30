# Offline Security Connector
The Offline Security Connector is a package for [Offline Security Client](https://github.com/offlinesec/offlinesec-client) which allows direct connection to SAP systems via RFC protocol (PyRFC library). It collects all needed data for the Offline Security reports.

# Advantages

* You don't need to perform manual actions in SAP anymore
* It supports password authentication, SNC and SSO configurations

## Table of contents

* [Installation](#installation)
* [Quick Start](#quick-start)
* [Use Cases](#use-cases)

## Installation

### Python installation
Install the last version of Python 3.x [from here](https://www.python.org/downloads/)<br />
We support only Python 3.x!

### PyRFC installation
Please refer to [the pyrfc doc](https://github.com/SAP-archive/PyRFC/blob/main/doc/install.rst)
Do not forget to download SAP NWRFC SDK from sap.com. 

### Published version installation (recommended)
```sh
pip3 install offlinesec-connector
```
or
```sh
python3 -m pip install offlinesec-connector
```

Check the installation script output. if you see the following message:
WARNING: The scripts offlinesec_connector and offlinesec_conn_settings are installed in '/Users/<username>/Library/Python/3.8/bin' which is not on PATH.

Then add Python folder to the PATH variable:
```sh
export PATH="$PATH:/Users/<username>/Library/Python/3.8/bin"
```

### Upgrade to the latest published version
```sh
pip3 install --upgrade offlinesec-connector
```
Note: It's recommended to use the last available version each time

### Check what version is installed right now on your laptop
```sh
pip3 show offlinesec-connector
```

## Quick Start
1. Set Connection settings with offlinesec_conn_settings
```sh
offlinesec_conn_settings -f settings.yaml
```
where settings.yaml file - a file with connection settings to SAP. Please refer to [the doc](./docs/offlinesec_conn_settings.md).

2. Run the connector
```sh
offlinesec_connector -c DEV
```
where DEV - a connection name from the settings file
Please refer to [the doc](./docs/offlinesec_connector.md)

```sh
offlinesec_connector -g 'g:productions'
```
where 'g:productions' - a groupname from the settings file

## Use Cases
### Missed SAP Security Notes (Unpatched SAP security vulnerabilities)
```sh
offlinesec_connector -c DEV
```
Please refer to [the doc](./docs/offlinesec_connector.md)

What access we need:
* S_TABU_NAM:ACTVT=03
  S_TABU_NAM:TABLE=CWBNTCUST, PATCHHIST
* S_RFC:ACTVT=16
  S_RFC:RFC_TYPE=FUGR
  S_RFC:RFC_NAME=SDTX, OCS_CRM

To run the following FMs:
* OCS_GET_INSTALLED_COMPS
* RFC_READ_TABLE

and read the following tables:
* CWBNTCUST
* PATCHHIST

## Uninstall
```sh
python3 -m pip uninstall offlinesec-connector
```
