# Stable Diffusion in a container

There are many ways to deploy an application on a container. On your laptop for local testing, on the cloud using either a self-managed VM or a managed container service, to name a few.  

There are also different ways to decouple storage and compute e.g. using Docker volumes, bind mounts, attached block storage, a shared file system, or mounting object storage onto the host as a directory and mounting it onto the Docker container. These have tradeoffs regarding ease of use, portability, performance, cost, features, and operational overhead such as backups.  

# Option A - Cloud deployment

Since my Macbook Air M2 with an 8-core GPU has an **arm**64 architecture and I don't have an **amd**64 machine with NVIDIA GPUs I'll use a cloud environment to illustrate the process of deploying to a container that can use CUDA.  

For flexibility on our choice of container registry and other aspects of our target environment, we'll use a VM on the cloud (known as an *instance*) to build our own Docker image. For simplicity we'll store the model files in object storage that can be mounted on our container with the help of a utility called s3fs-fuse without changes to the application code. This example uses AWS but the concepts should translate to other platforms.  

You'll need an AWS account. Make sure you have the AWS CLI installed and configured with your AWS credentials. Then follow this guide.  

## Set up storage for the models and outputs

We will:
- Choose a name for the S3 bucket. It needs to be unique so add something to it like your name.  
- Copy the model files to the bucket.  
- Create a role for the EC2 service. This sets the permissions for the application running on the instance to access the S3 bucket. Applications can obtain and refresh temporary security credentials from Amazon EC2 instance metadata. AWS SDKs (and in our case s3fs-fuse) do it transparently.

On your laptop
```Shell
BUCKET="santisbon-models"
REGION="us-east-1"
INSTANCE_PROFILE="EC2-S3"
INSTANCE_TYPE="g4dn.xlarge"
MY_KEY="awsec2.pem"

aws s3api create-bucket \
    --bucket $BUCKET \
    --region $REGION \
    --acl private

cd ~/Downloads

aws s3 cp ./sd-v1-4.ckpt s3://$BUCKET/sd-v1-4.ckpt
aws s3 cp ./GFPGANv1.3.pth s3://$BUCKET/GFPGANv1.3.pth

# Create the policy files we'll need for EC2.

cat << EOF > ./trustpolicyforec2.json
{
  "Version": "2012-10-17",
  "Statement": {
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }
}
EOF

cat << EOF > ./permissionspolicyforec2.json
{
  "Version": "2012-10-17",
  "Statement": {
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::${BUCKET}/*"
  }
}
EOF

# Create the role and attach the trust policy that allows EC2 to assume this role.
aws iam create-role --role-name S3-Role-for-EC2 --assume-role-policy-document file://./trustpolicyforec2.json
# Embed the permissions policy (in this example an inline policy) to the role to specify what it is allowed to do.
aws iam put-role-policy --role-name S3-Role-for-EC2 --policy-name Permissions-Policy-For-Ec2 --policy-document file://./permissionspolicyforec2.json
# Create the instance profile required by EC2 to contain the role
aws iam create-instance-profile --instance-profile-name $INSTANCE_PROFILE
# Finally, add the role to the instance profile
aws iam add-role-to-instance-profile --instance-profile-name $INSTANCE_PROFILE --role-name S3-Role-for-EC2
```

[Learn more](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html)

## Launch an instance

### Choose an Amazon Machine Image (AMI) 

First we'll get the ID for the image we want to use. We'll use the Deep Learning AMI (Ubuntu 18.04). It includes NVIDIA CUDA, Docker, and NVIDIA-Docker. This example uses the N. Virginia region; adjust for the one closest to your location.

```Shell
# platform: windows | don't specify filter for Linux
# architecture: i386 | x86_64 | arm64
# virtualization-type: paravirtual | hvm

# If you want to see all options
aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI*Ubuntu 20*' \
          'Name=state,Values=available' \
          'Name=architecture,Values=x86_64' \
          'Name=virtualization-type,Values=hvm' \
--query 'reverse(sort_by(Images, &CreationDate))[*].[ImageId,PlatformDetails,Architecture,Name,Description,RootDeviceType,VirtualizationType]' \
--output json

# Grab the ID for the Ubuntu 18 DLAMI
AMI="$(aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Ubuntu 18.04) Version ??.?' \
          'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[0].ImageId' | tr -d  '"')"

echo $AMI

aws ec2 describe-images --image-ids $AMI
```

We can see that the AMI ID for this region is: *ami-07351ca9581da4fc7*.

### Choose an instance family

*G4dn* instances feature NVIDIA T4 GPUs and custom Intel Cascade Lake CPUs, and are optimized for machine learning inference and small scale training. Ideal for NVIDIA software such as CUDA.  
You can use the size appropriate for your needs but here we'll go with 1 GPU, 4 vCPUs, 16 GiB memory. At the time of this writing in the selected region it costs $0.526 per hour on-demand. Feel free to explore cost optimization measures such as *spot instances*.

### Launch the instance with storag access

- We'll use the default subnet on the default VPC.
- TODO: Specify a security group that gives us SSH access.

On your laptop
```Shell
SG=

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