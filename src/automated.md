## macOS
Get the [Homebrew](https://brew.sh/) package manager.
```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew doctor
```
You can use a more [detailed guide](https://mac.install.guide/homebrew/index.html) if needed.

Install [chezmoi](https://www.chezmoi.io/install/) to manage your dotfiles and [mas](https://github.com/mas-cli/mas) to automate App Store installs.
```sh
brew install chezmoi
brew install mas
```

On your current machine, backup your configuration, edit as needed, and push to a GitHub repo.
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
brew bundle --file="~/.local/share/chezmoi/Brewfile" # or wherever your Brewfile is

# At any time
chezmoi update -v
mas list
mas upgrade
```