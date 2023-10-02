## macOS

Do you want your new machine (or a brand new, [clean install](/reference/install-os/) of macOS on the same machine) to be automatically set up just the way you like it? You can set up your [dotfiles](https://missing.csail.mit.edu/2019/dotfiles/), tools, apps (including the ones from the App Store), and macOS preferences automatically.

!!! tip
    In Finder you can also show/hide your hidden files with ++command+shift+period++

Get the [Homebrew](https://brew.sh/) package manager, the GitHub CLI and [chezmoi](https://www.chezmoi.io/install/) to manage your dotfiles.
```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install gh
brew install chezmoi
```

### Current
On your current machine  

1. Back up you current configuration.
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

### New
On your new machine 

1. Install Homebrew and chezmoi. [Learn more](https://www.chezmoi.io/quick-start/#using-chezmoi-across-multiple-machines).

    !!! tip
        Install antivirus software like Avast Security. The only reason I don't include it in my Brewfile is because at the time of this writing its Homebrew formula seems to be broken so I download it directly from their site.

2. If you use [Oh My Zsh](https://ohmyz.sh), install it:
    ```sh
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    ```
3. Let chezmoi and Homebrew configure your new machine:
    ```sh
    chezmoi init --apply $GITHUB_USERNAME

    # Install all tools, extensions, and apps from Homebrew and the App Store:
    brew bundle --no-lock --file="~/.local/share/chezmoi/Brewfile" 
    # At any time you can also update your dotfiles:
    chezmoi update -v    
    ```
4. If you have a [macOS configuration script](https://github.com/santisbon/dotfiles/blob/main/macos-defaults.sh), make sure your terminal has Full Disk Access and run it with `sudo`.
5. If you have an [iTerm profile `.json` file](https://github.com/santisbon/dotfiles/blob/main/iTerm2Profile.json), add it as default and delete the old one. This will set your shell, font, colors, etc.

    1. *iTerm2 > Settings > Profiles > Other Actions... > Import JSON Profiles*.
    2. Restart iTerm to reload the configuration file.

6. If you use GitHub with an SSH key:
    ```sh
    cd ~/.local/share/chezmoi
    git remote -v # is it https? Change it to SSH with:
    git remote remove origin
    git remote add origin git@github.com:$GITHUB_USERNAME/dotfiles.git
    git fetch # retrieve upstream branches from the remote
    git branch -u origin/main # set 'main' to track 'origin/main'.
    ```
