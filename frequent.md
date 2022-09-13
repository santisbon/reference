If you have the OhMyZsh plugins and .zshrc file recommended here you can:  

Git
```Shell
gst                   # git status
ga                    # git add
gb                    # git branch (--list)
gb new-feature        # git branch
gco feature           # git checkout
gcb new-feature       # git checkout -b

gcmsg "Fixed x"       # git commit -m

gdt main feature      # git diff-tree
gdtl main feature     # git difftool with Codium

git config pull.rebase true   # rebase
gco bugFix            # git checkout bugFix
grb main              # git rebase main
gco main              # git checkout main
grb bugFix            # git rebase bugFix

gbd feature           # git branch -d (--delete)
gbD feature           # git branch -D (--delete --force)
gp origin -d feature  # git push origin --delete feature

git diff              # changes between the Working Directory and the Staging Area
git diff HEAD         # changes between the Working Directory and the HEAD
git diff --staged     # changes between the Staging Area and the HEAD

# Github CLI
gh pr list -R <user>/<repo> | grep something
gh pr view <number> -R <user>/<repo> 
```

For rebase behavior you have:
```Shell
git config pull.rebase false  # merge
git config pull.rebase true   # rebase
git config pull.ff only       # fast-forward only
```
Hint: You can replace ```git config``` with ```git config --global``` to set a default preference for all repositories. You can also pass ```--rebase```, ```--no-rebase```, or ```--ff-only``` on the command line to override the configured default per
invocation.

Docker
```Shell
drme  # docker rm -v $(docker ps -aq -f status=exited)
dps   # docker ps -a
```
