# Raspberry Pi  

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

### Upgrade

* `upgrade` is used to install available upgrades of all packages currently installed on the system. New packages will be installed if required to satisfy dependencies, but existing packages will never be removed. If an upgrade for a package requires the removal of an installed package the upgrade for this package isn't performed.  
* `full-upgrade` performs the function of upgrade but will remove currently installed packages if this is needed to upgrade the system as a whole.

```sh title="On your Pi"
sudo apt update # updates the package list
sudo apt full-upgrade
```

### Authentication

If you **didn't do so during setup with cloud-init or manually**, generate and add an ssh key.
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

### Board-specific tools

#### Raspberry Pi

On Raspberry Pi OS
```sh title="On your Pi"
sudo raspi-config
# Go to Interface Options, VNC (for graphical remote access)
# Tab to the Finish option and reboot.
```

#### Orange Pi

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

## Troubleshooting

* I see `cloud-init` had failures.  
    Based on the `user-data` file:
    Manually run `sudo apt update`, `sudo apt full-upgrade`.  
    Manually run `sudo apt install` on any packages that failed.  
    Manually add any kernel modules you need and make sure `/etc/modules-load.d/modules.conf` has them so they'll be added on every boot.
* I'm not sure cgroups are enabled.  
    Check with 
    ```sh
    cat /proc/cgroups
    ```