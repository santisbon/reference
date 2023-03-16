# Raspberry Pi
## Setup

1. Write and preconfigure Raspberry Pi OS on the SD card using Raspberry Pi Imager (`brew install --cask raspberry-pi-imager`). Make sure you use the correct version of the OS (32-bit or 64-bit).  
    1.1. Change the default password for the `pi` user.  
    1.2. Enable SSH (password or ssh keys).  
    1.3. Configure WiFi if needed.  
    1.4. Take note of the hostname.  
2. Insert the SD card in your Raspberry Pi and turn it on. 

If you didn't do so during setup, you can still generate and add an ssh key at any time. Example:
```zsh title="on your laptop"
ssh-keygen
ssh-copy-id -i ~/.ssh/id_rsa pi@raspberrypi4.local
```
To remove password authentication:
```zsh title="on the Pi"
sudo nano /etc/ssh/sshd_config
```
and replace `#PasswordAuthentication yes` with `PasswordAuthentication no`.
Test the validity of the config file and restart the service (or reboot).
```zsh
sudo sshd -t
sudo service sshd restart
sudo service sshd status
```

## Configuration

Find the IP of your Raspberry Pi using its hostname or find all devices on your network with `arp -a`.
```zsh
arp raspberrypi4.local 
```
SSH into it with the `pi` user and the IP address or hostname. Examples:
```zsh
ssh pi@192.168.xxx.xxx
ssh pi@raspberrypi4.local
# You'll be asked for the password if applicable
```

Configure it.
```zsh
pi@raspberrypi4:~ $ sudo raspi-config
# Go to Interface Options, VNC (for graphical remote access)
# Tab to the Finish option and reboot.
```
Update it.  
`upgrade` is used to install available upgrades of all packages currently installed on the system. New packages will be installed if required to satisfy dependencies, but existing packages will never be removed. If an upgrade for a package requires the removal of an installed package the upgrade for this package isn't performed.  
`full-upgrade` performs the function of upgrade but will remove currently installed packages if this is needed to upgrade the system as a whole.
```zsh
pi@raspberrypi4:~ $ sudo apt update # updates the package list
pi@raspberrypi4:~ $ sudo apt full-upgrade
```
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
`inform` means that the Raspberry Pi will attempt to get the IP address you requested, but if it's not available, it will choose another. If you use `static`, it will have no IP v4 address at all if the requested one is in use.  

Save the file and `sudo reboot`. From now on, upon each boot, the Pi will attempt to obtain the static ip address you requested.  

You could also set your router to manually assign the static IP to the Raspberry Pi under its DHCP settings e.g. LAN, DHCP server.

## To set it up as a DNS server
1. Install and configure a DNS Server e.g. DNSmasq or Pi-Hole on the Raspberry Pi.
2. Change your router’s DNS settings to point to the Raspberry Pi. Log in to your router's admin interface and look for DNS e.g. in LAN, DHCP Server. Set the primary DNS server to the IP of your Raspberry Pi and make sure it's the only DNS server. The Raspberry Pi will handle upstream DNS services.

## Remote GUI access

Now you'll need a VNC viewer on your laptop to connect to the Raspberry Pi using the graphical interface.
```zsh
brew install --cask vnc-viewer
```

Apparently, on Raspberry Pi pip does not download from the python package index (PyPi), it downloads from PiWheels. PiWheels wheels do not come with pygame's dependencies that are bundled in normal releases.

Install Pygame [dependencies](https://www.piwheels.org/project/pygame/) and Pygame.
```zsh
pi@raspberrypi4:~ $ sudo apt install libvorbisenc2 libwayland-server0 libxi6 libfluidsynth2 libgbm1 libxkbcommon0 libopus0 libwayland-cursor0 libsndfile1 libwayland-client0 libportmidi0 libvorbis0a libopusfile0 libmpg123-0 libflac8 libxcursor1 libxinerama1 libasyncns0 libxrandr2 libdrm2 libpulse0 libxfixes3 libvorbisfile3 libmodplug1 libxrender1 libsdl2-2.0-0 libxxf86vm1 libwayland-egl1 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libjack0 libsdl2-mixer-2.0-0 libinstpatch-1.0-2 libxss1 libogg0
pi@raspberrypi4:~ $ sudo pip3 install pygame
```

Check that the installation worked by running one of its demos
```zsh
pi@raspberrypi4:~ $ python3 -m pygame.examples.aliens
```

## Copy files

Copy files between Pi and local machine. On local machine run:
```zsh
scp -r pi@raspberrypi2.local:/home/pi/Documents/ ~/Documents/pidocs
```

## Find info about your Pi

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

## Learn about electronics

I've added some sample code from the [MagPi Essentials book](https://magpi.raspberrypi.com/books/essentials-gpio-zero-v1).  
[Sample code](https://github.com/santisbon/guides/tree/main/assets/raspberrypi)

### GPIO Header

![GPIO](https://i.imgur.com/3Zroadt.jpg)


