# Install utilities
These will vary for each person. Some examples on a Mac:  

```Shell
brew install wget
brew install gcc
brew install jq
brew install --cask docker
brew install kompose # translate Docker Compose files to Kubernetes resources
brew install --cask 1password
brew install --cask nordvpn
brew install --cask google-chrome # or chromium
brew install --cask firefox
brew install --cask visual-studio-code # or vscodium 
brew install --cask kindle
brew install --cask authy
brew install --cask teamviewer
brew install --cask raspberry-pi-imager
brew install --cask balenaetcher # to make bootable media
brew install --cask zoom
brew install --cask spotify
brew install --cask whatsapp
brew install --cask messenger # Facebook messenger
brew install --cask rectangle # to snap windows
brew install --cask avast-security # if it fails, download from website
brew install --cask handbrake # if you need to rip DVDs
brew install --cask virtualbox # currently Intel Macs only. ARM installer in beta.
brew install --cask multipass # run Ubuntu VMs in a local mini-cloud.
brew install --cask steam # if you want games
brew tap homebrew/cask-drivers # add repository of drivers
brew install logitech-options # driver for Logitech mouse
```

On macOS you can also install gcc by installing the xcode developer tools if you're not using Homebrew.
```Shell
xcode-select -v # check if tools are installed
xcode-select --install
```
