# Amazon Web Services
## AWS CLI

### Install the AWS command line interface
```Shell
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### Check if the AWS CLI is installed correctly
```Shell
# you may need to reload your shell's rc file first.
aws --version
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
