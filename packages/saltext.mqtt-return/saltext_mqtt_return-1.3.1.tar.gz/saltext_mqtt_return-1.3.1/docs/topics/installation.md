# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Mqtt-return extension:
  pip.installed:
    - name: saltext-mqtt-return
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-mqtt-return
```
:::

:::{tab} Regular installation
```bash
pip install saltext-mqtt-return
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
