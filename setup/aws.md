# Amazon Web Services

## AWS CLI

### Install the AWS command line interface
```Shell
sudo pip install --upgrade --user awscli
```

### Add the AWS CLI to your PATH
macOS  
Only if it's not already on your ~/.bash_profile e.g. ~/Library/Python/2.7/bin
```Shell
export PATH=~/Library/Python/3.10/bin:$PATH
```
Linux  
If not on your ~/.bashrc
```Shell
export PATH=~/.local/bin:$PATH
```

### Check if the AWS CLI is installed correctly
```Shell
# you may need to reload your config with "source ~/.bashrc" on Linux (or ~/.bash_profile on macOS)
aws --version
```

If you get a permission denied error on macOS, make yourself the owner 
```Shell
sudo chown -R $USER ~/Library/Python
```

### Configure the AWS CLI
```Shell
aws configure
```

## Alexa Skills Kit (ASK) CLI
https://developer.amazon.com/docs/smapi/set-up-credentials-for-an-amazon-web-services-account.html  
https://developer.amazon.com/docs/smapi/quick-start-alexa-skills-kit-command-line-interface.html

## AWS Amplify
```Shell
npm install -g @aws-amplify/cli
amplify configure
```
