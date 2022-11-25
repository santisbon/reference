# Raspberry Pi

1. Write and preconfigure Raspberry Pi OS on the SD card using Raspberry Pi Imager (```brew install --cask raspberry-pi-imager```). Make sure you use the correct version of the OS (32-bit or 64-bit).
   - Change the default password for the ```pi``` user.
   - Enable SSH (password or ssh keys).
   - Configure WiFi if needed.
   - Take note of the hostname.
2. Insert the SD card in your Raspberry Pi and turn it on. 
3. Find the ip of your Raspberry Pi using its hostname e.g.
```Shell
$ arp raspberrypi4.local # or find all devices on your network with arp -a
```
SSH into it with the ```pi``` user
```Shell
$ ssh pi@192.168.xxx.xxx
# You'll be asked for the password if applicable
```

32 or 64-bit kernel?
```Shell
getconf LONG_BIT
# or check machine's hardware name: armv7l is 32-bit and aarch64 is 64-bit
pi@raspberrypi4:~ $ uname -m
```

See Raspbian version
```Shell
cat /etc/os-release
```

Architecture    
If the following returns a ```Tag_ABI_VFP_args``` tag of ```VFP registers```, it's an ```armhf``` (```arm```) system.  
A blank output means ```armel``` (```arm/v6```).
```Shell
pi@raspberrypi2:~ $ readelf -A /proc/self/exe | grep Tag_ABI_VFP_args
```
Or check the architecture with:
```Shell
hostnamectl
```

Now you can configure it:
```Shell
pi@raspberrypi4:~ $ sudo raspi-config
# Go to Interface Options, VNC (for graphical remote access)
# Tab to the Finish option and reboot.
```
and update it:
```Shell
# Update the package list
pi@raspberrypi4:~ $ sudo apt update
# Upgrade your installed packages to their latest versions.
# full-upgrade is used in preference to a simple upgrade, as it also picks up any dependency changes that may have been made
pi@raspberrypi4:~ $ sudo apt full-upgrade
```

Now you'll need a VNC viewer on your laptop to connect to the Raspberry Pi using the graphical interface.
```Shell
$ brew install --cask vnc-viewer
```

Apparently, on Raspberry Pi pip does not download from the python package index (PyPi), it downloads from PiWheels. PiWheels wheels do not come with pygame's dependencies that are bundled in normal releases.

Install Pygame [dependencies](https://www.piwheels.org/project/pygame/) and Pygame. Check that the installation worked by running one of its demos:

```Shell
pi@raspberrypi4:~ $ sudo apt install libvorbisenc2 libwayland-server0 libxi6 libfluidsynth2 libgbm1 libxkbcommon0 libopus0 libwayland-cursor0 libsndfile1 libwayland-client0 libportmidi0 libvorbis0a libopusfile0 libmpg123-0 libflac8 libxcursor1 libxinerama1 libasyncns0 libxrandr2 libdrm2 libpulse0 libxfixes3 libvorbisfile3 libmodplug1 libxrender1 libsdl2-2.0-0 libxxf86vm1 libwayland-egl1 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libjack0 libsdl2-mixer-2.0-0 libinstpatch-1.0-2 libxss1 libogg0
pi@raspberrypi4:~ $ sudo pip3 install pygame
pi@raspberrypi4:~ $ python3 -m pygame.examples.aliens
```

Copy files from Pi to local machine. On local machine run:
```Shell
scp -r pi@raspberrypi2.local:/home/pi/Documents/ ~/Documents/pidocs
```
