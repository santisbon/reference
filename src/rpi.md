# Single-board Computers (SBCs)
Raspberry Pi, Orange Pi, and many others.

![SBCs](https://res.cloudinary.com/practicaldev/image/fetch/s--gU1esoW1--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_800/https://dev-to-uploads.s3.amazonaws.com/uploads/articles/k1mer6vmt81awg37l856.png)

## Get OS image

You *could* use an imager program that flashes an operating system on the SD card for you but you'll be very limited in the ways you can preconfigure the OS. It's better to download the OS image and flash it yourself.  
   
I recommend using an **Ubuntu** image made specifically for your board instead of a manufaturer's custom OS like Raspberry Pi OS or Orange Pi OS. Those are designed for simplicity and ease of use at the expense of functionality that will be important to us when building our homelab as a private cloud.

* ❌ Raspberry Pi OS doesn't come with [`cloud-init`](https://cloud-init.io).
* ❌ Orange Pi OS doesn't support the GPU, Neural Processing Unit (NPU), and Vision Processing Unit (VPU) that some Orange Pi boards have for Artificial Intelligence and graphics-intensive workloads.
* ✅ Ubuntu comes with `cloud-init` preinstalled which will make your life easier.
* ✅ Ubuntu comes with [`snapd`](https://ubuntu.com/core/services/guide/snaps-intro) preinstalled which lets us preconfigure [MicroK8s](https://microk8s.io).
* ✅ Ubuntu, Debian, and Android support the Orange Pi's GPU, NPU, and VPU.

Make sure you grab the *Server* image corresponding to your Pi's architecture (32-bit or 64-bit). We choose the server version because we don't need the graphical environment that comes with the *Desktop* version.  

Official Ubuntu images for all Raspberry Pis (recommended):  
[Download](https://ubuntu.com/download/raspberry-pi)  
[Checksums](https://github.com/canonical/ubuntu.com/blob/main/releases.yaml)

Manufacturer's images for Orange Pi 3B:  
*For some reason, an SD card flashed with the Ubuntu image provided by Orange Pi can't be mounted on macOS. We need to mount it to inject or edit files before first boot if we want to automate the setup as much as possible. For this reason, if you're setting up an Orange Pi download the image and see the [one-off](#set-up-a-one-off) instructions*.  
[Download](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-3B.html)  

Examples of verifying the integrity of the image file:
```sh
# Extract and verify
7zz x Orangepi3b_1.0.0_ubuntu_jammy_server_linux5.10.160.7z
shasum -c Orangepi3b_1.0.0_ubuntu_jammy_server_linux5.10.160.img.sha

# Verify it matches the hash on the website and decompress
echo "f3842efb3be1be4243c24203bd16e335f155fdbe104b1ed8c5efc548ea478ab0 *ubuntu-22.04.3-preinstalled-server-arm64+raspi.img.xz" | shasum -a 256 --check
xz -d ubuntu-22.04.3-preinstalled-server-arm64+raspi.img.xz
```

## Set up a cloud native homelab 
This is the most flexible option.

!!! tip
    This lets you automatically upgrade the system, configure users, modify boot parameters, specify software to install, custom commands to run on first boot, among other things. Recommended when setting up multiple Pis or installing Kubernetes.

### Flash pre-configured image

We'll flash the SD card with our `cloud-init` file and other configurations. This will set up `avahi-daemon` to be able to reach the Pi using its hostname rather than having to use its IP. It also installs a tool for viewing hardware info and MicroK8s.  

Replace values for your own environment (your [OS tools to copy/paste](https://ostechnix.com/how-to-use-pbcopy-and-pbpaste-commands-on-linux/), name of your [SSH key](https://www.ssh.com/academy/ssh/keygen), volume name, etc.).  

This example uses the macOS version of `sed` with an empty string for the mandatory extension parameter when editing a file in-place. It also uses [`pv`](https://formulae.brew.sh/formula/pv#default) to monitor data progress.  

These commands have been tested with the image provided by Ubuntu on a Raspberry Pi.  

```sh title="On your laptop" 
# Insert the SD card and find the corresponding device
diskutil list
# df -h

###################################################################
# REPLACE WITH YOUR VALUES
###################################################################
IMAGE=ubuntu-22.04.3-preinstalled-server-arm64+raspi.img
DEVICE=/dev/mydevice # e.g. /dev/disk4

HOSTNAME=orangepi3
LOCALE=en_US
TIMEZONE=US/Central

COUNTRY=US
WIFI_NAME=myssid
WIFI_PASSWORD='mypassword'

pbcopy < ~/.ssh/id_ed25519.pub
KEY=$(pbpaste)
###################################################################

# Unmount the card
diskutil unmountDisk $DEVICE

# You can use `dd` by itself
sudo dd if=$IMAGE of=$DEVICE bs=1m status=progress
# or to get a progress bar and percentage, use `pv` through a pipe
pv $IMAGE | sudo dd bs=1m of=$DEVICE

# When it's done you'll see a volume mounted on your desktop 
# called `boot`, `bootfs`, `system-boot` or something similar.
# You can also mount it manually. Example:
# diskutil mountDisk /dev/disk4

###################################################################
# REPLACE WITH YOUR VALUES
###################################################################
VOLUME=system-boot
###################################################################

# enable Wi-Fi if applicable
cat << EOF > /Volumes/$VOLUME/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=${COUNTRY}
network={
ssid=${WIFI_NAME}
psk=${WIFI_PASSWORD}
}
EOF

# check that it worked
# cat /Volumes/$VOLUME/wpa_supplicant.conf

# create file for `cloud-init`
cat << EOF > /Volumes/${VOLUME}/user-data
#cloud-config

hostname: ${HOSTNAME}
manage_etc_hosts: true
locale: ${LOCALE}
timezone: ${TIMEZONE}

users:
  - name: pi
    lock_passwd: true
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ${KEY}

package_upgrade: true
packages:
  - avahi-daemon 
  - lshw

runcmd:
  - [snap install microk8s --classic]
EOF

# cat /Volumes/${VOLUME}/user-data

# Add these options at the end of the file as Kubernetes will need them to run on the Pi.
sed -i "" "$ s/$/ cgroup_enable=memory cgroup_memory=1/" /Volumes/$VOLUME/cmdline.txt
# cat /Volumes/$VOLUME/cmdline.txt

diskutil unmountDisk $DEVICE
# remove SD card from laptop, insert it in your Pi and turn it on
```

Since we preconfigured everything it has a lot of work to do before it can be available including upgrading the system and installing packages. Wait at least 20 minutes before trying to connect to it via SSH. 

## Set up a one-off 

### Flash the stock image

!!! tip
    This is the easiest option but is limited in how much you can preconfigure the OS. Recommended if you're setting up only one Pi and don't need to install Kubernetes or anything else that requires modified boot parameters.

Use Raspberry Pi Imager (`brew install --cask raspberry-pi-imager`) to:  

* Change the password for the default user or disable passwords altogether.  
* Enable SSH (password or ssh keys); remove password authentication if using keys.  
* Configure Wi-Fi if needed.  
* Set the hostname.  

!!! attention
    If you flash a different type of image (like an Orange Pi image) using the Raspberry Pi Imager, the pre-configurations you entered on the tool won't take effect. You'll still have to configure it manually.

### Access your Pi

If you're **reinstalling** the OS you might need to remove old key fingerprints belonging to that hostname from your `known_hosts` file. Example:
```zsh title="On your laptop"
ssh-keygen  -f ~/.ssh/known_hosts -R raspberrypi4.local
```

Find the IP of your Pi using its hostname or find all devices on your network with `arp -a`.
```zsh title="On your laptop"
arp raspberrypi4.local 
```
SSH into it with the configured user e.g. `pi` and the IP address or hostname. Examples:
```zsh title="On your laptop"
ssh pi@raspberrypi4.local
# or
ssh pi@192.168.xxx.xxx

# Logs are located here
ls -al /var/log
# Example
sudo cat /var/log/cloud-init.log
```

### Upgrade

* `upgrade` is used to install available upgrades of all packages currently installed on the system. New packages will be installed if required to satisfy dependencies, but existing packages will never be removed. If an upgrade for a package requires the removal of an installed package the upgrade for this package isn't performed.  
* `full-upgrade` performs the function of upgrade but will remove currently installed packages if this is needed to upgrade the system as a whole.

```zsh
pi@raspberrypi4:~ $ sudo apt update # updates the package list
pi@raspberrypi4:~ $ sudo apt full-upgrade
```

### Configure

Make the board reachable using its hostname, not only its IP. Also install tool to view hardware info.
```zsh
sudo apt install avahi-daemon lshw
```

#### Authentication

If you **didn't do so during setup**, you can still generate and add an ssh key at any time. Example:
```zsh title="On your laptop"
ssh-keygen
ssh-copy-id -i ~/.ssh/id_rsa pi@raspberrypi4.local
```
To remove password authentication:
```zsh title="on the Pi"
sudo nano /etc/ssh/sshd_config
```
and replace `#PasswordAuthentication yes` with `PasswordAuthentication no`.
Test the validity of the config file and restart the service (or reboot).
```zsh title="on the Pi"
sudo sshd -t
sudo service sshd restart
sudo service sshd status
```

#### Board-specific tools

Once you're on the SBC, configure it if needed.
```zsh
pi@raspberrypi4:~ $ sudo raspi-config
# Go to Interface Options, VNC (for graphical remote access)
# Tab to the Finish option and reboot.
```

Orange Pi has a config tool as well
```zsh
orangepi@orangepi3b:~$ sudo orangepi-config
```

#### Other
After this, [install MicroK8s](/reference/k8s/#microk8s).

### Remote GUI access
*If you installed a graphical desktop*

You'll need a VNC viewer on your laptop to connect to the Pi using the graphical interface.
```zsh
brew install --cask vnc-viewer
```

!!! attention
    Apparently, on Raspberry Pi `pip` does not download from the Python Package Index (PyPI), it downloads from PiWheels. PiWheels wheels do not come with `pygame`'s dependencies that are bundled in normal releases.

    Install Pygame [dependencies](https://www.piwheels.org/project/pygame/) and Pygame.
    ```zsh
    pi@raspberrypi4:~ $ sudo apt install libvorbisenc2 libwayland-server0 libxi6 libfluidsynth2 libgbm1 libxkbcommon0 libopus0 libwayland-cursor0 libsndfile1 libwayland-client0 libportmidi0 libvorbis0a libopusfile0 libmpg123-0 libflac8 libxcursor1 libxinerama1 libasyncns0 libxrandr2 libdrm2 libpulse0 libxfixes3 libvorbisfile3 libmodplug1 libxrender1 libsdl2-2.0-0 libxxf86vm1 libwayland-egl1 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libjack0 libsdl2-mixer-2.0-0 libinstpatch-1.0-2 libxss1 libogg0
    pi@raspberrypi4:~ $ sudo pip3 install pygame
    ```

    Check that the installation worked by running one of its demos
    ```zsh
    pi@raspberrypi4:~ $ python3 -m pygame.examples.aliens
    ```

## Usage

### To give it a static IP
Find the IP adddress of your router. It's the address that appears after `default via`.
```zsh
pi@raspberrypi4:~ $ ip r
default via [IP]
```
Get the IP of your DNS server (it may or may not be your router)
```zsh
pi@raspberrypi4:~ $ grep nameserver /etc/resolv.conf
```

Open this file:
```zsh
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

You could also set your router to manually assign the static IP to the Pi under its DHCP settings e.g. LAN, DHCP server.

### To set it up as a DNS server
0. Install and configure a DNS Server e.g. DNSmasq or Pi-Hole on the Pi.
1. Change your router’s DNS settings to point to the Pi. Log in to your router's admin interface and look for DNS e.g. in LAN, DHCP Server. Set the primary DNS server to the IP of your Pi and make sure it's the only DNS server. The Pi will handle upstream DNS services.


### Copying files

To copy files between the Pi and local machine
```zsh title="On your laptop"
scp -r pi@raspberrypi2.local:/home/pi/Documents/ ~/Documents/pidocs
```

### Find info about your Pi

What model do you have?
```zsh
cat /sys/firmware/devicetree/base/model ;echo
```

What's the connection speed of the ethernet port?
```zsh
ethtool eth0
```

32 or 64-bit kernel?
```zsh
getconf LONG_BIT
# or check machine's hardware name: armv7l is 32-bit and aarch64 is 64-bit
pi@raspberrypi4:~ $ uname -m
```

See OS version
```zsh
cat /etc/os-release
```

Architecture    
If the following returns a `Tag_ABI_VFP_args` tag of `VFP registers`, it's an `armhf` (`arm`) system.  
A blank output means `armel` (`arm/v6`).
```zsh
pi@raspberrypi2:~ $ readelf -A /proc/self/exe | grep Tag_ABI_VFP_args
```
Or check the architecture with:
```zsh
hostnamectl
```

You can find info about the hardware like ports, pins, RAM, SoC, connectivity, etc. with:
```zsh
pi@raspberrypi4:~ $ pinout
```

### Troubleshooting

If your Pi's ethernet port is capable of 1Gbps, you're using a cat5e cable or better, your router and switch support 1Gbps,  and you're still only getting 100Mbps **first try with another cable**. A faulty cable is the most common cause of problems like this. If that doesn't work you can try disabling EEE (Energy Efficient Ethernet) although it will be reenabled at reboot. You could also try setting the speed manually.
```zsh
ethtool --show-eee eth0
sudo ethtool --set-eee eth0 eee off

# set speed manually and disable autonegotiation
ethtool -s eth0 speed 1000 duplex full autoneg off
```

If not using `cloud-init` or an imager program, enable ssh with
```zsh
touch /Volumes/$VOLUME/ssh
```

DNS issues
```zsh
cat /etc/resolv.conf
resolvectl status
```

### Learn about electronics

I've added some sample code from the [MagPi Essentials book](https://magpi.raspberrypi.com/books/essentials-gpio-zero-v1).  
[Sample code](https://github.com/santisbon/guides/tree/main/assets/SBC)

#### GPIO Header

![GPIO](https://i.imgur.com/3Zroadt.jpg)
