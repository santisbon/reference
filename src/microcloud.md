# Cloud-native Homelab

A homelab is a playground for learning, experimenting, and running workloads in a private environment at home. You can use it to deploy web servers, storage/backup solutions, media servers, home automation, development/test environments, and more.

Building a homelab in a cloud-native way will teach you the concepts and building blocks used by all public cloud providers like AWS or GCP so that when you learn and use their specific implementations everything will make sense.

The goal for this guide is to make our homelab:

- **Cost-effective**: We'll use a cluster of single-board computers (SBCs) for low cost and low power consumption.
- **Cloud-native** with these features:
    - Scalable, highly available, virtualized workloads. 
    - Block, file, and object storage. 
    - Software-defined networking.
- **Open source**.

## Background and Terminology

Quick overview of the technologies we'll work with. Based on  and summarized from materials compiled from different places in the Canonical documentation sites for Ubuntu, MicroCloud, MicroK8s, LXD, Ceph, and OVN.  
Reference: [Canonical](https://canonical.com)

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


## Hardware

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

## Setup

Follow these steps to set up the Raspberry Pi devices. When an instruction tells you to power on the Pi you can either plug it in to power or flip the power supply switch to *On* if you have one.

0. Assemble your cluster according to your case's instructions. Plug the Raspberry Pis to your home network with the ethernet cables.
1. If you don't have an ssh key, [generate one](https://www.ssh.com/academy/ssh/keygen) on macOS/Linux with `ssh-keygen -t ed25519`.  
2. Download the OS image with [these instructions](#getting-os-images).
3. Set up each of the Pis to boot from SSD.
    1. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash the **USB Boot** utility image onto the microSD card. 
        ```sh
        brew install --cask raspberry-pi-imager
        ```
        It's in Operating System > CHOOSE OS > Misc utility images > Bootloader > USB Boot.
    2. Insert the card into the Pi, turn it on so the Pi flashes the bootloader from the card. When it's done the green LED will start blinking.
    3. Turn off the Pi and remove the card.    
4. For each SSD flash your desired OS image to the SSD as explained [here](#flashing-os-images).
5. For each Pi/SSD remove the SSD from your laptop and plug it into a USB 3.0 port on your Pi which **should be connected to your router with an ethernet cable**. The Wi-Fi won't be available until everything has finished configuring and you manually do a required system restart.
6. Turn on your Pis.
7. Connect to your Pis over ssh and check available storage space with `df -h`.

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
```sh
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

Insert/connect the target device (microSD card or SSD) and check the device name. 
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
On Linux you can use `parted` as explained [here](#ssd-as-additional-storage).  

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

When it's done you'll see a volume mounted on your desktop called `system-boot` or something similar. Modify the volume to inject the `user-data` used by cloud-init and set boot parameters to enable c-groups. On systems running k8s this is required so that kubelet will work out of the box but we'll do it here anyways in case we want to install k8s on this system later on.  

Feel free to modify in case you don't want to set up Wi-Fi or want different software installed.
```sh title="On your laptop" 
###################################################################
# REPLACE WITH YOUR VALUES
###################################################################
VOLUME='system-boot'

HOSTNAME='node-01' 
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

Since we pre-configured everything it has a lot of work to do on the first boot and it takes several minutes. You'll be able to go in as soon as the SSH service is up but it will probably still be in the process of upgrading packages as well as installing and configuring our software.  

Go make yourself a cup of tea before [connecting](#access-your-pi) for the first time.

#### Verification

Once cloud-init is done launching our instance, check a few things to make sure everything went smoothly.
```sh title="On your laptop"
ssh pi@$IP_ADDRESS_OF_YOUR_PI
```
If you see a welcome message with `System restart required`, `sudo reboot` and ssh again.

```sh title="On your Pi"
# Check if there were any cloud-init errors
sudo cat /var/log/cloud-init.log | grep failures
sudo cat /var/log/cloud-init-output.log
```

!!! important
    If anything failed to install or commands ran into errors, run it again manually.

```sh title="On your Pi"
# Verify your kernel is built with the modules you need. If modprobe shows 'not found' install the extra kernel modules package for your kernel release, rebuild the kernel to include the modules you need, install a newer kernel, or choose a different Linux distribution.
lsmod | grep rbd
# if it's not enabled:
sudo modprobe rbd

lsmod | grep dm-crypt
# if it's not enabled:
sudo modprobe dm-crypt

# Check if packages were installed
apt list --installed | grep linux-modules-extra-$(uname -r)
sudo cat /var/log/apt/history.log

# Check if a service is running
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

### SSD as Additional Storage

!!! important
    If using a SATA SSD make sure the cable/adapter has an **ASMedia** chipset so it will work properly with Raspberry Pi.

If you have an additional SSD you'll need to:

1. Choose a partition manipulation program
    * [GNU Parted](https://www.gnu.org/software/parted/manual/parted.html) (`parted`) is probably already installed and ready to use from the command line. 
    * [GParted](https://thepihut.com/blogs/raspberry-pi-tutorials/how-to-set-up-an-ssd-with-the-raspberry-pi) - If you have a desktop environment you can use this graphical frontend. Install with `sudo apt install gparted`.
2. Create a partition table (aka disklabel). The default partition table type is `msdos` for disks smaller than 2 Tebibytes in size (assuming a 512 byte sector size) and `gpt` for disks 2 Tebibytes and larger.
3. Create partition(s) and file system(s).
4. Find the file system's UUID.
5. Create a directory for mounting the SSD.
6. Set up automatic SSD mounting, mount the SSD, reboot to test.

Example with `parted`:
```sh
cat /sys/block/sda/queue/optimal_io_size
# 33553920
cat /sys/block/sda/queue/minimum_io_size
# 512
cat /sys/block/sda/alignment_offset
# 0
cat /sys/block/sda/queue/physical_block_size
# 512

sudo parted

(parted) print devices # you should see your SSD e.g. /dev/sda (240GB)
(parted) select /dev/sda # whatever name your SSD device has
(parted) mklabel msdos 

# Add optimal_io_size to alignment_offset and divide the result by physical_block_size.
# This number is the sector at which the partition should start. Here it ends in the last sector.
# Example:
(parted) mkpart primary ext4 65535s -1s

(parted) print list
(parted) align-check optimal 1 # or whatever number your partition has
# 1 aligned 
(parted) quit

# Make the filesystem with a volume label on partition 1 (or whatever number yours has)
sudo mkfs.ext4 -L WDSSD -c /dev/sda1
# Filesystem UUID is displayed but you can also find it with:
sudo lsblk -o UUID,NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL,MODEL

mkdir wdssd
sudo chown pi:pi -R /home/pi/wdssd/
sudo chmod a+rwx /home/pi/wdssd/
sudo nano /etc/fstab
# At the end of the file that opens, add a new line containing the UUID and mounting directory
# UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx /home/pi/wdssd/ ext4 defaults,auto,users,rw,nofail 0 0
```

### Resizing a root partition

By default the root partition will consume all the available space. If you have an SSD you may want to set up partitions appropriately for things like a Ceph cluster. You can't shrink a system partition while it's being used so **we'll create our own GParted bootable USB drive**. This is because the GParted Live image available for download is only for x86-based architectures like amd64. Both the Pi and Apple Silicon Macs are arm64.

1. Put a microSD card in a USB adapter and flash a Linux distribution with a desktop GUI.

    !!! danger
        Make sure you got the right device name. All data on the device will be lost.

    ```sh title="On your laptop" 
    diskutil list
    diskutil zeroDisk short /dev/disk5
    ```
    ```sh
    ###################################################################
    # REPLACE WITH YOUR VALUES
    ###################################################################
    IMAGE='ubuntu-22.04.3-preinstalled-desktop-arm64+raspi.img' 
    DEVICE='/dev/disk5' 
    ###################################################################

    # Unmount the card
    diskutil unmountDisk $DEVICE

    cd ~/Downloads
    # sudo dd if=$IMAGE of=$DEVICE bs=1m status=progress
    pv $IMAGE | sudo dd bs=1m of=$DEVICE
    ```
    ```sh
    diskutil unmountDisk $DEVICE
    ```

2. After setting up your Pi with the USB bootloader (see the *Boot from SSD* section), connect the SSD to your Pi using a USB 3.0 port.
3. Allow time for cloud-init to finish configuring your SSD and connect to it via SSH for a required `sudo reboot`.
4. Connect via SSH again and `sudo shutdown -h now`.
5. Disconnect the SSD and connect the GParted USB to a USB 3.0 port, a monitor or TV, a mouse, and a keyboard. Turn on your Pi.
6. After setting up the OS, install GParted.
    ```sh title="On your Pi" 
    sudo apt update
    sudo apt upgrade
    sudo apt install gparted
    ```
7. Connect the SSD to the other USB 3.0 port and open GParted. Hit *Refresh devices* if needed. Select the SSD e.g. `/dev/sdb`.
8. Right-click on the root ext4 partition e.g. `/dev/sdb2` (it should already be unmounted) and select and apply these operations.
    1. Check the root partition.
    2. Resize it to 64 Gi (65,536 Mi) or desired size.
    3. Create unformatted partition in the unallocated space.
    4. Check the root partition again.
9. Turn off the Pi. Disconnect the GParted USB, keep the SSD connected and turn it on.

**Alternatively**, you can use `parted` to set up/resize the SSD partitions and file systems as desired. For example, leave a raw partition (no formatted filesystem) for use by a Ceph storage cluster.  

1. [Resize the filesystem](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_file_systems/getting-started-with-an-ext4-file-system_managing-file-systems#resizing-an-ext4-file-system_getting-started-with-an-ext4-file-system).
2. If needed, [shrink the partition](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_file_systems/partition-operations-with-parted_managing-file-systems#proc_resizing-a-partition-with-parted_partition-operations-with-parted) to leave space to be used by Ceph.

Repeat for each node in your cluster.

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
