# Setting up a new machine

## Table of Contents


* [Do a clean install of the OS](#do-a-clean-install-of-the-os)
* [Package manager](#package-manager)
   * [macOS](#macos)
   * [Linux](#linux)
* [Shell](#shell)
   * [Bash](#bash)
   * [Zsh](#zsh)
   * [Terminal replacement](#terminal-replacement)
* [Install utilities](#install-utilities)
* [Git](#git)
   * [Install](#install)
   * [Configure](#configure)
   * [Set up git autocompletion (bash)](#set-up-git-autocompletion-bash)
   * [Set up SSH key](#set-up-ssh-key)
* [Docker](#docker)
   * [Install](#install-1)
      * [macOS](#macos-1)
      * [Linux:](#linux-1)
   * [Use](#use)
      * [Architecture](#architecture)
      * [Examples](#examples)
* [Python](#python)
   * [Install Python, the pip Python package installer, and Setuptools](#install-python-the-pip-python-package-installer-and-setuptools)
      * [With Homebrew](#with-homebrew)
      * [Without Homebrew](#without-homebrew)
   * [Get the pep8 python style checker](#get-the-pep8-python-style-checker)
   * [Anaconda](#anaconda)
      * [Notebooks](#notebooks)
* [Raspberry Pi](#raspberry-pi)
* [Amazon Web Services](#amazon-web-services)
   * [AWS CLI](#aws-cli)
      * [Install the AWS command line interface](#install-the-aws-command-line-interface)
      * [Add the AWS CLI to your PATH](#add-the-aws-cli-to-your-path)
      * [Check if the AWS CLI is installed correctly](#check-if-the-aws-cli-is-installed-correctly)
      * [Configure the AWS CLI](#configure-the-aws-cli)
   * [Alexa Skills Kit (ASK) CLI](#alexa-skills-kit-ask-cli)
   * [AWS Amplify](#aws-amplify)
* [MySQL development](#mysql-development)
   * [Install MySQL Community Edition](#install-mysql-community-edition)
   * [Configure your PATH](#configure-your-path)
   * [Start the MySQL service](#start-the-mysql-service)
   * [Verify it's running](#verify-its-running)
   * [Connect to your MySQL instance](#connect-to-your-mysql-instance)
   * [To stop MySQL](#to-stop-mysql)
   * [Exporting data](#exporting-data)
* [Node.js](#nodejs)
   * [Install](#install-2)
   * [Update npm](#update-npm)
   * [Initialize a node project by creating a package.json](#initialize-a-node-project-by-creating-a-packagejson)
   * [Installing dependencies examples](#installing-dependencies-examples)
      * [Troubleshooting mocha](#troubleshooting-mocha)
   * [Set up ESLint with a configuration file](#set-up-eslint-with-a-configuration-file)

# Do a clean install of the OS

On macOS download the new version from System Preferences, Software Update and create the bootable media with:
```Shell
sudo /Applications/Install\ macOS\ Monterey.app/Contents/Resources/createinstallmedia --volume /Volumes/Untitled
```
where Untitled is the name of the external drive you are using.  

If you have an Intel-powered Mac here's how to install macOS from a bootable installer:
1. Plug in your bootable media.
2. Turn off your Mac.
3. Press and hold Option/Alt while the Mac starts up - keep pressing the key until you see a screen showing the bootable volume.

If you have an Apple silicon Mac here's how to install macOS from a bootable installer:
1. Plug in your bootable media.
2. Turn off your Mac.
3. Press the power button to turn on the Mac - but keep it pressed until you see the startup options window including your bootable volume.  

Open Finder and show hidden files with Command + Shift + . (period) or with
```Shell
defaults write com.apple.finder AppleShowAllFiles TRUE; killall Finder
```

# Package manager 

## macOS
Get [Homebrew](https://brew.sh/), a package manager for macOS.
```Shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew doctor
```
You can use a more [detailed guide](https://mac.install.guide/homebrew/index.html) if needed.
## Linux
Depending on your distribution, you may have apt (Ubuntu), yum (Red Hat), or zypper (openSUSE).

# Shell

## Bash
If you want to use bash
```Shell
brew install bash # get the latest version of bash
chsh -s $(which bash)
nano ~/.bash_profile # and paste from sample dot file
```

## Zsh

```zsh
brew install zsh # get the latest version

# You may need to add the Homebrew version of Zsh to the list on /etc/shells
sudo nano /etc/shells # add the output of "which zsh" to the top of the list, save the file.

where zsh # you might see both the shell that came with your Mac and the latest from Homebrew
which zsh # make sure this returns the one from Homebrew.

chsh -s $(which zsh)
# Install Oh My Zsh, a framework for managing your Zsh configuration with plugins and themes
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

[Oh My Zsh](https://ohmyz.sh/)  
Add any built-in [plugins](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins) you need to your ```~/.zshrc```
```Shell
plugins=(git macos python)
```

You can also add custom plugins by cloning the repo into the plugins directory or with Homebrew. 

This plugin [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) highlights valid commands green and invalid ones red so you don't have to test the command to see if it will work.
```Shell
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```
Or just use Homebrew:
```Shell
brew install zsh-syntax-highlighting
# To activate the syntax highlighting, add the following at the end of your ~/.zshrc:
source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

Some Oh My Zsh themes like [Spaceship](https://spaceship-prompt.sh/) have requirements like the Powerline Fonts. Get them with:
```Shell
git clone https://github.com/powerline/fonts.git --depth=1
./fonts/install.sh
rm -rf fonts
```

You can also install fonts with Homebrew by adding the fonts repository. [Fira Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) is a good one for programming and computer science.
```Shell
brew tap homebrew/cask-fonts
brew install --cask font-fira-code
```
Install your Oh My Zsh theme e.g. Spaceship
```Shell
brew install spaceship
# If the theme is not copied to your themes folder, sim link from the Homebrew dir to your custom themes folder e.g.
ln -sf $(brew --prefix)/Cellar/spaceship/4.2.0/spaceship.zsh $ZSH_CUSTOM/themes/spaceship.zsh-theme
```
Set ```ZSH_THEME="spaceship"``` in your ```.zshrc```.  

Any time you edit your zsh configuration file you can reload it to apply changes.
```Shell
source ~/.zshrc
```

## Terminal replacement
You can use [iTerm2](https://iterm2.com/index.html)
```Shell
brew install --cask iterm2
```

After you have installed the font(s) required by your Oh My Zsh theme set your iTerm preferences like default shell and font.  
Verify that you're using the shell you want. In the output of the ```env``` command look for something like ```SHELL=/opt/homebrew/bin/zsh```.

# Install utilities
These will vary for each person. Some examples on a Mac:  

```Shell
brew install wget
brew install gcc
brew install jq
brew install --cask docker
brew install --cask 1password
brew install --cask nordvpn
brew install --cask google-chrome # or chromium
brew install --cask firefox

brew install --cask vscodium 
# Q. VSCodium cannot be opened because Apple cannot check it for malicious software
# A. You have to "right click" the .app and then hold the alt/option key, while clicking "Open" (only on first launch).

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
brew install --cask virtualbox
brew install --cask steam # if you want games
brew tap homebrew/cask-drivers # add repository of drivers
brew install logitech-options # driver for Logitech mouse
```

On macOS you can also install gcc by installing the xcode developer tools if you're not using Homebrew.
```Shell
xcode-select -v # check if tools are installed
xcode-select --install
```

# Git

## Install

macOS  
```Shell
brew install git
git --version

# GitHub CLI
brew install gh 
gh auth login
gh config set editor "codium -w" # or code, nano, etc
```
GitHub CLI [reference](https://docs.github.com/en/github-cli/github-cli/github-cli-reference).

Linux
```Shell
sudo yum install git # or git-all
git --version
```

## Configure
```Shell
git config --global core.editor 'codium --wait'

git config --global diff.tool codium
git config --global difftool.codium.cmd 'codium --wait --diff $LOCAL $REMOTE'

git config --global merge.tool codium
git config --global mergetool.codium.cmd 'codium --wait $MERGED'

# or
codium ~/.gitconfig # and paste from sample dot file. Also: codium, vscode, nano
```

Then you can ```git difftool main feature-branch```.  

If using AWS CodeCommit do this after configuring the AWS CLI:
```Shell
git config --global credential.helper '!aws codecommit credential-helper $@'
git config --global credential.UseHttpPath true
```
Troubleshooting CodeCommit  
https://docs.aws.amazon.com/codecommit/latest/userguide/troubleshooting-ch.html#troubleshooting-macoshttps

## Set up git autocompletion (bash)

```bash
cd ~
curl -OL https://github.com/git/git/raw/master/contrib/completion/git-completion.bash
mv ~/git-completion.bash ~/.git-completion.bash
```

## Set up SSH key
1. [Check](https://help.github.com/articles/checking-for-existing-ssh-keys/) for existing keys.
2. [Generate](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/) a new SSH key and add it to ssh-agent. You may need to set permissions to your key file with ```chmod 600```.
3. [Add](https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/) the public key to your GitHub account.

If the terminal is no longer authenticating you:
```
git remote -v # is it https or ssh? Should be ssh
git remote remove origin
git remote add origin git@github.com:user/repo.git
```
Still having issues? Start the ssh-agent in the background and add your SSH private key to the ssh-agent.
```Shell
ps -ax | grep ssh-agent
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```
If you need to add your public key to Github again copy and paste it on your Settings page on Github:
```
pbcopy < ~/.ssh/id_ed25519.pub
```

# Docker

## Install

### macOS
```Shell
brew install --cask docker
```
* You must use the --cask version. Otherwise only the client is included and can't run the Docker daemon. Then open the Docker app and grant privileged access when asked. Only then will you be able to use docker.

### Linux:  
```Shell
curl https://get.docker.com > /tmp/install.sh
chmod +x /tmp/install.sh
/tmp/install.sh
```

If you don't want to have to prefix commands with sudo add your user to the `docker` group. This is equivalent to giving that user root privileges.
```Shell
sudo usermod -aG docker
```

On Ubuntu this may mess up DNS resolution. To fix it: (To-Do).

## Use

### Architecture

[Supported Architectures](https://github.com/docker-library/official-images#architectures-other-than-amd64)  

[Platform specifiers](https://github.com/containerd/containerd/blob/v1.4.3/platforms/platforms.go#L63)  

| Value   | Normalized |                 | 
| :-----: | :--------: | :-------------: |
| aarch64 | arm64      | M1/M2           |
| armhf   | arm        |                 |
| armel   | arm/v6     |                 |   
| i386    | 386        |                 |
| x86_64  | amd64      | Default (Intel) |
| x86-64  | amd64      | Default (Intel) |

Docker Desktop for Apple silicon can run (or build) an Intel image using emulation.  
The ```--platform``` option sets the platform if server is multi-platform capable.  

Macbook **M1/M2** is based on **ARM**. The Docker host is detected as **linux/arm64/v8** by Docker.  

On a Macbook M1/M2 running a native arm64 linux image instead of an amd64 (x86-64 Intel) image with emulation:  
When installing apps on the container either install the package for the ARM platform if they provide one, or run an amd64 docker image (Docker will use emulation). 

See Docker host info.  
You need to use the real field names (not display names) so we'll grab the info in json to get the real field names and use ```jq``` to display it nicely. Then we'll render them using Go templates.

```Shell
docker info --format '{{json .}}' | jq .

docker info --format "{{.Plugins.Volume}}"
docker info --format "{{.OSType}} - {{.Architecture}} CPUs: {{.NCPU}}"
```

With the default images, Docker Desktop for Apple silicon warns us the requested image's platform (linux/amd64) is different from the detected host platform (linux/arm64/v8) and no specific platform was requested.  
```--platform linux/amd64``` is the default and the same as  ```--platform linux/x86_64```. It runs (or builds) an Intel image.  
```--platform linux/arm64``` runs (or builds) an aarch64 (arm64) image. Architecture used by Appple M1/M2.  

```Shell
docker run -it --name container1 debian # WARNING. uname -m -> x86_64 (amd64)
docker run -it --platform linux/amd64 --name container1 debian # NO warning. uname -m -> x86_64 (amd64). On Mac it emulates Intel.
docker run -it --platform linux/arm64 --name container1 debian # NO warning. uname -m -> aarch64 (arm64). Mac native.

# On a Mac M2 you can also use this image
docker run -it --name mycontainer arm64v8/debian bash # NO warning. uname -m -> aarch64 (arm64). Mac native.
```


### Examples
```Shell
# sanity check
docker version
docker --help

# "docker run" = "docker container run"

docker run --name container1 debian # created and Exited
docker run -it --name container2 debian # created and Up. Interactive tty
docker run --detach --name container3 debian # created and Exited
docker run -it --detach --name container4 debian # created and Up. Running in background

docker stop container4 # Exited
docker restart container4 # Up
docker attach container4 # Interactive tty

# To have it removed automatically when it's stopped 
docker run -it --rm --name mycontainer debian # created and Up. Interactive tty. 

# Run bash in a new container with interactive tty, based on debian image.
docker run -it --name mycontainer debian bash
```

```Shell

# Show all images (including intermediate images)
docker image ls -a

# Get the IDs of all stopped containers. Options: all, quiet (only IDs), filter.
docker ps -aq -f status=exited

# Build an image from a Dockerfile and give it a name (or name:tag).
docker build -f mydockerfile -t santisbon/myimage .
docker builder prune -a		# Remove all unused build cache, not just dangling ones

# Start a container from an image.
docker run \
--name mycontainer \
--hostname mycontainer \
--mount source=my-vol,target=/data \
santisbon/myimage

# Volumes
docker volume create my-vol
docker volume ls
docker volume inspect my-vol

docker volume prune
docker volume rm my-vol

# Get rid of all stopped containers. Options: remove **anonymous volumes** associated with the container.
docker rm -v $(docker ps -aq -f status=exited)
# You might want to make an alias:
alias drm='docker rm -v $(docker ps -aq -f status=exited)'
# or
alias drm='sudo docker rm -v $(sudo docker ps -aq -f status=exited)'

# on macOS the volume mountpoint (/var/lib/docker/volumes/) is in the VM that Docker Desktop uses to provide the Linux environment.
# You can read it through a container given extended privileges. 
# Use: 
# - the "host" PID namespace, 
# - an image e.g. debian, 
# - the nsenter command to run a program (sh) in a different namespace
# - the target process with PID 1
# - enter following namspaces of the target process: mount, UTS, network, IPC.
docker run -it --privileged --pid=host debian nsenter -t 1 -m -u -n -i sh
```

# Python

## Install Python, the pip Python package installer, and Setuptools
### With Homebrew
Even if you already have Python on your OS it might be an outdated version. This installs python and pip.  
macOS
```Shell
brew install python
python3 --version
```
The python formulae install pip (as pip3) and Setuptools. Setuptools can be updated via pip3 and pip3 can be used to upgrade itself.
```Shell
python3 -m pip install --upgrade setuptools
python3 -m pip install --upgrade pip
```
Add the unversioned symlinks to your ```$PATH``` by adding this to your ```.zshrc``` file.
```Shell
export PATH="$(brew --prefix)/opt/python/libexec/bin:$PATH"
```
See the [Homebrew Python](https://docs.brew.sh/Homebrew-and-Python) documentation for details.  

### Without Homebrew
Linux (Ubuntu)
```Shell
sudo apt install python3
```

macOS  
Download .pkg installer from pythong.org. Then get pip.
```Shell
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
```

Linux
```Shell
sudo apt install python-pip
```

```Shell
pip install --upgrade pip setuptools
```
On Ubuntu, upgrading to pip 10 may break pip. If this happens you need to:
```Shell
sudo nano /usr/bin/pip
# change "from pip import main" to "from pip._internal import main"
```

## Get the pep8 python style checker
```Shell
# On Linux you may need to use sudo.
pip install pep8
```

## Anaconda
For data science and machine learning. [Anaconda](https://docs.anaconda.com/anaconda/) is a distribution of the Python and R programming languages for scientific computing. See [Getting Started](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html).
```Shell
brew install --cask anaconda
```

[Installing in silent mode](https://docs.anaconda.com/anaconda/install/silent-mode/)  

Add anaconda to your ```PATH``` on your ```.zshrc``` and ```source ~/.zshrc``` to apply the changes.
```Shell
export PATH="$(brew --prefix)/anaconda3/bin:$PATH"
```
To use zsh:
```Shell
conda init zsh
```
If ```conda init zsh``` messed up the ```PATH``` in your ```~/.zshrc``` by adding the ```condabin``` directory instead of ```bin``` you can fix it with a symlink:
```Shell
ln -sf $(brew --prefix)/anaconda3/bin/jupyter-lab $(brew --prefix)/anaconda3/condabin/jupyter-lab
ln -sf $(brew --prefix)/anaconda3/bin/jupyter $(brew --prefix)/anaconda3/condabin/jupyter
```

If you don't want to activate the ```base``` environment every time you open your terminal:
```Shell
conda config --set auto_activate_base false
```

When creating a conda environment you can use optionally use a configuration file. You can also of course, save a config file from an existing environment to back it up.
```Shell
conda env create -f myenv.yml
conda activate myenv

conda env list
conda env remove --name ldm
```

### Notebooks
Fresh installs of Anaconda no longer include notebook extensions in their Jupyter installer. This means that the nb_conda libraries need to be added into your environment separately to access conda environments from your Jupyter notebook. Just run these to add them and you should be able to select your environment as a kernel within a Jupyter notebook.
```Shell
conda activate <myenv>
conda install ipykernel
conda install nb_conda_kernels # or defaults::nb_conda_kernels
```

Now you can launch the new JupyterLab or the classic Jupyter Notebook.
```Shell
jupyter-lab # or the classic "jupyter notebook"
```

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

# You can check which version of the OS you're running with the machine's hardware name
# armv7l is 32-bit and aarch64 is 64-bit
pi@raspberrypi4:~ $ uname -m
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

# Amazon Web Services

## AWS CLI

### Install the AWS command line interface
```Shell
sudo pip install --upgrade --user awscli
```

### Add the AWS CLI to your PATH
macOS  
Only if it's not already on your ~/.bash_profile e.g. ~/Library/Python/2.7/bin
```Shell
export PATH=~/Library/Python/2.7/bin:$PATH
```
Linux  
If not on your ~/.bashrc
```Shell
export PATH=~/.local/bin:$PATH
```

### Check if the AWS CLI is installed correctly
```Shell
# you may need to reload your config with "source ~/.bashrc" on Linux (or ~/.bash_profile on macOS)
aws --version
```

If you get a permission denied error on macOS, make yourself the owner 
```Shell
sudo chown -R $USER ~/Library/Python
```

### Configure the AWS CLI
```Shell
aws configure
```

## Alexa Skills Kit (ASK) CLI
https://developer.amazon.com/docs/smapi/set-up-credentials-for-an-amazon-web-services-account.html  
https://developer.amazon.com/docs/smapi/quick-start-alexa-skills-kit-command-line-interface.html

## AWS Amplify
```Shell
npm install -g @aws-amplify/cli
amplify configure
```

# MySQL development

## Install MySQL Community Edition 
Use your OS package manager or download .dmg installer for macOS. Take note of the root password.

## Configure your PATH
Add the mysql location to your PATH. Typically as part of your ~/.bash_profile
```Shell
export PATH=/usr/local/mysql/bin:$PATH
```

## Start the MySQL service
On macOS
```Shell
sudo launchctl load -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist
```

## Verify it's running
On macOS
```Shell
sudo launchctl list | grep mysql
```

## Connect to your MySQL instance
Use MySQL Workbench or other client tool.

## To stop MySQL
On macOS
```Shell
sudo launchctl unload -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist
```

## Exporting data
If you need to export data you may need to disable or set a security setting. On macOS:

View the variable using your SQL client. If it's NULL you will be restricted regarding file operations.
```sql
show variables like 'secure_file_priv';
```

Open the configuration file.
```Shell
cd /Library/LaunchDaemons
sudo nano com.oracle.oss.mysql.mysqld.plist
```
and set the --secure-file-priv to an empty string (to disable the restriction) or a dir of your choice.
```xml
<key>ProgramArguments</key>
    <array>
        <string>--secure-file-priv=</string>
    </array>
```

Then restart MySQL. Now you can export data:
```sql
SELECT *
INTO OUTFILE 'your_file.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
FROM `your_db`.`your_table`
```

You can find your exported data:
```Shell
sudo find /usr/local/mysql/data -name your_file.csv
```

# Node.js

## Install

macOS  
Download the Node.js installer from https://nodejs.org/en/download/  
or
```Shell
brew install node
```

Linux  
```Shell
sudo apt install nodejs
sudo apt install npm
```

[Optional] Install nvm from https://github.com/creationix/nvm to manage multiple versions of node and npm.  

Windows Subsystem for Linux  
On WSL the recommended approach for installing a current version of Node.js is nvm.
```Shell
touch ~/.bashrc
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
# Reload your configuration
source ~/.bashrc
nvm install node
# Upgrade npm. You may need to run this twice on WSL.
npm install npm@latest -g
```

## Update npm
If you installed npm as part of node you may need to update npm.
```Shell
sudo npm install -g npm
```

## Initialize a node project by creating a package.json
```Shell
npm init
```

## Installing dependencies examples
```Shell
sudo npm install --save ask-sdk moment
sudo npm install --save-dev mocha chai eslint virtual-alexa
```
### Troubleshooting mocha
If you get an error running mocha tests e.g. ```node_modules/.bin/mocha``` not having execute permissions or *mocha Error: Cannot find module './options'* delete your node_modules folder and ```npm install```.

## Set up ESLint with a configuration file
```Shell
eslint --init
# you may need to run it as:
# sudo ./node_modules/.bin/eslint --init
```