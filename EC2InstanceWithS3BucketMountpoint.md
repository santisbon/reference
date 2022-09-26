# Docker on a cloud instance
 
We'll use a cloud environment to illustrate the process of deploying to a container on an **amd**64 machine that can use CUDA with an NVIDIA GPU.  

For flexibility on our choice of container registry and other aspects, we'll use a VM on the cloud to build the Docker image. For simplicity we'll store the model files and images in object storage that can be mounted on our container with the help of a utility without changes to the application code.  

This example uses [AWS](https://aws.amazon.com/) but the concepts should translate to other environments. You'll need an AWS account. Make sure you have the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed and configured with AWS credentials with ```AdministratorAccess```. Then follow this guide.  

## Set up the cloud instance

We will use:  
- The Deep Learning AMI with Ubuntu. It includes NVIDIA CUDA, Docker, and NVIDIA-Docker.  
- A [GPU-based instance](https://docs.aws.amazon.com/dlami/latest/devguide/gpu.html) optimized for machine learning. Note that these have a cost so make sure you understand the pricing for [G4](https://aws.amazon.com/ec2/instance-types/g4/) and [G5](https://aws.amazon.com/ec2/instance-types/g5/) instances.
- S3 Standard for storage. Make sure you understand [S3 pricing](https://aws.amazon.com/s3/pricing/).
- The default subnet on the default VPC.
- SSM Parameter Store so we can retrieve configuration parameters while creating or updating the infrastructure.  
- SSH to connect to the instance with an RSA key that we'll create.

**On your laptop**
```Shell
REPO="https://github.com/santisbon/stable-diffusion.git"
# TODO: Change to main branch once it's merged
REPO_BRANCH="cloud-container"
REPO_PATH="$(echo $REPO | sed 's/\.git//' | sed 's/github/raw\.githubusercontent/')"
REGION="us-east-1"
MY_KEY="awsec2.pem"
BUCKET="invoke-ai"
AMI="$(aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Ubuntu 18.04) Version ??.?' \
          'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[0].ImageId' | tr -d  '"')"

mkdir -p ~/.ssh/
aws ec2 create-key-pair --region $REGION --key-name $MY_KEY --query 'KeyMaterial' | tr -d  '"' > ~/.ssh/$MY_KEY
chmod 400 ~/.ssh/$MY_KEY

aws ssm put-parameter --type "String" --data-type "aws:ec2:image" \
    --name "ai/ec2/deep-learning-ami" \
    --value $AMI 

aws ssm put-parameter --type "String" \
    --name "ai/ec2/instance-type-dev" \
    --value "g4dn.xlarge" 

aws ssm put-parameter --type "String" \
    --name "ai/ec2/instance-type-prod" \
    --value "g5.xlarge" 

aws ssm put-parameter --type "String" \
    --name "ai/ec2/key-name" \
    --value $MY_KEY 

cd ~  && mkdir docker-build && cd docker-build

wget $REPO_PATH/$REPO_BRANCH/docker-build/aws-infra.yaml

aws cloudformation create-stack \
--stack-name ai \
--template-body file://./aws-infra.yaml  \
--parameters ParameterKey=AmiId,ParameterValue=ai/ec2/deep-learning-ami \
             ParameterKey=InstanceType,ParameterValue=ai/ec2/instance-type-dev \
             ParameterKey=KeyName,ParameterValue=ai/ec2/key-name \
             ParameterKey=BucketName,ParameterValue=$BUCKET \
             ParameterKey=SSHLocation,ParameterValue=0.0.0.0/0 \
--capabilities CAPABILITY_NAMED_IAM

cd ~/Downloads
aws s3 cp ./sd-v1-4.ckpt s3://$BUCKET/sd-v1-4.ckpt
aws s3 cp ./GFPGANv1.3.pth s3://$BUCKET/GFPGANv1.3.pth

INSTANCE_PUBLIC_DNS="$(aws cloudformation describe-stacks --stack-name ai --output json \
--query "Stacks[0].Outputs[?OutputKey=='HostPublicDnsName'].OutputValue | [0]" | tr -d '"')"

ssh -i ~/.ssh/$MY_KEY ubuntu@$INSTANCE_PUBLIC_DNS
```

## Set up the container

**On the cloud instance**
```Shell
REPO="https://github.com/santisbon/stable-diffusion.git"
# TODO: Change to main branch once it's merged
REPO_BRANCH="cloud-container"
REPO_PATH="$(echo $REPO | sed 's/\.git//' | sed 's/github/raw\.githubusercontent/')"
# TODO: set to empty once merged into main.
CLONE_OPTIONS="-b $REPO_BRANCH "
# Change the tag to your own.
DOCKER_IMAGE_TAG="santisbon/stable-diffusion"
PLATFORM="linux/amd64"
REQS_FILE="requirements-lin.txt"

cd ~  && mkdir docker-build && cd docker-build
wget $REPO_PATH/$REPO_BRANCH/docker-build/Dockerfile 
wget $REPO_PATH/$REPO_BRANCH/docker-build/entrypoint.sh && chmod +x entrypoint.sh
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O anaconda.sh && chmod +x anaconda.sh

docker build -t $DOCKER_IMAGE_TAG \
--platform $PLATFORM \
--build-arg gsd=$CLONE_OPTIONS$REPO \
--build-arg rsd=$REQS_FILE .

# Mount: source is the host dir and target is the container dir
docker run -it \
--rm \
--platform $PLATFORM \
--name invoke-ai \
--hostname invoke-ai \
--mount type=bind,source=/mnt/ai-data,target=/data \
$DOCKER_IMAGE_TAG
```

**On the container**
```Shell
python3 scripts/dream.py --full_precision -o /data
```

# Troubleshooting

- The container on the cloud instance can't find the model files.
Make sure you followed the steps to mount the S3 bucket on the Docker host as a directory. Verify with:  
**On the cloud instance**
```Shell
# View contents of the dir mounted on the host (should match the S3 bucket).
ls /mnt/ai-data
```
**On the container**
```Shell
# View contents of the dir mounted on the container (should match the S3 bucket).
ls /data
```