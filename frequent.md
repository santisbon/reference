# Frequently used commands
Some of these come when you have the OhMyZsh plugins and .zshrc file recommended in this repo.  

# Git
```Shell
gst                   # git status
ga                    # git add
gb                    # git branch (--list)
gb new-feature        # git branch
gco feature           # git checkout
gcb new-feature       # git checkout -b

gcmsg "Fixed x"       # git commit -m

gdt main feature      # git diff-tree
gdtl main feature     # git difftool 

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

git log --author="Armando"

# oneline | short | medium | full | fuller
git log --author=Armando --pretty=oneline --grep="Merge branch 'lstein"

python3 scripts/dream.py --full_precision

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

# Docker
```Shell
drme  # docker rm -v $(docker ps -aq -f status=exited)
dps   # docker ps -a

docker image inspect santisbon/stablediffusion-amd64
docker image rm santisbon/stablediffusion-amd64
docker run -it --platform=linux/amd64 --name stablediffusion santisbon/stablediffusion-amd64

# Login to Docker Hub to scan images for vulnerabilities
docker scan --login
docker scan <image-name>
# Create a snapshot of your project
snyk monitor
```

```scp``` is too slow for copying big files into a Docker host instance and volume. For small files it's fine.  
Example:
```Shell
# On your local machine
scp -i ~/.ssh/$MY_KEY".pem" ~/Downloads/big-file.pth ec2-user@$INSTANCE_PUBLIC_DNS:~/
# On the docker host instance
docker cp ~/big-file.pth <container-id>:/data
rm -rf ~/big-file.pth
```

# Python
```Shell
# conda envs
conda create -y --name myenv && conda activate myenv
conda env list
conda env remove --name myenv

# debug a script
python3 -m pdb scripts/dream.py --full_precision
# Pdb command to set breakpoint: b path/to/file.py:<line>
(Pdb) b ../ldm/gfpgan/gfpgan_tools.py:10
# Pdb commands: n(ext), s(tep), c(ont(inue))
# print variable: p <variable>
(Pdb) p model_path
```

# AWS

```Shell
aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI*' \
          'Name=state,Values=available' \
          'Name=architecture,Values=x86_64' \
          'Name=virtualization-type,Values=hvm' \
--query 'reverse(sort_by(Images, &CreationDate))[*].[ImageId,PlatformDetails,Architecture,Name,Description,RootDeviceType,VirtualizationType]' \
--output json

aws ec2 describe-images --image-ids ami-XXXXXXXXXX

aws ssm get-parameters-by-path \
 --path /aws/service/ami-amazon-linux-latest \
 --query 'Parameters[].Name'

aws ssm get-parameters-by-path \
 --path / \
 --output json
```

You can retrieve the current Amazon [ECS GPU-optimized AMI](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html) using the AWS CLI with the following command:
```Shell
aws ssm get-parameters \
--names /aws/service/ecs/optimized-ami/amazon-linux-2/gpu/recommended \
--query "Parameters[0].Value" 
```

[Learn more about s3fs](https://github.com/s3fs-fuse/s3fs-fuse/blob/master/doc/man/s3fs.1.in)  
[Learn more about canned ACLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl)  
[Larn more about cleanup to prevent charges when you're no longer using the instance](https://docs.aws.amazon.com/dlami/latest/devguide/launch-config-cleanup.html)  

# [HERE Documents](https://stackoverflow.com/a/25903579)  

To overwrite an existing file (or write to a new file) that you own, substituting variable references inside the heredoc:
```Shell
cat << EOF > /path/to/your/file
This line will write to the file.
${THIS} will also write to the file, with the variable contents substituted.
EOF
```

To append an existing file (or write to a new file) that you own, substituting variable references inside the heredoc:
```Shell
cat << FOE >> /path/to/your/file
This line will write to the file.
${THIS} will also write to the file, with the variable contents substituted.
FOE
```

To overwrite an existing file (or write to a new file) that you own, with the literal contents of the heredoc:
```Shell
cat << 'END_OF_FILE' > /path/to/your/file
This line will write to the file.
${THIS} will also write to the file, without the variable contents substituted.
END_OF_FILE
```

To append an existing file (or write to a new file) that you own, with the literal contents of the heredoc:
```Shell
cat << 'eof' >> /path/to/your/file
This line will write to the file.
${THIS} will also write to the file, without the variable contents substituted.
eof
```

To overwrite an existing file (or write to a new file) owned by root, substituting variable references inside the heredoc:
```Shell
cat << until_it_ends | sudo tee /path/to/your/file
This line will write to the file.
${THIS} will also write to the file, with the variable contents substituted.
until_it_ends
```

To append an existing file (or write to a new file) owned by user=foo, with the literal contents of the heredoc:
```Shell
cat << 'Screw_you_Foo' | sudo -u foo tee -a /path/to/your/file
This line will write to the file.
${THIS} will also write to the file, without the variable contents substituted.
Screw_you_Foo
```
