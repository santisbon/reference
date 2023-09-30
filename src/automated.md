## macOS

Do you want your new machine (or a brand new, [clean install](/reference/install-os/) of macOS on the same machine) to be automatically set up just the way you like it?  
You can automatically set up your git and shell configurations, tools, apps (including the ones from the App Store), and macOS preferences.

Get the [Homebrew](https://brew.sh/) package manager and GitHub cli. You can use a more [detailed guide](https://mac.install.guide/homebrew/index.html) if needed.
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
See my [`dotfiles`](https://github.com/santisbon/dotfiles) repo for an example that also includes macOS preferences and a Brewfile with [mas](https://github.com/mas-cli/mas) to automate App Store installs.



Then on your [new machine](https://www.chezmoi.io/quick-start/#using-chezmoi-across-multiple-machines) or clean installation of macOS:
```sh
# Install Homebrew and chezmoi, then:
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

Follow any [shell instructions](/reference/shell/) that are not covered by your `chezmoi`/`brew bundle`/`defaults` files. Same thing for any other sections of this documentation not covered by the automation.

