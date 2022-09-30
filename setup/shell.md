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

This plugin auto suggests previous commands. 
```Shell
git clone https://github.com/zsh-users/zsh-autosuggestions $ZSH_CUSTOM/plugins/zsh-autosuggestions
# add zsh-autosuggestions to plugins list in ~/.zshrc and:
source ~/.zshrc
```

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
ln -sf $(brew --prefix)/Cellar/spaceship/4.4.1/spaceship.zsh $ZSH_CUSTOM/themes/spaceship.zsh-theme

touch ~/.spaceshiprc.zsh
```

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

Install iTerm 2 color schemes
```Shell
git clone https://github.com/mbadolato/iTerm2-Color-Schemes.git
cd iTerm2-Color-Schemes

# Import all color schemes
tools/import-scheme.sh schemes/*

# Import all color schemes (verbose mode)
tools/import-scheme.sh -v schemes/*

# Import specific color schemes (quotations are needed for schemes with spaces in name)
tools/import-scheme.sh 'schemes/SpaceGray Eighties.itermcolors' # by file path
tools/import-scheme.sh 'SpaceGray Eighties'                     # by scheme name
tools/import-scheme.sh Molokai 'SpaceGray Eighties'             # import multiple
```
Restart iTerm 2 (need to quit iTerm 2 to reload the configuration file).  
iTerm2 > Preferences > Profile > Colors > Color Presets 