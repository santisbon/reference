# Cloud-native Homelab

A homelab is a playground for learning, experimenting, and running workloads in a private environment at home. You can use it to deploy web servers, backup solutions, media servers, home automation, development/test environments, and more.

Building a homelab in a cloud-native way will teach you the concepts and building blocks used by all public cloud providers like AWS or GCP so that when you learn and use their specific implementations everything will make sense.

The goal for this guide is to make our homelab:

- **Cost-effective**: We'll use a cluster of single-board computers (SBCs) for low cost and low power consumption.
- **Cloud-native** with these features:
    - Scalable, highly available, virtualized workloads. 
    - Block, file, and object storage. 
    - Software-defined networking.
- **Open source**.

## Background and Terminology

Quick overview of the technologies we'll work with. Based on  and summarized from materials compiled from different places in the Canonical documentation sites for Ubuntu, LXD, Ceph, and OVN.

### Compute

LXD is a solution for managing instances which can be system containers or virtual machines.

- **System containers** use the kernel on the host. They simulate a full OS and run multiple processes. Fast and lightweight. Implemented through LXC. Not to be confused with *application* containers e.g. Docker - those package a single process or application.
- **Virtual machines** have their own kernel and run on top of a hypervisor so they can run an OS different from the host. They are slower and more resource-intensive. LXD uses qemu for VMs.

### Storage

#### Storage Pools

Think of them as the disks used to store data. They use one of these storage drivers:

- Btrfs - `btrfs`
- CephFS - `cephfs`
- Ceph Object - `cephobject`
- Ceph RBD - `ceph`
- Dell PowerFlex - `powerflex`
- Directory - `dir`
- LVM - `lvm`
- ZFS - `zfs`. Needs a GA variant of Ubuntu and **not** the Hardware Enablement (HWE) stack.

  

!!! attention
    Ubuntu **Desktop** installations default to tracking the **HWE** stack.  
    Ubuntu **Server** installations default to the **GA** kernel with the enablement kernel as optional.

STORAGE LOCATION

| LOCATION                 | DIRECTORY  | BTRFS  | LVM | ZFS  | CEPH RBD | CEPHFS  | 
|--------------------------|:----------:|:------:|:---:|:----:|:---------:|:------:|
| Shared with the host     |     ✅     |   ✅   |  ➖  |  ✅  |     ➖    |    ➖   |
| Dedicated disk/partition |     ➖     |   ✅   |  ✅  |  ✅  |     ➖    |    ➖   |
| Loop disk                |     ➖     |   ✅   |  ✅  |  ✅  |     ➖    |    ➖   |
| Remote storage           |     ➖     |   ➖   |  ➖  |  ➖  |     ✅    |    ✅   |

FEATURE COMPARISON

| FEATURE                                   | DIRECTORY  | BTRFS  |  LVM   |  ZFS   | CEPH RBD | CEPHFS  | CEPH OBJECT | DELL POWERFLEX |
|-------------------------------------------|:----------:|:------:|:------:|:------:|:--------:|:-------:|:-----------:|:--------------:|
| Optimized image storage                   |     ❌     |   ✅   |   ✅    |  ✅    |     ✅    |    ➖   |      ➖     |       ❌       |
| Optimized instance creation               |     ❌     |   ✅   |   ✅    |  ✅    |     ✅    |    ➖   |      ➖     |       ❌       |
| Optimized snapshot creation               |     ❌     |   ✅   |   ✅    |  ✅    |     ✅    |    ✅   |      ➖     |       ✅       |
| Optimized image transfer                  |     ❌     |   ✅   |   ❌    |  ✅    |     ✅    |    ➖   |      ➖     |       ❌       |
| Optimized backup (import/export)          |     ❌     |   ✅   |   ❌    |  ✅    |     ❌    |    ➖   |      ➖     |       ❌       |
| Optimized volume transfer                 |     ❌     |   ✅   |   ❌    |  ✅    |     ✅[1] |    ➖   |      ➖     |       ❌       |
| Optimized volume refresh                  |     ❌     |   ✅   |   ✅[2] |  ✅    |     ✅[3] |    ➖   |      ➖     |       ❌       |
| Copy on write                             |     ❌     |   ✅   |   ✅    |  ✅    |     ✅    |    ✅   |      ➖     |       ✅       |
| Block based                               |     ❌     |   ❌   |   ✅    |  ❌    |     ✅    |    ❌   |      ➖     |       ✅       |
| Instant cloning                           |     ❌     |   ✅   |   ✅    |  ✅    |     ✅    |    ✅   |      ➖     |       ❌       |
| Storage driver usable inside a container  |     ✅     |   ✅   |   ❌    |  ✅[4] |     ❌    |    ➖   |      ➖     |       ❌       |
| Restore from older snapshots (not latest) |     ✅     |   ✅   |   ✅    |  ❌    |     ✅    |    ✅   |      ➖     |       ✅       |
| Storage quotas                            |     ✅[5]  |   ✅   |   ✅    |  ✅    |     ✅    |    ✅   |      ✅     |       ✅       |
| Available on lxd init                     |     ✅     |   ✅   |   ✅    |  ✅    |     ✅    |    ❌   |      ❌     |       ❌       |
| Object storage                            |     ✅     |   ✅   |   ✅    |  ✅    |     ❌    |    ❌   |      ✅     |       ❌       |

[1] Volumes of type `block` will fall back to non-optimized transfer when migrating to an older LXD server that doesn’t yet support the `RBD_AND_RSYNC` migration type.
[2] Requires `lvm.use_thinpool` to be enabled. Only when refreshing local volumes.
[3] Only for volumes of type `block`.
[4] Requires` zfs.delegate` to be enabled.
[5] The `dir` driver supports storage quotas when running on either ext4 or XFS with project quotas enabled at the file system level.

!!! hint
    The `ceph` and `cephfs` drivers store the data in an independent Ceph storage cluster that must be set up separately from LXD. This is where MicroCeph will come in.


#### Storage Volumes

They're like partitions on the disk for specific purposes. Part of a storage pool. 

Types:  

- `container`/`virtual-machine` - LXD creates these automatically when you launch an instance. Used as the root disk for the instance. Destroyed when the instance is deleted.
- `image` - Created by LXD when it unpacks an image to launch an instance from it. Deleted 10 days after it was last used to launch an instance.
- `custom` - You can add them to one or more instances as a disk device (they can be shared between instances). You can also use them as a special kind of volume to hold data separately from your instances (e.g. to hold backups or images) by setting some server configuration values. They're retained until you delete them.

!!! note
    For most storage drivers, custom storage volumes are not replicated across the cluster and exist only on the member for which they were created. This is different for remote storage pools (`ceph`, `cephfs`), where volumes are available from any cluster member.

Storage volume **content** types: 

- `filesystem` - Used for containers and container images. Default for custom storage volumes. They take a mount point.
- `block` - Used for virtual machines and virtual machine images. Can be used for custom storage volumes. A custom storage volume of this content type can be attached only to virtual machines. They don't take a mount point.
- `iso` - They're always read-only and can be attached to more than one VM at a time without corrupting data.

!!! note
    Storage volumes of content type `block` or `iso` cannot be attached to containers, only to virtual machines.

!!! warning
    Custom storage volumes of content type `block` should **not** be shared between instances because simultaneous access can cause data corruption.

#### Storage Buckets 

- Object storage using the Amazon S3 protocol. Part of a pool too, just like storage volumes. 
- Assigned access keys that must be used by applications to access the bucket.

Options:

- Local storage in a `dir`, `btrfs`, `lvm`, or `zfs` pool. Instead of adding them to an instance like a custom storage volume, they're accessed by applications directly via their URL. You must configure the S3 address for your LXD server. LXD uses MinIO for local storage buckets. 
- Remote storage ( `cephobject` pools).

### Networking

#### Network devices (NICs)

- Default network bridge.
- Use an existing network interface as a network device.
- Create a managed network and attach it to the instance as a network device.

#### Managed Networks

##### Fully controlled networks

Create network interfaces and provide most functionality e.g. IP management. Types:

- Bridge network (default) - Creates a virtual L2 ethernet switch that instance NICs can connect to. Good for  running LXD on a single system or a public cloud.
- OVN network - Software-defined networking system for virtual network abstraction. Good for building your own private cloud. Creates a logical network. Needs the OVN tools and an uplink network (an external network or a managed LXD bridge). Can be created and managed inside a project as a non-admin user.

##### External networks

Use network interfaces that already exist. Main purpose is to provide an uplink network through a parent interface.

- Macvlan network - Can assign several IP addresses to the same network interface based on randomly generated MAC addresses.
- SR-IOV network - Hardware standard that allows a single network card port to appear as several virtual network interfaces.
- Physical network - Connects to an existing physical network (network interface or bridge).

## Hardware

![RPi](https://assets.raspberrypi.com/static/raspberry-pi-4-labelled@2x-1c8c2d74ade597b9c9c7e9e2fff16dd4.png)

- 3x Raspberry Pi 4 8GB.
- 3x 3.5A Power supply (USB-C).
- 3x 2.5" SATA III SSD.
- 3x 2.5" SATA III to USB 3.0 adapter with an ASMedia chipset.
- 1x SD card.
- 1x Cluster case with fans. Optional but highly recommended. Make sure it can fit at least 3 Pis and 3 fans.
- 3x cat5e or better ethernet cables. Optional but wired connections highly recommended.

!!! important
    If using a SATA SSD make sure the cable/adapter has an **ASMedia** chipset so it will work properly with Raspberry Pi.

## Setup

1. Download the latest LTS version of Ubuntu Server for ARM architectures (24.04.1 LTS at the time of this writing).
2. 

## Notes

- MicroCloud requires static IPs. Your physical hosts should also have static IPs for convenience.
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
