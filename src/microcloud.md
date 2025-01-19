# Cloud-native Homelab

A homelab is a playground for learning, experimenting, and running workloads in a private environment at home. You can use it to deploy web servers, storage/backup solutions, media servers, home automation, development/test environments, and more.

Building a homelab in a cloud-native way has important advantages: 

- It will teach you the concepts and building blocks used by all public cloud providers like AWS or GCP so that when you learn and use their specific implementations everything will make sense.
- It can serve as a personal cloud that lets you take full control of your data and applications by hosting them yourself.
- It's a lot of fun!

The goal for this guide is to make our homelab:

- **Cost-effective** - We'll use a cluster of single-board computers (SBCs) for low cost and low power consumption.
- **Small footprint** - The homelab can even be placed on your desk or in the same space as your home router. 
- **Cloud-native** with these features:
    - Scalable, highly available, virtualized workloads. 
    - Block, file, and object storage. 
    - Software-defined networking.
- **Open source**.

The appendix has instructions for common tasks needed in any Raspberry Pi project. We'll refer to them often as we build our lab.

## Background

Quick overview of the technologies we'll work with. Based on materials compiled from different places in the Canonical documentation sites for Ubuntu, MicroCloud, LXD, Ceph, OVN, and MicroK8s as well as my own observations and tips from using these products.  
I've tried to keep it as succinct as possible so you can get right to action with enough information to get things done and understand what's happening. Then if you want to dive deep into a topic the Canonical site is a great place to start.  
Reference: [Canonical](https://canonical.com).

### Compute

LXD is a solution for managing instances which can be virtual machines or system containers.

- **Virtual machines** (VMs) have their own kernel and run on top of a hypervisor so they can run an OS different from the host. LXD uses qemu for VMs.
- **System containers** use the kernel on the host. They simulate a full OS and run multiple processes. Faster and more lightweight than VMs. Implemented through LXC. Not to be confused with *application* containers e.g. Docker - those are used to package a single process or application.

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

!!! hint
    The `ceph`, `cephfs`, and `cephobject` drivers store the data in an independent Ceph storage cluster that must be set up separately from LXD. This is where MicroCeph will come in.

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

#### Storage Volumes

They're like partitions on the disk for specific purposes. Part of a storage pool. 

Types:  

- `container`/`virtual-machine` aka instance volumes - LXD creates these automatically when you launch an instance. Used as the root disk for the instance. Destroyed when the instance is deleted.
- `image` - Created by LXD when it unpacks an image to launch an instance from it. Deleted 10 days after it was last used to launch an instance.
- `custom` - You can add them to one or more instances as a disk device (they can be shared between instances). You can also use them as a special kind of volume to hold data separately from your instances (e.g. to hold backups or images) by setting some server configuration values. They're retained until you delete them.

!!! note
    For most storage drivers, custom storage volumes are not replicated across the cluster and exist only on the member for which they were created. This is different for remote storage pools (`ceph`, `cephfs`, `cephobject`, `powerflex`), where volumes are available from any cluster member.

Storage volume **content** types: 

- `filesystem` - Used for **containers** and container images. Default for custom storage volumes. They take a mount point.
- `block` - Used for **virtual machines** and virtual machine images. Can be used for custom storage volumes. A custom storage volume of this content type can be attached only to virtual machines. They don't take a mount point.
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

#### Managed Networks

##### Fully controlled networks

They create network interfaces and provide most functionality e.g. IP management. Types:

- Bridge network (default) - Creates a virtual L2 ethernet switch that instance NICs can connect to. Good for  running LXD on a single system or a public cloud.
- OVN network - Software-defined networking system for virtual network abstraction. Good for building your own private cloud. Creates a logical network. Needs the OVN tools and an uplink network (an external network or a managed LXD bridge). Can be created and managed inside a project as a non-admin user.

##### External networks

Use network interfaces that already exist. Main purpose is to provide an uplink network through a parent interface.

- Macvlan network - Can assign several IP addresses to the same network interface based on randomly generated MAC addresses.
- SR-IOV network - Hardware standard that allows a single network card port to appear as several virtual network interfaces.
- Physical network - Connects to an existing physical network (network interface or bridge).

Ways to attach a network device:

- Default network bridge.
- Use an existing network interface as a network device.
- Create a managed network and attach it to the instance as a network device.

#### Network devices (NICs)

Network devices aka Network Interface Controllers (NICs) provide a connection to a network.

When you create a device you specify a device option (only 1 option):

- `nictype` - With this option you can specify a network interface not controlled by LXD and have to specify all the info that LXD needs to use the network interface.
- `network` - When you specify this option, the NIC is linked to an existing managed network and the `nictype` option is derived automatically from the network type.

NIC types that can be added using the `nictype` or `network` options:

- `bridged` uses an existing bridge on the host.
- `macvlan` sets up a new network device based on an existing one but with a different MAC address.
- `sriov` passes a virtual function of an SR-IOV-enabled physical network device into the instance.
- `physical` Passes a physical device from the host through to the instance. The targeted device will vanish from the host and appear in the instance.

NICs that can be added using the `network` option only.

- `ovn` Uses an existing OVN network and creates a virtual device pair to connect the instance to it

NICs that can be added using the `nictype` option only.

- `ipvlan`: Sets up a new network device based on an existing one, using the same MAC address but a different IP.
- `p2p`: Creates a virtual device pair, putting one side in the instance and leaving the other side on the host.
- `routed`: Creates a virtual device pair to connect the host to the instance and sets up static routes and proxy ARP/NDP entries to allow the instance to join the network of a designated parent interface.


## Our hardware

![RPi](https://assets.raspberrypi.com/static/raspberry-pi-4-labelled@2x-1c8c2d74ade597b9c9c7e9e2fff16dd4.png)

You'll need:

- 3x Raspberry Pi 4 8GB.
- 3x 3.5A Power supply (USB-C). I recommend getting one that includes an on/off switch for convenience.
- 3x 2.5" SATA SSD.
- 3x 2.5" SATA to USB 3.0 adapter with an ASMedia chipset.
- 1x microSD card.
- 1x Cluster case with fans. Make sure it can fit 3 Pis and 3 fans.
- 3x cat5e or better ethernet cables. Optional but wired connections highly recommended.

!!! important
    If using a SATA SSD make sure the cable/adapter has an **ASMedia** chipset so it will work properly with Raspberry Pi.

## Pi Cluster Setup

Follow these steps to set up your homelab. When an instruction tells you to power on the Pi you can either plug it in to power or flip the power supply switch to *On* if you have one.

0. Assemble your cluster according to your case's instructions. Plug the Raspberry Pis to your home network with the ethernet cables.
1. If you don't have an ssh key, [generate one](https://www.ssh.com/academy/ssh/keygen) on macOS/Linux with `ssh-keygen -t ed25519`.  
2. Download the OS image with [these instructions](#getting-os-images).
3. Set up each of the Pis to boot from SSD.
    1. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash the **USB Boot** utility image onto the microSD card. You can install it on your Mac with: 
        ```sh title="On your laptop"
        brew install --cask raspberry-pi-imager
        ```
        The USB Boot utility is in Operating System > CHOOSE OS > Misc utility images > Bootloader > USB Boot.
    2. Insert the card into the Pi, turn it on so the Pi flashes the bootloader from the card. When it's done the green LED will start blinking.
    3. Turn off the Pi and remove the card.    
4. For each Pi/SSD:
    1. [Flash the OS image](#flashing-os-images) to the SSD. 
    2. Make sure the Pi is connected to your router/switch with an ethernet cable.
    3. Remove the SSD from your laptop and plug it into a USB 3.0 port on your Pi. 
5. Turn on your Pis. They have a lot of work to do on the first boot and it takes several minutes as cloud-init automatically upgrades packages, configures our systems, and installs any software we specified.  
    You'll be able to go in as soon as the SSH service is up but it will probably still be in the process of setting everything up.  
    Go make yourself a cup of tea before accessing your Pis for the first time. If you also set up the Wi-Fi connection it won't be available until everything has finished configuring and you manually do a required system restart.
6. [Connect](#accessing-a-pi) to your Pis over ssh.
7. [Verify](#verifying-correctness) everything went smoothly.
8. Give your Pis a [static IP](#static-ip).

### LXD Cluster

The steps in this section can also be automated by adding them to the base cloud-init file and using `lxd init --preseed`.  
For now we'll go over them manually as we get more comfortable with all the moving pieces.

For each Pi:

1. Our cloud-init config already updated Snap for us so just make sure it's version 2.59.1 or later with `snap version`.
2. We need LXD version 5.21. Install or update with:
    ```sh title="pi@node-01"
    sudo snap install lxd
    # or
    sudo snap refresh lxd --channel=5.21/stable
    ```
3. We'll choose `node-01` as the bootstrap server for the LXD cluster. 
    ```sh title="pi@node-01"
    sudo lxd init
    ```
    Accept defaults for all questions below except the ones that have a specified value.
    ```title="pi@node-01"
    Would you like to use LXD clustering? (yes/no) [default=no]: yes
    What IP address or DNS name should be used to reach this server? [default=192.0.2.101]: # <===== THE STATIC IP
    Are you joining an existing cluster? (yes/no) [default=no]: no
    What member name should be used to identify this server in the cluster? [default=server1]: node-01
    Do you want to configure a new local storage pool? (yes/no) [default=yes]:
    Name of the storage backend to use (btrfs, dir, lvm, zfs) [default=zfs]:
    Create a new ZFS pool? (yes/no) [default=yes]:
    Would you like to use an existing empty block device (e.g. a disk or partition)? (yes/no) [default=no]:
    Size in GiB of the new loop device (1GiB minimum) [default=30GiB]:
    Do you want to configure a new remote storage pool? (yes/no) [default=no]:
    Would you like to connect to a MAAS server? (yes/no) [default=no]:
    Would you like to configure LXD to use an existing bridge or host interface? (yes/no) [default=no]:
    Would you like to create a new Fan overlay network? (yes/no) [default=yes]:
    What subnet should be used as the Fan underlay? [default=auto]:
    Would you like stale cached images to be updated automatically? (yes/no) [default=yes]:
    Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]:
    ```
4. Join additional servers

    !!! warning
        If you're adding existing (not newly installed) LXD servers, make sure to clear their contents before adding them to the cluster because any existing data on them will be lost.

    ```sh title="pi@node-02"
    sudo lxd init
    ```
    ```title="pi@node-02"
    Would you like to use LXD clustering? (yes/no) [default=no]: yes
    What IP address or DNS name should be used to reach this server? [default=192.0.2.101]: # <===== THE STATIC IP
    Are you joining an existing cluster? (yes/no) [default=no]: yes
    Do you have a join token? (yes/no/[token]) [default=no]: yes
    Please provide join token: # <===== enter the generated token from the command below
    All existing data is lost when joining a cluster, continue? (yes/no) [default=no] yes
    Choose "size" property for storage pool "local":
    Choose "source" property for storage pool "local":
    Choose "zfs.pool_name" property for storage pool "local":
    Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]:
    ```
    Generate a cluster join token on an existing cluster member and enter it when asked on the new joining member. 
    ```sh title="pi@node-01"
    sudo lxc cluster add node-02 # new_member_name
    ```
    Do the same for the third node.

### Provide storage disks

Each Pi will have 1 VM. We'll provide each VM with 1 disk for local storage and 1 disk for remote storage. Remote storage with high availability (HA) requires at least 3 disks located across 3 cluster members.  
That means we'll create a total of 6 disks.

Create a ZFS storage pool called `disks`
```sh title="pi@node-01"
sudo lxc storage create disks zfs size=100GiB
```

Configure default volume size for the pool
```sh title="pi@node-01"
sudo lxc storage set disks volume.size 10GiB
```

Create a custom volume (as opposed to an instance volume) for local storage
```sh title="pi@node-01"
sudo lxc storage volume create disks local1 --type block
```

Create volumes for remote storage
```sh title="pi@node-01"
sudo lxc storage volume create disks remote1 --type block size=90GiB
```

View details
```sh title="pi@node-01"
sudo lxc storage volume list disks
sudo lxc storage volume show disks custom/local1 # as opposed to container/local1 or virtual-machine/local1
sudo lxc storage volume show disks custom/remote1
```

### Create external network

Create a network for external connectivity
```sh title="pi@node-01"
sudo lxc network create microbr0
```

View network details. Note down the assigned IPv4 and IPv6 addresses for the network.
```sh title="pi@node-01"
sudo lxc network list

sudo lxc network get microbr0 ipv4.address
sudo lxc network get microbr0 ipv6.address
```

Example:
```
node-01
10.119.73.1/24
fd42:d32b:a375:2855::1/64

node-02
10.45.122.1/24
fd42:dc56:50a1:9c70::1/64

node-03
10.230.81.1/24
fd42:8cba:e02b:a498::1/64
```

### Create cluster members

#### Create the VMs 

Without starting them yet.
```sh title="pi@node-01" 
sudo lxc init ubuntu:24.04 micro1 --vm --config limits.cpu=2 --config limits.memory=4GiB -d eth0,ipv4.address=10.1.123.10 -d eth0,ipv6.address=fd42:1:1234:1234::10
```
```sh title="pi@node-02" 
sudo lxc init ubuntu:24.04 micro2 --vm --config limits.cpu=2 --config limits.memory=4GiB -d eth0,ipv4.address=10.1.123.20 -d eth0,ipv6.address=fd42:1:1234:1234::20
```
```sh title="pi@node-03" 
sudo lxc init ubuntu:24.04 micro3 --vm --config limits.cpu=2 --config limits.memory=4GiB -d eth0,ipv4.address=10.1.123.30 -d eth0,ipv6.address=fd42:1:1234:1234::30
```

#### Attach the disks to the VMs

The storage pool (`disks`) and volumes (`local1`, `remote1`) have the same names on all machines.

```sh title="pi@node-01" 
sudo lxc storage volume attach disks local1 micro1
sudo lxc storage volume attach disks remote1 micro1
```

```sh title="pi@node-02" 
sudo lxc storage volume attach disks local1 micro2
sudo lxc storage volume attach disks remote1 micro2
```

```sh title="pi@node-03" 
sudo lxc storage volume attach disks local1 micro3
sudo lxc storage volume attach disks remote1 micro3
```

#### Add instance devices

Add network interfaces that use the dedicated MicroCloud uplink network. We'll call the nic `eth1`.

See what we have so far
```sh title="pi@node-01"
sudo lxc config device list micro1 # 2, 3
```
Add the devices
```sh title="pi@node-01" 
sudo lxc config device add micro1 eth1 nic network=microbr0 # instance, device-name, type, [key=value...]
```

```sh title="pi@node-02" 
sudo lxc config device add micro2 eth1 nic network=microbr0
```

```sh title="pi@node-03"
sudo lxc config device add micro3 eth1 nic network=microbr0
```

#### Start the VMs

```sh title="pi@node-01" 
sudo lxc start micro1
```

```sh title="pi@node-02" 
sudo lxc start micro2
```

```sh title="pi@node-03"
sudo lxc start micro3
```

If a VM fails to start check if you have enough available RAM to start the VM. If needed, reduce the amount of memory assigned to the VM and try to start it again.
```sh title="On the node where the VM failed" 
free -h
# Example setting a lower RAM limit on a VM
sudo lxc config set micro2 limits.memory 2GiB
```

## MicroCloud

We'll install al required snaps on each VM and configure the network interfaces so they can be used by MicroCloud.  
MicroCloud needs a network interface that doesn't have an IP address assigned so we'll configure the network interface connected to our external traffic uplink network (`microbr0`) to refuse any IP addresses.

You can see all devices for the VM, including nics.
```sh title="pi@node-03"
sudo lxc config device --help
sudo lxc config device list micro3 #instance
sudo lxc config device show micro3 # instance
sudo lxc config device get micro3 eth1 type  # instance, device, key=[network|type]
```

### Install

Open 3 terminal windows so you can run these on all machines (`node-01`/`micro1`, `node-02`/`micro2`, `node-03`/`micro3`) at the same time.  

```sh title="pi@node-01" 
sudo lxc exec micro1 -- bash
```
```sh title="root@micro1" 
cat << EOF > /etc/netplan/99-microcloud.yaml
# MicroCloud requires a network interface that doesn't have an IP address
network:
    version: 2
    ethernets:
        enp6s0:
            accept-ra: false
            dhcp4: false
            link-local: []
EOF
chmod 0600 /etc/netplan/99-microcloud.yaml
```

!!! note
    `enp6s0` is the name that the VM assigns to the network interface that we previously added as `eth1`.
    You can verify it with `lshw -C network -short` on the VM.

Bring the network interface up.
```sh title="root@micro1" 
netplan apply
```

Install the required snaps

```sh title="root@micro1" 
snap install lxd --channel=5.21/stable --cohort="+"
snap install microceph --channel=squid/stable --cohort="+"
snap install microovn --channel=24.03/stable --cohort="+"
snap install microcloud --channel=2/stable --cohort="+"

# if lxd is already installed, just refresh it to the latest version
# snap refresh lxd --channel=5.21/stable --cohort="+"
```

!!! note
    The `--cohort="+"` flag in the command ensures that the same version of the snap is installed on all machines so the cluster members [stay in sync]((https://canonical-microcloud.readthedocs-hosted.com/en/latest/microcloud/how-to/snaps/#howto-snap-cluster)).

After you've done this on all 3 machines, you're done!

### Initialize

This ia a good time to make sure our systems are upgraded and `snap/bin` has been added to our PATH by rebooting our machines. 

For each machine (make sure you have 3 terminal windows open, 1 for each Node.):
```sh title="root@micro1" 
exit
```
```sh title="pi@mnode-01" 
sudo apt update
sudo apt upgrade
sudo reboot
```
Wait a bit for the system to restart and then:
```sh title="On your laptop" 
ssh pi@node-01
```
```sh title="pi@mnode-01" 
sudo lxc exec micro1 -- bash
```
Done!

Now you can use any of the VMs to initialize MicroCloud but here we'll use `micro1`
```sh title="root@micro1" 
microcloud init
```
```
Do you want to set up more than one cluster member? (yes/no) [default=yes]: yes
Select an address for MicroCloud's internal traffic: <=== the IPv4 address
# Copy the session passphrase
```

On each of the other VMs, join the cluster
```sh title="root@micro2" 
microcloud join
# select the IPv4 address
# when asked, enter the session passphrase
```


## APPENDIX

### Getting OS images
   
We'll use an **Ubuntu** image made specifically for your board instead of a manufaturer's custom OS like Raspberry Pi OS. Those are designed for simplicity and ease of use at the expense of functionality that is important when building a cloud-native homelab like [`cloud-init`](https://cloud-init.io). That's right, even our host Raspberry Pis can be set up in an automated, cloud-native way with cloud-init!

!!! tip
    This lets you launch your Pi just like a cloud instance. Automatically upgrade the system, configure users, modify boot parameters, install software, run commands on first boot, among other things.

We'll use the *Server* version because we need a non-HWE variant for our storage pools and we don't need the graphical environment that comes with the *Desktop* version.  

Download the [official Ubuntu image for Raspberry Pi](https://ubuntu.com/download/raspberry-pi) with these commands:
```sh title="On your laptop" 
cd ~/Downloads
wget -q --show-progress https://cdimage.ubuntu.com/releases/24.04.1/release/ubuntu-24.04.1-preinstalled-server-arm64+raspi.img.xz
```

Verify the integrity of the image file with its [checksum](https://github.com/canonical/ubuntu.com/blob/main/releases.yaml):
```sh title="On your laptop" 
echo "e59925e211080b20f02e4504bb2c8336b122d0738668491986ee29a95610e5b1 *ubuntu-24.04.1-preinstalled-server-arm64+raspi.img.xz" | shasum -a 256 --check
```

If you see an `OK` message like `ubuntu-24.04.1-preinstalled-server-arm64+raspi.img.xz: OK` go ahead and decompress the file:
```sh title="On your laptop"
xz -d ubuntu-24.04.1-preinstalled-server-arm64+raspi.img.xz
```

### Flashing OS images

We'll flash a pre-configured SSD with:  

* A hostname.
* A user with ssh key authentication (and password authentication disabled).
* Upgraded packages.
* Additional packages installed.
* Wi-Fi configuration.
* Optional: Boot parameters modified to support application container orchestration if we ever want to use that.

Execute each code block one at a time to avoid errors.

!!! attention
    This guide uses macOS. If you're on something else, adjust the commands with your OS's tools to [copy/paste](https://ostechnix.com/how-to-use-pbcopy-and-pbpaste-commands-on-linux/) and view disks, as well as its `dd` options and [`sed` version](https://unix.stackexchange.com/questions/13711/differences-between-sed-on-mac-osx-and-other-standard-sed).  

!!! tip
    Install `pv` to see a progress bar and percentage of completion as the image is being flashed:  
    `brew install pv`

Connect the target device (e.g. SSD) and check the device name. 
If macOS tells you *The disk you attached was not readable by this computer* you can ignore it.
```sh title="On your laptop" 
diskutil list
```

Wipe out any existing data/partitions.

!!! danger
    Make sure you got the right device name. All data on the device will be lost.

```sh title="On your laptop" 
diskutil zeroDisk short /dev/disk4 # or whatever name your device has
```
On Linux you can use [`parted`](https://www.gnu.org/software/parted/manual/parted.html).  

Use that device name to flash the OS image to the card/SSD.
```sh title="On your laptop" 
###################################################################
# REPLACE WITH YOUR VALUES
###################################################################
IMAGE='ubuntu-24.04.1-preinstalled-server-arm64+raspi.img' 
DEVICE='/dev/disk4' 
###################################################################

# Unmount the card/ssd
diskutil unmountDisk $DEVICE

cd ~/Downloads
# sudo dd if=$IMAGE of=$DEVICE bs=1m status=progress
pv $IMAGE | sudo dd bs=1m of=$DEVICE
```

When it's done you'll see a volume mounted on your desktop called `system-boot` or something similar.  
We'll modify the volume to inject the `user-data` used by cloud-init and set boot parameters to enable c-groups. On systems running k8s this is required so that kubelet will work out of the box but we'll do it here in case we want to do container orchestration directly on this system (or on system containers that share its kernel) later on.  

Feel free to modify in case you don't want to set up Wi-Fi or want different software installed.
```sh title="On your laptop" 
###################################################################
# REPLACE WITH YOUR VALUES
###################################################################
VOLUME='system-boot'

HOSTNAME='node-01' # Change for node-02, node-03
LOCALE='en_US' 
TIMEZONE='US/Central' 

WIFI_NAME='MySSID' 
WIFI_PASSWORD='MyPassword' 

pbcopy < ~/.ssh/id_ed25519.pub
KEY=$(pbpaste)
###################################################################
```

```sh title="On your laptop" 
# create file for `cloud-init`
cat << EOF > /Volumes/$VOLUME/user-data
#cloud-config

hostname: ${HOSTNAME}
manage_etc_hosts: false
locale: ${LOCALE}
timezone: ${TIMEZONE}

users:
  - name: pi
    shell: /bin/bash
    lock_passwd: true
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ${KEY}

package_upgrade: true
packages:
  # For detailed hardware info
  - lshw
  # Networking tools like ifconfig
  #- net-tools
  # Kernel modules needed by storage solutions like OpenEBS or Rook Ceph
  - linux-modules-extra-$(uname -r)
  # For managing logical partitions
  - lvm2

write_files:
- content: |
    # This file is generated from information provided by the datasource.  Changes
    # to it will not persist across an instance reboot.  To disable cloud-init's
    # network configuration capabilities, write a file
    # /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
    # network: {config: disabled}
    network:
        ethernets:
            eth0:
                dhcp4: true
                optional: true
        version: 2
        wifis:
            wlan0:
                optional: true
                access-points:
                    "${WIFI_NAME}":
                        password: "${WIFI_PASSWORD}"
                dhcp4: true
  path: /etc/netplan/50-cloud-init.yaml
- content: |
    network: {config: disabled}
  path: /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg

runcmd:
  #- sudo ifconfig wlan0 up
  - sudo snap refresh
  # For MicroK8s
  #- sudo snap install microk8s --channel=1.28/stable --classic
  #- sudo usermod -a -G microk8s pi
  #- sudo chown -f -R pi ~/.kube
  #- newgrp microk8s
  # For OpenEBS
  #- sudo sysctl vm.nr_hugepages=1024
  #- echo 'vm.nr_hugepages=1024' | sudo tee -a /etc/sysctl.conf
  #- sudo modprobe nvme_tcp
  #- echo 'nvme-tcp' | sudo tee -a /etc/modules-load.d/microk8s-mayastor.conf
  # For Ceph
  - sudo modprobe rbd
  - echo 'rbd' | sudo tee -a /etc/modules-load.d/modules.conf
  # For full-disk encryption
  - sudo modprobe dm-crypt
  - echo 'dm-crypt' | sudo tee -a /etc/modules-load.d/modules.conf
EOF

# For Kubernetes to run on the Pi, add these options at the end of the file.
sed -i "" "$ s/$/ cgroup_enable=memory cgroup_memory=1/" /Volumes/$VOLUME/cmdline.txt
```

You can verify that the files were written correctly
```sh title="On your laptop" 
cat /Volumes/$VOLUME/user-data
```
```sh title="On your laptop" 
cat /Volumes/$VOLUME/cmdline.txt
```

Unmount the card/SSD
```sh title="On your laptop"
diskutil unmountDisk $DEVICE
```

🎉 **You're done!** 🍾  

Head back to the [Pi Cluster Setup](#pi-cluster-setup) section for the next steps.

### Accessing a Pi

!!! tip

    **Before connecting to your Pi**  
    If it's not already running, start the `ssh-agent` in the background and add your private key to it so you're not asked for your passphrase every time.
    ```sh title="On your laptop"
    # is it running?
    ps -ax | grep ssh-agent
    # which identities have been added?
    ssh-add -l

    # start the agent and add your identity
    eval "$(ssh-agent -s)"
    ssh-add --apple-use-keychain ~/.ssh/id_ed25519
    ```

!!! attention
    If you're **reinstalling** the OS you might need to remove old key fingerprints belonging to that hostname from your `known_hosts` file.  
    Examples:
    ```sh title="On your laptop"
    ssh-keygen  -f ~/.ssh/known_hosts -R 192.168.xxx.xxx
    ssh-keygen  -f ~/.ssh/known_hosts -R node-01
    ssh-keygen  -f ~/.ssh/known_hosts -R raspberrypi4b.local
    ```

SSH into it with the configured user e.g. `pi` and hostname or IP address.  
The first time you access it you'll get asked about adding the key fingerprint to the list of known hosts. Choose `yes`.
```sh title="On your laptop"
ssh pi@node-01 # hostname or IP address
```

!!! attention
    If you're on a VPN you may need to disconnect from it to access your Pis using the hostname.

If you want to use the IP address, find your board's IP in your router's admin UI or by going over the list of all devices on your network with `arp -a`.

If you see a welcome message with `System restart required`, `sudo reboot` and ssh again.

### Verifying correctness

Once cloud-init is done launching our instance, check a few things to make sure everything went smoothly.

Access your Pi via ssh as explained [here](#accessing-a-pi).

```sh title="pi@node-01"
# Verify your kernel is built with the modules you need for Ceph RBD (RADOS Block Device) and for disk encryption. 
# It's OK if they're not currently being used (a zero in the third column of the results). They just need to be loaded.
lsmod | grep -iE 'crypto|dm_crypt|aes' # verify that at least dm_crypt is available.
lsmod | grep -iE 'rbd|ceph' # verify that at least rbd is available.

# You can also check with
sudo modinfo dm-crypt
sudo modinfo rbd

# if they're not found:
sudo modprobe dm-crypt
sudo modprobe rbd

# Check if the unattended upgrade service is running
systemctl status unattended-upgrades.service

# Check cloud-init's network configuration 
cat /etc/netplan/50-cloud-init.yaml
cat /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg

# Look at the state of the network.
# You may need to `sudo reboot` for Wi-Fi to be enabled but 
# make sure you've allowed enough time for cloud-init to 
# finish configuring your instance.
sudo lshw -c network
ip addr show | grep wlan0
```

### Static IP

#### Option A: The router

Check the MAC address of your `eth0` interface (**not** your `wlan0`, for example).
```sh title="pi@node-01"
lshw -C network -short
```

Log in to your router's admin interface and go to **LAN** -> **DHCP Server** (or similar wording).  
There will be an option to manually assign an IP address to an item on the list of client MAC addresses. Choose the MAC address you got from the command above.  
Add all the needed records and apply changes.

#### Option B: `dhcpcd.conf`
Find the IP adddress of your router. It's the address that appears after `default via`.
```sh title="pi@node-01"
ip r
default via [IP]
```
Get the IP of your DNS server (it may or may not be your router)
```sh title="pi@node-01"
grep nameserver /etc/resolv.conf
```

Open this file:
```sh title="pi@node-01"
nano /etc/dhcpcd.conf
```
and add/edit these lines at the end filling in the correct info.
```
interface [wlan0 for Wi-Fi or eth0 for Ethernet]
static_routers=[ROUTER IP]
static domain_name_servers=[DNS IP]
[static or inform] ip_address=[STATIC IP ADDRESS YOU WANT]/24
```
`inform` means that the Pi will attempt to get the IP address you requested, but if it's not available, it will choose another. If you use `static`, it will have no IP v4 address at all if the requested one is in use.  

Save the file and `sudo reboot`. From now on, upon each boot, the Pi will attempt to obtain the static ip address you requested.  

## Troubleshooting

* I see `cloud-init` had failures.  
    Based on the `user-data` file:
    Manually run `sudo apt update`, `sudo apt full-upgrade`.  
    Manually run `sudo apt install` on any packages that failed.  
    Manually add any kernel modules you need and make sure `/etc/modules-load.d/modules.conf` has them so they'll be added on every boot.
* I'm not sure cgroups are enabled.  
    Check with 
    ```sh title="pi@node-01"
    cat /proc/cgroups
    ```

## Cleanup

View
```sh title="pi@node-01"
sudo lxc cluster list # LXD cluster members
sudo lxc cluster show node-01

sudo lxc storage list #storage pools
sudo lxc storage show local

sudo lxc storage volume list # storage volumes
sudo lxc storage volume list local # storage volumes for a pool

sudo lxc network list # networks
sudo lxc network show lxdfan0

sudo lxc list #instances
sudo lxc show micro1

sudo lxc config device list micro1 # instance devices

```

Delete
```sh title="pi@node-01"
sudo lxc stop micro1 # 1, 2, 3
sudo lxc delete micro1 # 1, 2, 3

sudo lxc storage volume delete disks local1
sudo lxc storage volume delete disks remote1

sudo lxc storage delete disks

#networks
sudo lxc network delete microbr0

sudo snap remove lxd --purge # uninstall lxd

snap saved
sudo snap forget 1 # snapshot id
```