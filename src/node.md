# Node.js

**Install**

macOS  
Download the Node.js installer from https://nodejs.org/en/download/  
or
```zsh
brew install node
```

Linux  
```zsh
sudo apt install nodejs
sudo apt install npm
```

[Optional] Install nvm from https://github.com/creationix/nvm to manage multiple versions of node and npm.  

Windows Subsystem for Linux  
On WSL the recommended approach for installing a current version of Node.js is nvm.
```zsh
touch ~/.bashrc
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
# Reload your configuration
source ~/.bashrc
nvm install node
# Upgrade npm. You may need to run this twice on WSL.
npm install npm@latest -g
```

**Update npm**
If you installed npm as part of node you may need to update npm.
```zsh
sudo npm install -g npm
```

**Initialize a node project by creating a package.json**
```zsh
npm init
```

**Installing dependencies examples**
```zsh
sudo npm install --save ask-sdk moment
sudo npm install --save-dev mocha chai eslint virtual-alexa
```
**Troubleshooting mocha**
If you get an error running mocha tests e.g. `node_modules/.bin/mocha` not having execute permissions or *mocha Error: Cannot find module './options'* delete your node_modules folder and `npm install`.

**Set up ESLint with a configuration file**
```zsh
eslint --init
# you may need to run it as:
# sudo ./node_modules/.bin/eslint --init
```