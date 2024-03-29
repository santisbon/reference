# Git
## Install

macOS  
```zsh
brew install git
git --version

# GitHub CLI
brew install gh 
gh auth login
gh config set editor "codium -w" # or code, nano, etc
```
GitHub CLI [reference](https://docs.github.com/en/github-cli/github-cli/github-cli-reference).

Linux
```zsh
sudo yum install git # or git-all
git --version
```

## Configure
```zsh
git config --global core.editor 'codium --wait'

git config --global diff.tool codium
git config --global difftool.codium.cmd 'codium --wait --diff $LOCAL $REMOTE'

git config --global merge.tool codium
git config --global mergetool.codium.cmd 'codium --wait $MERGED'

# or
codium ~/.gitconfig # Also: codium, vscode, nano
```

Then you can ```git difftool main feature-branch```.  

If using AWS CodeCommit do this after configuring the AWS CLI:
```zsh
git config --global credential.helper '!aws codecommit credential-helper $@'
git config --global credential.UseHttpPath true
```
[Troubleshooting CodeCommit](https://docs.aws.amazon.com/codecommit/latest/userguide/troubleshooting-ch.html#troubleshooting-macoshttps)

To create a squash function:
```zsh
git config --global alias.squash-all '!f(){ git reset $(git commit-tree "HEAD^{tree}" "$@");};f'
```
!!! note
    * Git allows you to escape to a shell (like bash or zsh) using the ! (bang). [Learn more](https://www.atlassian.com/blog/git/advanced-git-aliases).
    * [`commit-tree`](https://git-scm.com/docs/git-commit-tree) creates a new commit object based on the provided tree object and emits the new commit object id on stdout.
    * [`tree` objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects#Tree-Objects) correspond to UNIX directory entries. 
    * `reset` resets current HEAD to the specified state e.g a commit.
    * The `master^{tree}` syntax specifies the tree object that is pointed to by the last commit on your `master` branch. So `HEAD^{tree}` is the tree object pointed to by the last commit on your current branch.
    * If you’re using ZSH, the `^` character is used for globbing, so you have to enclose the whole expression in quotes: `"HEAD^{tree}"`.

Then just run:
```zsh
git squash-all -m "a brand new start"
git push -f
```

[Change](https://docs.github.com/en/get-started/getting-started-with-git/managing-remote-repositories#changing-a-remote-repositorys-url) a remote repo's URL
```zsh
git remote set-url origin git@github.com:OWNER/REPOSITORY.git
```
Or edit `.git/config` and change the URLs there.

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

!!! tip
    If the terminal is no longer authenticating you:
    ```zsh
    git remote -v # is it https or ssh? Should be ssh
    git remote remove origin
    git remote add origin git@github.com:user/repo.git
    ```

    Still having issues? Start the `ssh-agent` in the background and add your SSH private key to it.  
    ```zsh
    # is it running?
    ps -ax | grep ssh-agent
    # which identities have been added?
    ssh-add -l

    # start the agent and add your identity
    eval "$(ssh-agent -s)"
    ssh-add --apple-use-keychain ~/.ssh/id_ed25519
    ```

If you need to add your public key to Github again copy and paste it on your Settings page on Github:
```zsh
pbcopy < ~/.ssh/id_ed25519.pub
```

