# Stable Diffusion in a container

There are many ways to deploy an application on a container. On your laptop for local testing, on the cloud using either a self-managed VM or a managed container service, to name a few.  

There are also different ways to decouple storage and compute e.g. using Docker volumes, bind mounts, attached block storage, a shared file system, or mounting object storage onto the host as a directory and mounting it onto the Docker container. These have tradeoffs regarding ease of use, portability, performance, cost, features, and operational overhead such as backups.  

# Option A - Cloud deployment

Since my Macbook Air M2 with an 8-core GPU has an **arm**64 architecture and I don't have an **amd**64 machine with NVIDIA GPUs I'll use a cloud environment to illustrate the process of deploying to a container that can use CUDA.  

For flexibility on our choice of container registry and other aspects of our target environment, we'll use a VM on the cloud (known as an *instance*) to build our own Docker image. For simplicity we'll store the model files in object storage that can be mounted on our container with the help of a utility called s3fs-fuse without changes to the application code. This example uses AWS but the concepts should translate to other platforms.  

You'll need an AWS account. Make sure you have the AWS CLI installed and configured with your AWS credentials. Then follow this guide.  

## Setup

We will:  
- Use the Deep Learning AMI (Ubuntu 18.04). It includes NVIDIA CUDA, Docker, and NVIDIA-Docker.  
- Use the ```G4dn``` instance family with NVIDIA T4 GPUs and custom Intel Cascade Lake CPUs.  
Optimized for machine learning inference and small scale training. Ideal for NVIDIA software like CUDA.  
You can use the size appropriate for your needs but here we'll go with ```xlarge``` (1 GPU, 4 vCPUs, 16 GiB memory).  
- Use the default subnet on the default VPC.
- Use Parameter Store to store the AMI ID so you can retrieve it while creating or updating the infrastructure.  
- Connect to the host via ssh with an RSA key that we'll create.

```Shell
REGION="us-east-1"
MY_KEY="awsec2.pem"
BUCKET="santisbon-ai"
INSTANCE_TYPE="g4dn.xlarge"
AMI="$(aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Ubuntu 18.04) Version ??.?' \
          'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[0].ImageId' | tr -d  '"')"

mkdir -p ~/.ssh/
aws ec2 create-key-pair --region $REGION --key-name $MY_KEY --query 'KeyMaterial' | tr -d  '"' > ~/.ssh/$MY_KEY
chmod 400 ~/.ssh/$MY_KEY

aws ssm put-parameter \
    --name "deep-learning-ami" \
    --type "String" \
    --data-type "aws:ec2:image"\
    --value $AMI \
    --overwrite
```
------------------------------------------------

```Shell

cat << EOF > ./userdata.txt
apt update
apt upgrade

# Mount storage on host instance
sudo apt install s3fs
sudo mkdir /mnt/sd-data
export BUCKET="santisbon-models"
sudo s3fs $BUCKET /mnt/sd-data -o iam_role=auto -o allow_other -o default_acl=private -o use_cache=/tmp/s3fs
EOF

aws ec2 run-instances \
--region $REGION
--image-id $AMI \
--instance-type $INSTANCE_TYPE \
--iam-instance-profile $INSTANCE_PROFILE \
--security-group-ids $SG
--key-name $MY_KEY
--user-data file://./userdata.txt
```
TODO: Connect to the instance via SSH

```Shell
cd ~/Downloads
aws s3 cp ./sd-v1-4.ckpt s3://$BUCKET/sd-v1-4.ckpt
aws s3 cp ./GFPGANv1.3.pth s3://$BUCKET/GFPGANv1.3.pth
```

On the instance:
```Shell
# View contents of the S3 bucket and the mounted dir (should match).
aws s3 ls s3://$BUCKET
ll /mnt/sd-data

# TODO: Build Docker image with Dockerfile and linux environment file

# Run container with mount source = host dir and target = container dir
docker run \
--mount type=bind,source=/mnt/sd-data,target=/data \
<your-container-image>
```

Now you are at the command line on a container running on a Linux instance with NVIDIA GPUs and CUDA in the cloud. Follow the usage instructions to generate AI images.  


[Learn more about s3fs](https://github.com/s3fs-fuse/s3fs-fuse/blob/master/doc/man/s3fs.1.in)
[Learn more about canned ACLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl)
[Larn more about cleanup to prevent charges when you're no longer using the instance](https://docs.aws.amazon.com/dlami/latest/devguide/launch-config-cleanup.html)

# Option B - Local deployment

If you have a Linux amd64 laptop you can have a simple setup that holds everything on your machine but still decouples compute and storage (or at least the largest model files) by setting up a Docker volume.