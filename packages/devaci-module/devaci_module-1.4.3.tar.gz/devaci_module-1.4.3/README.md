# DEVACI Module
DEVACI module for python 3.x

## Requirements
Before of install devaci module, you must install the acicobra and acimodel package.
They can be downloaded from the APIC controller https://APIC_IP/cobra/_downloads/

```shell
$ pip install acicobra*
$ pip install acimodel*
```

## Installation
```shell
$ pip install devaci_module
```

## Requirement


## Quickstart
Import the `devaci_module` library to use the package
```python
from devaci_module import DeployClass
....
```

Below an example.
```python

import os
from pathlib import Path
from devaci_module import DeployClass
from dotenv import load_dotenv


ROOT = Path(__file__).parent

load_dotenv(ROOT / ".env")

SETTINGS = {
    "username": os.getenv("USER"),
    "password": os.getenv("PASS"),
    "ip": os.getenv("IP"),
    "testing": False,
    "logging": True,
    "render_to_xml": True,
    "log": ROOT / "logging.json",
}


if __name__ == "__main__":
    aci = DeployClass(**SETTINGS)
    aci.xlsx = [
        ROOT / "configurations/config1.xlsx",
    ]
    aci.template = [
        ROOT / "templates/create_tenants.j2",
        ROOT / "templates/create_tenant1.j2",
        ROOT / "templates/create_tenant2.j2",
    ]
    aci.deploy()
    aci.show_output()
```