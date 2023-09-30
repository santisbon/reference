## macOS

You can automatically set up your dotfiles, tools, apps from Homebrew and App Store, and macOS preferences on a new machine.

Get the [Homebrew](https://brew.sh/) package manager and GitHub cli.
```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew doctor
brew install gh
```
You can use a more [detailed guide](https://mac.install.guide/homebrew/index.html) if needed.

Install [chezmoi](https://www.chezmoi.io/install/) to manage your dotfiles. You'll need this on your current and new machines.
```sh
brew install chezmoi
```

On your current machine, backup your configuration, edit the generated Brewfile as needed, and push to a GitHub repo. 
Add [mas](https://github.com/mas-cli/mas) to your Brewfile to automate App Store installs.  
See my [`dotfiles`](https://github.com/santisbon/dotfiles) repo for examples.
```sh
chezmoi init
chezmoi add ~/.gitconfig
chezmoi add ~/.zshrc
chezmoi add ~/.spaceshiprc.zsh

cd ~/.local/share/chezmoi
brew bundle dump # generates your Brewfile
# add and commit everything, then
gh repo create dotfiles --public -d "My dotfiles" -y
git remote add origin git@github.com:$GITHUB_USERNAME/dotfiles.git
git branch -M main
git push -u origin main
```

On your [new machine](https://www.chezmoi.io/quick-start/#using-chezmoi-across-multiple-machines)
```sh
chezmoi init --apply $GITHUB_USERNAME
cd ~/.local/share/chezmoi
git remote -v # is it https? Change to ssh
git remote remove origin
git remote add origin git@github.com:$GITHUB_USERNAME/dotfiles.git
git fetch # retrieve upstream branches that already exist at the remote
git branch -u origin/main # branch 'main' set up to track 'origin/main'.

# Install all tools, extensions, and apps from Homebrew and the App Store
brew bundle --no-lock --file="~/.local/share/chezmoi/Brewfile" 
# At any time you can also update your dotfiles
chezmoi update -v
```

If you have a [macOS defaults script](https://github.com/santisbon/dotfiles/blob/main/macos-defaults.sh) run it.

Follow any [shell instructions](/reference/shell/) that are not covered by your `chezmoi`/`brew bundle`/`defaults` files. Same thing for any other sections of this documentation not covered by the automation.

