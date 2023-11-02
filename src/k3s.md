## Prerequisites

1. Set up your Raspberry Pi devices with `cloud-init` as defined in the [Raspberry Pi](/reference/rpi/) section.
2. Assign static IPs to all the nodes. 
3. `sudo nano /etc/hosts` on each node and add the IP and hostnames of the other nodes so they can resolve during the join process.

## Installation

* [Ubuntu/Debian requirements](https://docs.k3s.io/advanced#ubuntu--debian).
* [Installation](https://docs.k3s.io/installation).