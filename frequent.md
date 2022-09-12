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

Docker
```Shell
drme  # docker rm -v $(docker ps -aq -f status=exited)
dps   # docker ps -a
```
