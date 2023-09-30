# Package manager 
## macOS
Get [Homebrew](https://brew.sh/), a package manager for macOS.
```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew doctor
```
You can use a more [detailed guide](https://mac.install.guide/homebrew/index.html) if needed.

## Linux
Depending on your distribution, you may have apt (Debian), yum (Red Hat), or zypper (openSUSE).

Many apps use a different distribution method like Snap or Flatpak.

### [Snap](https://snapcraft.io/docs)

If you need to install a snap and your distro doens't have snap pre-installed e.g. in a remote system with Raspberry Pi OS:
```zsh
sudo apt update
sudo apt install snapd
sudo reboot
# ...reconnect after reboot
sudo snap install core
```

### [Flatpak](https://flatpak.org)

Set up [instructions](https://flatpak.org/setup/) for your distribution.