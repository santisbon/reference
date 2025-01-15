# MicroCloud

This is an opinionated guide for setting up a cloud-native homelab.

## Background

### LXD instances

- System containers - Use the kernel on the host. They simulate a full OS and run multiple processes. Fast and lightweight. Implemented through LXC.
- Virtual machines - Have their own kernel and run on top of a hypervisor. Can run a different OS. LXD uses qemu for VMs.

#### Storage Pools

The disk used to store data. Uses a storage driver like Directory, ZFS, Ceph RBD, CephFS, or Ceph Object.

#### Storage Volumes

- Partitions on the disk. Part of a pool.
- Types: 
    - container/virtual-machine, 
    - image, 
    - custom.
Content Types: filesystem, block, iso.

#### Storage Buckets 

- Object storage using the Amazon S3 protocol. Part of a pool too. 
- Assigned access keys that must be used by applications to access the bucket.
- Can be on local storage (e.g. dir, zfs pools) or remote storage ( cephobject pools)

### Application containers
E.g. Docker - Package a single process or application.

### MicroOVN

#### Network devices (NICs)

- Default network bridge.
- Use an existing network interface as a network device.
- Create a managed network and attach it to the instance as a network device.

#### Managed Networks

##### Fully controlled networks

Create network interfaces and provide most functionality e.g. IP management. Types:

- Bridge network (default) - Creates a virtual L2 Ethernet switch that instance NICs can connect to. Good for  running LXD on a single system or a public cloud.
- OVN network - Software-defined networking system for virtual network abstraction. Good for building your own private cloud. Creates a logical network. Needs the OVN tools and an uplink network (an external network or a managed LXD bridge). Can be created and managed inside a project as a non-admin user.

##### External networks

Use network interfaces that already exist. Main purpose is to provide an uplink network through a parent interface.

- Macvlan network - Can assign several IP addresses to the same network interface based on randomly generated MAC addresses.
- SR-IOV network - Hardware standard that allows a single network card port to appear as several virtual network interfaces.
- Physical network - Connects to an existing physical network (network interface or bridge).

## Prerequisites

Overview of what we'll set up.

- 3 Raspberry Pi devices.
    - Fixed IP
    - If you need full disk encryption on cluster members, the `dm-crypt` kernel module
        ```sh
        # Check if the emodule exists
        sudo modinfo dm-crypt
        ```
    - For Ceph you'll need the `rbd` kernel module.
- `snapd` version 2.59.1 or later.
    ```sh
    sudo apt update
    snap version
    # if needed
    sudo apt install snapd
    ```
- LXD version 5.21. Install or update with:
    ```sh
    sudo snap install lxd
    # or
    sudo snap refresh lxd --channel=5.21/stable
    ```

## Installation
1. Initialize LXD
    ```sh
    lxd init
    ```
    