# Shell

## Touch ID for `sudo`

```sh
sudo nano /etc/pam.d/sudo
```
Add this as the second line of the file under the comment:
```sh
auth       sufficient     pam_tid.so
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

### [Oh My Zsh](https://ohmyz.sh/)  

#### Plugins

Add any built-in [plugins](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins) you need to your `~/.zshrc`
```zsh
plugins=(git macos python)
```

You can also add custom plugins by cloning the repo into the `$ZSH_CUSTOM/plugins/` directory and adding it to the plugins list in `~/.zshrc` or with Homebrew. 

The [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) plugin auto suggests previous commands. 
```zsh
brew install zsh-autosuggestions
# To activate, add this to your ~/.zshrc:
source $(brew --prefix)/share/zsh-autosuggestions/zsh-autosuggestions.zsh
```

The [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) plugin highlights valid commands green and invalid ones red so you don't have to test the command to see if it will work.
```zsh
brew install zsh-syntax-highlighting
# To activate, add this to your ~/.zshrc:
source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
```

#### Themes

Some Oh My Zsh themes like [Spaceship](https://spaceship-prompt.sh/) have font requirements.  
You can install fonts with Homebrew by adding the fonts repository. [Fira Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) is a good one for programming and computer science.
```zsh
brew tap homebrew/cask-fonts
brew install --cask font-fira-code
```

Or get a ton of fonts with:
```zsh
git clone https://github.com/powerline/fonts.git --depth=1
./fonts/install.sh
rm -rf fonts
```

Install your Oh My Zsh theme e.g. Spaceship (requires at least the Fire Code font)
```zsh
brew install spaceship
# If the theme is not copied to your themes folder, sim link from the Homebrew dir to your custom themes folder e.g.
ln -sf $(brew --prefix)/Cellar/spaceship/4.4.1/spaceship.zsh $ZSH_CUSTOM/themes/spaceship.zsh-theme

touch ~/.spaceshiprc.zsh
```

Any time you edit your zsh configuration file you can reload it to apply changes.
```zsh
source ~/.zshrc
```

Verify that you're using the shell you want. In the output of the `env | grep zsh` command look for something like `/opt/homebrew/bin/zsh`.

## Bash
If you want to use bash
```zsh
brew install bash # get the latest version of bash
chsh -s $(which bash)
nano ~/.bash_profile 
```

## Terminal app replacement
You can use [iTerm](https://iterm2.com/index.html) or [Warp](https://docs.warp.dev/getting-started/getting-started-with-warp)
```zsh
brew install --cask iterm2
brew install --cask warp
```

Install iTerm 2 color schemes
```zsh
git clone https://github.com/mbadolato/iTerm2-Color-Schemes.git
cd iTerm2-Color-Schemes

# Import all color schemes
tools/import-scheme.sh schemes/*
```

Set your iTerm preferences like default shell, font e.g. Fira Code, and colors:  
iTerm2 > Settings > Profiles > Colors > Color Presets  