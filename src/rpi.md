# Raspberry Pi

![RPi](https://www.raspberrypi.org/pagekit-assets/media/images/dfb2931ebc2dbf1cc9e6.svg)

## Boot from SSD

!!! important
    If using a SATA SSD make sure the cable/adapter has an **ASMedia** chipset so it will work properly with Raspberry Pi.

These instructions are for Raspberry Pi 4. Other boards may need [additional steps](https://www.makeuseof.com/how-to-boot-raspberry-pi-ssd-permanent-storage/).

1. Use Raspberry Pi Imager to flash the **USB Boot** bootloader utility image onto a microSD card.
2. Insert the card into the Pi, turn it on so the Pi flashes the bootloader from the card. When it's done the green LED will start blinking.
3. Turn off the Pi and remove the card.
4. Connect a raw device (no partitions or formatted filesystems) SSD to your laptop. If the device already has partitions wipe out everything e.g. on a Mac:
    
    !!! danger
        Make sure you got the right device name. All data on the device will be lost.

    ```sh
    diskutil list
    diskutil zeroDisk short /dev/disk5 # or whatever name your device has
    ```
    On Linux you can use `parted` as explained [here](#ssd-as-additional-storage).

5. Flash your desired OS image to the SSD with `dd` or preferred tool e.g. as explained [here](#flash-the-image).
6. Unmount and remove the SSD drive from your laptop and connect it to a USB 3.0 port on your Pi.
7. Turn on your Pi.
8. Connect to your Pi over ssh and check available storage space with `df -h`.

## SSD as Additional Storage

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

## Get OS image

You *could* use an imager program that flashes an operating system for you but you'll be very limited in the ways you can pre-configure the OS. It's better to download the OS image and flash it yourself.  
   
I recommend using an **Ubuntu** image made specifically for your board instead of a manufaturer's custom OS like Raspberry Pi OS or Orange Pi OS. Those are designed for simplicity and ease of use at the expense of functionality that is important when building a cloud native homelab.

* ❌ Raspberry Pi OS doesn't come with [`cloud-init`](https://cloud-init.io).
* ❌ Orange Pi OS doesn't support the GPU, Neural Processing Unit (NPU), and Vision Processing Unit (VPU) that some Orange Pi boards have for Artificial Intelligence and graphics-intensive workloads.
* ✅ Ubuntu comes with `cloud-init`.
* ✅ Ubuntu comes with [Snap](https://ubuntu.com/core/services/guide/snaps-intro) support preinstalled.
* ✅ Ubuntu, Debian, and Android support the Orange Pi's GPU, NPU, and VPU.

Make sure you grab the image corresponding to your Pi's CPU architecture (32-bit or 64-bit). We'll use the *Server* version because we don't need the graphical environment that comes with the *Desktop* version.  

Official Ubuntu images for all Raspberry Pis (recommended):  
[Download](https://ubuntu.com/download/raspberry-pi)  
[Checksums](https://github.com/canonical/ubuntu.com/blob/main/releases.yaml)

Manufacturer's images for Orange Pi 3B:    
[Download](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-3B.html)  

The rest of this guide assumes you downloaded your image to `~/Downloads`.

Examples of verifying the integrity of the image file:
```sh title="On your laptop" 
# Check the sum from the Ubuntu website and decompress
echo "f3842efb3be1be4243c24203bd16e335f155fdbe104b1ed8c5efc548ea478ab0 *ubuntu-22.04.3-preinstalled-server-arm64+raspi.img.xz" | shasum -a 256 --check
xz -d ubuntu-22.04.3-preinstalled-server-arm64+raspi.img.xz

# Extract Orange Pi image and check the sum
7zz x Orangepi3b_1.0.0_ubuntu_jammy_server_linux5.10.160.7z
shasum -c Orangepi3b_1.0.0_ubuntu_jammy_server_linux5.10.160.img.sha
```

## Option A: Cloud native 

### Overview

This is the repeatable, flexible option.

!!! tip
    This lets you launch your Pi just like a cloud instance. Automatically upgrade the system, configure users, modify boot parameters, install software, run commands on first boot, among other things. Recommended when setting up multiple Pis or installing Kubernetes.

!!! important
    This requires the OS image to:

    * Have `cloud-init` preinstalled.
    * Be mountable on the OS you're using (e.g. macOS) so you can inject `user-data` and boot parameters.
    
    ✅ Supported by the Ubuntu images for Raspberry Pi.  
    ❌ Not supoprted by Orange Pi images.

    If you're setting up an Orange Pi, download the image and see the [one-off](#option-b-one-off) instructions.

We'll flash a pre-configured microSD card or SSD with:  

* A hostname.
* A user with ssh key authentication (and password authentication disabled).
* Upgraded packages.
* Additional packages installed.
* Wi-Fi configuration.
* Boot parameters modified to support Kubernetes.
* Kubernetes ([MicroK8s](https://microk8s.io)).

If you don't have an ssh key, [generate one](https://www.ssh.com/academy/ssh/keygen) with `ssh-keygen -t ed25519`.  

!!! tip
    Install `pv` to see a progress bar and percentage of completion as the image is being flashed:  
    `brew install pv`

!!! attention
    This example uses macOS. Adjust the commands with your OS's tools to [copy/paste](https://ostechnix.com/how-to-use-pbcopy-and-pbpaste-commands-on-linux/), view disks, `dd` options, and [`sed` version](https://unix.stackexchange.com/questions/13711/differences-between-sed-on-mac-osx-and-other-standard-sed). It has been tested with the image provided by Ubuntu for Raspberry Pi.  

### Flash the image

Insert the microSD card (or connect the SSD) and check the device name.  
Wipe out any existing data/partitions.

!!! danger
    Make sure you got the right device name. All data on the device will be lost.

```sh title="On your laptop" 
diskutil list
diskutil zeroDisk short /dev/disk5
```

Use that device name to flash the OS image to the card/SSD.
```sh title="On your laptop" 
###################################################################
# REPLACE WITH YOUR VALUES
###################################################################
IMAGE='ubuntu-22.04.3-preinstalled-server-arm64+raspi.img' 
DEVICE='/dev/disk5' 
###################################################################

# Unmount the card
diskutil unmountDisk $DEVICE

cd ~/Downloads
# sudo dd if=$IMAGE of=$DEVICE bs=1m status=progress
pv $IMAGE | sudo dd bs=1m of=$DEVICE
```

When it's done you'll see a volume mounted on your desktop called `system-boot` or something similar. Modify the volume to inject `user-data` and set boot parameters to enable c-groups so the kubelet will work out of the box.
```sh title="On your laptop" 
###################################################################
# REPLACE WITH YOUR VALUES
###################################################################
VOLUME='system-boot'

HOSTNAME='raspberrypi4b' 
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
  #- lshw
  #- net-tools
  # For OpenEBS or Rook Ceph
  - linux-modules-extra-$(uname -r)
  # For Rook Ceph
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
  - sudo ifconfig wlan0 up
  - sudo snap refresh
  # For MicroK8s
  - sudo snap install microk8s --channel=1.28/stable --classic
  - sudo usermod -a -G microk8s pi
  - sudo chown -f -R pi ~/.kube
  - newgrp microk8s
  # For OpenEBS
  # - sudo sysctl vm.nr_hugepages=1024
  # - echo 'vm.nr_hugepages=1024' | sudo tee -a /etc/sysctl.conf
  # - sudo modprobe nvme_tcp
  # - echo 'nvme-tcp' | sudo tee -a /etc/modules-load.d/microk8s-mayastor.conf
  # For Rook Ceph
  - sudo modprobe rbd
  - echo 'rbd' | sudo tee -a /etc/modules-load.d/modules.conf
EOF

# For Kubernetes to run on the Pi, add these options at the end of the file.
sed -i "" "$ s/$/ cgroup_enable=memory cgroup_memory=1/" /Volumes/$VOLUME/cmdline.txt
```

You can verify that the files were written correctly
```sh title="On your laptop" 
cat /Volumes/$VOLUME/user-data
cat /Volumes/$VOLUME/cmdline.txt
```

Unmount the card/SSD
```sh title="On your laptop"
diskutil unmountDisk $DEVICE
```

🎉 **You're done!** 🍾  

Now remove the card/SSD from your laptop and insert it into the Pi which **should be connected to your router with an ethernet cable**. The Wi-Fi won't be available until everything has finished configuring and you manually do a required system restart.

Since we pre-configured everything it has a lot of work to do on the first boot and it takes several minutes. You'll be able to go in as soon as the SSH service is up but it will probably still be in the process of upgrading packages as well as installing and configuring our software.  

Go make yourself a cup of tea before [connecting](#access-your-pi) for the first time.

### Verify

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

## Option B: One-off 

!!! tip
    This is the easiest option but is limited in how much you can pre-configure the OS. Recommended if you're setting up only one board or if your OS image doesn't have `cloud-init`.


### Flash the image

Use Raspberry Pi Imager or Balena Etcher (`brew install --cask [raspberry-pi-imager | balenaetcher]`) to flash the image to the microSD card or SSD. If you use Pi Imager you can:  

* Change the password for the default user or disable passwords altogether.  
* Enable SSH (password or ssh keys); remove password authentication if using keys.  
* Configure Wi-Fi if needed.  
* Set the hostname.  

!!! attention
    The Orange Pi images have to be configured manually after first boot.

[Access your Pi](#access-your-pi) 

### Upgrade

* `upgrade` is used to install available upgrades of all packages currently installed on the system. New packages will be installed if required to satisfy dependencies, but existing packages will never be removed. If an upgrade for a package requires the removal of an installed package the upgrade for this package isn't performed.  
* `full-upgrade` performs the function of upgrade but will remove currently installed packages if this is needed to upgrade the system as a whole.

```sh title="On your Pi"
sudo apt update # updates the package list
sudo apt full-upgrade
```

#### Authentication

If you **didn't do so during setup**, generate and add an ssh key.
```sh title="On your laptop"
# Specify the type of key to create e.g. `ed25519` or `rsa`.
ssh-keygen -t ed25519
# Add it on the remote machine (if the `-i` filename does not end in `.pub` this is added)
# Examples:
ssh-copy-id -i ~/.ssh/id_rsa pi@raspberrypi4b.local
ssh-copy-id -i ~/.ssh/id_ed25519 orangepi@orangepi3b.local
```

To remove password authentication:
```sh title="On your Pi"
sudo nano /etc/ssh/sshd_config
```
and replace `#PasswordAuthentication yes` with `PasswordAuthentication no`.
Test the validity of the config file and restart the service (or reboot).
```sh title="On your Pi"
sudo sshd -t
sudo service sshd restart
sudo service sshd status
```

#### Board-specific tools

##### Raspberry Pi

On Raspberry Pi OS
```sh title="On your Pi"
sudo raspi-config
# Go to Interface Options, VNC (for graphical remote access)
# Tab to the Finish option and reboot.
```

##### Orange Pi

In Ubuntu for Orange Pi, to reach other machines by hostname you need to add an entry to the hosts file. Example:
```sh title="/etc/hosts"
192.168.x.x  thathostname
```

Orange Pi has a config tool as well
```sh title="On your Pi"
sudo orangepi-config
```
If you just need to connect to Wi-Fi on Orange Pi, use:
```sh title="On your Pi"
nmcli dev wifi connect wifi_name password wifi_passwd
```

To set a static IP on Orange Pi see the [user manual](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-3B.html) for instructions on using the `nmtui` command.

## Usage

### Access your Pi

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

If you're **reinstalling** the OS you might need to remove old key fingerprints belonging to that hostname from your `known_hosts` file. Example:
```sh title="On your laptop"
ssh-keygen  -f ~/.ssh/known_hosts -R raspberrypi4b.local
```

Find your board's IP in your router's admin UI or by going over the list of all devices on your network with `arp -a`.

SSH into it with the configured user e.g. `pi` and the IP address or hostname. Examples:
```sh title="On your laptop"
ssh pi@raspberrypi4b.local
# or
ssh pi@192.168.xxx.xxx
```

Update the password for default users like `pi`, `orangepi`, `ubuntu`, etc. Examples:
```sh title="On your Pi"
sudo passwd root
sudo passwd pi
```

### Remote GUI access
*If you installed a graphical desktop*

You'll need a VNC viewer on your laptop to connect to the Pi using the graphical interface.
```sh title="On your laptop"
brew install --cask vnc-viewer
```

!!! attention
    Apparently, on Raspberry Pi OS `pip` does not download from the Python Package Index (PyPI), it downloads from PiWheels. PiWheels wheels do not come with `pygame`'s dependencies that are bundled in normal releases.

    Install Pygame [dependencies](https://www.piwheels.org/project/pygame/) and Pygame.
    ```sh title="On your Pi"
    sudo apt install libvorbisenc2 libwayland-server0 libxi6 libfluidsynth2 libgbm1 libxkbcommon0 libopus0 libwayland-cursor0 libsndfile1 libwayland-client0 libportmidi0 libvorbis0a libopusfile0 libmpg123-0 libflac8 libxcursor1 libxinerama1 libasyncns0 libxrandr2 libdrm2 libpulse0 libxfixes3 libvorbisfile3 libmodplug1 libxrender1 libsdl2-2.0-0 libxxf86vm1 libwayland-egl1 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libjack0 libsdl2-mixer-2.0-0 libinstpatch-1.0-2 libxss1 libogg0
    sudo pip3 install pygame

    # Check that the installation worked by running one of its demos
    python3 -m pygame.examples.aliens
    ```

### To give it a static IP

#### Option A: The router

Log in to your router's admin interface and go to **LAN** -> **DHCP Server** (or similar wording). There will be an option to manually assign an IP to an item on the list of client MAC addresses.

#### Option B: `dhcpcd.conf`
Find the IP adddress of your router. It's the address that appears after `default via`.
```sh title="On your Pi"
ip r
default via [IP]
```
Get the IP of your DNS server (it may or may not be your router)
```sh title="On your Pi"
grep nameserver /etc/resolv.conf
```

Open this file:
```sh title="On your Pi"
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

### To set it up as a DNS server
0. Install and configure a DNS Server e.g. DNSmasq or Pi-Hole on the Pi.
1. Change your router’s DNS settings to point to the Pi. Log in to your router's admin interface and look for DNS e.g. in **LAN** -> **DHCP Server**. Set the primary DNS server to the IP of your Pi and make sure it's the only DNS server. The Pi will handle upstream DNS services.


### Copying files

To copy files between the Pi and local machine
```sh title="On your laptop"
scp -r pi@raspberrypi2.local:/home/pi/Documents/ ~/Documents/pidocs
```

### Find info about your Pi

You can find info about the hardware like ports, pins, RAM, SoC, connectivity, etc. with:
```sh title="On your Pi"
free -h # RAM
df -h # storage space
pinout # requires `apt install python3-gpiozero`
```

View number of processing units and [system load](https://www.digitalocean.com/community/tutorials/load-average-in-linux#)
```sh title="On your Pi"
nproc
uptime
```

[CPU temperature](https://www.kernel.org/doc/Documentation/thermal/sysfs-api.txt) in millidegree Celsius (one thousandth of a degree)
```sh title="On your Pi"
cat /sys/class/thermal/thermal_zone*/temp
```
On the Orange Pi
```sh title="On your Pi"
# For CPU and GPU
sensors
# For NVMe SSD
sudo smartctl -a /dev/nvme0 | grep "Temperature:"
```

What model do you have?
```sh title="On your Pi"
cat /sys/firmware/devicetree/base/model ;echo
```

What's the connection speed of the ethernet port?
```sh title="On your Pi"
ethtool eth0
```

32 or 64-bit kernel?
```sh title="On your Pi"
getconf LONG_BIT
# or check machine's hardware name: armv7l is 32-bit and aarch64 is 64-bit
uname -m
```

See OS version
```sh title="On your Pi"
cat /etc/os-release
```

Architecture    
If the following returns a `Tag_ABI_VFP_args` tag of `VFP registers`, it's an `armhf` (`arm`) system.  
A blank output means `armel` (`arm/v6`).
```sh title="On your Pi"
readelf -A /proc/self/exe | grep Tag_ABI_VFP_args
```
Or check the architecture with:
```sh title="On your Pi"
hostnamectl
```

### Troubleshooting

If your Pi's ethernet port is capable of 1Gbps, you're using a cat5e cable or better, your router and switch support 1Gbps,  and you're still only getting 100Mbps **first try with another cable**. A faulty cable is the most common cause of problems like this. If that doesn't work you can try disabling EEE (Energy Efficient Ethernet) although it will be reenabled at reboot. You could also try setting the speed manually.
```sh title="On your Pi"
ethtool --show-eee eth0
sudo ethtool --set-eee eth0 eee off

# set speed manually and disable autonegotiation
ethtool -s eth0 speed 1000 duplex full autoneg off
```

If not using `cloud-init` or an imager program, enable ssh with
```sh title="On your Pi"
touch /Volumes/$VOLUME/ssh
```

DNS issues
```sh title="On your Pi"
cat /etc/resolv.conf
resolvectl status
```

### Learn about electronics

I've added some sample code from the [MagPi Essentials book](https://magpi.raspberrypi.com/books/essentials-gpio-zero-v1).  
[Sample code](https://github.com/santisbon/reference/tree/main/assets/SBC)

#### GPIO Header

![GPIO](https://i.imgur.com/3Zroadt.jpg)
