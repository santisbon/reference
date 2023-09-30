## macOS

Do you want your new machine (or a brand new, [clean install](/reference/install-os/) of macOS on the same machine) to be automatically set up just the way you like it? You can set up your git and shell configurations, tools, apps (including the ones from the App Store), and macOS preferences automatically.

Get the [Homebrew](https://brew.sh/) package manager and GitHub CLI. You can use a more [detailed guide](https://mac.install.guide/homebrew/index.html) if needed.
```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install gh
```

Install [chezmoi](https://www.chezmoi.io/install/) to manage your dotfiles. You'll need this on your current and new machines.
```sh
brew install chezmoi
```

On your current machine:
```sh
chezmoi init
# Add your dotfiles e.g.
chezmoi add ~/.gitconfig
chezmoi add ~/.zshrc

cd ~/.local/share/chezmoi
brew bundle dump # generates your Brewfile
# add and commit everything, then
gh repo create dotfiles --public -d "My dotfiles" -y
git remote add origin git@github.com:$GITHUB_USERNAME/dotfiles.git
git branch -M main
git push -u origin main
```
See my [dotfiles](https://github.com/santisbon/dotfiles) repo for an example that includes: 

* Brewfile with tools and apps from both Homebrew and the App Store (with [mas](https://github.com/mas-cli/mas)).
* Dotfiles for git and shell configurations.
* iTerm profile.
* macOS preferences.

Then on your [new machine](https://www.chezmoi.io/quick-start/#using-chezmoi-across-multiple-machines), after installing Homebrew and chezmoi, install [Oh My Zsh](https://ohmyz.sh): 
```sh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
and let chezmoi and Homebrew configure your new machine:
```sh
chezmoi init --apply $GITHUB_USERNAME

# Install all tools, extensions, and apps from Homebrew and the App Store:
brew bundle --no-lock --file="~/.local/share/chezmoi/Brewfile" 
# At any time you can also update your dotfiles:
chezmoi update -v

# If you use GitHub with an SSH key
cd ~/.local/share/chezmoi
git remote -v # is it https? Change it to use your SSH key:
git remote remove origin
git remote add origin git@github.com:$GITHUB_USERNAME/dotfiles.git
git fetch # retrieve upstream branches from the remote
git branch -u origin/main # branch 'main' set up to track 'origin/main'.
```

If you have a [macOS defaults script](https://github.com/santisbon/dotfiles/blob/main/macos-defaults.sh), run it.

If you have an iTerm profile `.json` file:

1. *iTerm2 > Settings > Profiles > Other Actions... > Import JSON Profiles*  
2. Restart iTerm to reload the configuration file.

!!! tip
    In Finder you can also show/hide your hidden files with ++command+shift+period++