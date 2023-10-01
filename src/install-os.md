# Do a clean install of the OS

On macOS download the new version from System Preferences, Software Update (or the Mac App Store) and create the bootable media with:
```zsh
sudo /Applications/Install\ macOS\ Sonoma.app/Contents/Resources/createinstallmedia --volume /Volumes/MyVolume/
```
using the volume that matches the name of the external drive you are using.  

To install macOS from a bootable installer:

1. Plug in your bootable media.
2. Turn off your Mac.
3. Depending on your CPU:
    1. If you have an Apple silicon Mac press ++power++ to turn on the Mac - but keep it pressed until you see the startup options window including your bootable volume.
    2. If you have an Intel-powered Mac press and hold ++option++ while the Mac starts up - keep pressing the key until you see a screen showing the bootable volume.
4. Use Disk Utility to erase the *Macintosh HD* volume group (not the individual system or data volumes), shut down, and start again launching the boot options for a clean install.