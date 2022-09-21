# Stable Diffusion in a container

There are many ways to deploy an application on a container. On your laptop for local testing, on the cloud using either a self-managed VM or a managed container service, to name a few.  

There are also different ways to decouple storage and compute e.g. using Docker volumes, bind mounts, attached block storage, a shared file system, or mounting object storage onto the host as a directory and mounting it onto the Docker container. These have tradeoffs regarding ease of use, portability, performance, cost, features, and operational overhead such as backups.  

# Option A - Cloud deployment

Since my Macbook Air M2 with an 8-core GPU has an **arm**64 architecture and I don't have an **amd**64 machine with NVIDIA GPUs I'll use a cloud instance to illustrate the process.  

For flexibility on our choice of container registry and other aspects of our target environment, we'll use a VM on the cloud (known as an *instance*) to build our own Docker image. For simplicity we'll store the model files in object storage that can be mounted on our container and used without changes to the application code. This example uses AWS but the concepts should translate to other options fairly easily.  

Make sure you have the AWS CLI installed and configured with your credentials. Then follow this guide.  

## Create an S3 bucket for the models

Choose a bucket name. It needs to be unique so add something to it like your name. Then copy the model files to the bucket.  

On your laptop
```Shell
BUCKET="santisbon-models"
REGION="us-east-1"

aws s3api create-bucket \
    --bucket $BUCKET \
    --region $REGION \
    --acl private

aws s3 cp ~/Downloads/sd-v1-4.ckpt s3://$BUCKET/sd-v1-4.ckpt
aws s3 cp ~/Downloads/GFPGANv1.3.pth s3://$BUCKET/GFPGANv1.3.pth

# Create role with read permissions on the bucket, create instance profile, assign role to instance profile. Then when you launch the instance, specify the instance profile.
# Applications can obtain temporary security credentials from Amazon EC2 instance metadata. AWS SDKs and s3fs-fuse do it transparently.

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
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::${BUCKET}/*"
  }
}
EOF

# Create the role and attach the trust policy that allows EC2 to assume this role.
$ aws iam create-role --role-name S3-Role-for-EC2 --assume-role-policy-document ./trustpolicyforec2.json

# Embed the permissions policy (in this example an inline policy) to the role to specify what it is allowed to do.
$ aws iam put-role-policy --role-name S3-Role-for-EC2 --policy-name Permissions-Policy-For-Ec2 --policy-document ./permissionspolicyforec2.json

# Create the instance profile required by EC2 to contain the role
$ aws iam create-instance-profile --instance-profile-name EC2-ListBucket-S3

# Finally, add the role to the instance profile
$ aws iam add-role-to-instance-profile --instance-profile-name EC2-ListBucket-S3 --role-name S3-Role-for-EC2
```

[Learn more](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html)

## Launch an instance

As you launch your intance from the AWS console you'll need to make some decisions.

### Choose an Amazon Machine Image (AMI) 

First we'll get the ID for the image we want to use. We'll use the Deep Learning AMI (Ubuntu 18.04). It includes NVIDIA CUDA, Docker, and NVIDIA-Docker. This example uses the N. Virginia region; adjust for the one closest to your location.

```Shell
aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI*Ubuntu 20*' \
          'Name=state,Values=available' \
          'Name=architecture,Values=x86_64' \
--query 'reverse(sort_by(Images, &CreationDate))[*].[ImageId,PlatformDetails,Name,Description]' \
--output json

aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Ubuntu 18.04) Version ??.?' \
          'Name=state,Values=available' \
          'Name=architecture,Values=x86_64' \
--query 'reverse(sort_by(Images, &CreationDate))[:1]' \
--output json

aws ec2 describe-images \
--region $REGION \
--owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Ubuntu 18.04) Version ??.?' \
          'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' \
--output text
```

We can see that the AMI ID for this region is: *ami-07351ca9581da4fc7*.

### Choose an instance family

*G4dn* instances feature NVIDIA T4 GPUs and custom Intel Cascade Lake CPUs, and are optimized for machine learning inference and small scale training. Ideal for NVIDIA software such as CUDA.
You can use the size appropriate for your needs but here we'll go with ```g4dn.xlarge```: 1 GPU, 4 vCPUs, 16 GiB memory. At the time of this writing in the selected region it costs $0.526 per hour on-demand. Feel free to explore cost optimization measures such as *spot instances*.

### Create instance profile
TODO: Create a role (the AWS console creates an instance profile automatically) and grant it permissions to read your S3 bucket.

### Set up storage access

User data on the instance.
```Shell
apt update
apt upgrade

# Mount storage on host instance
sudo apt install s3fs
sudo mkdir /mnt/sd-data
export BUCKET="santisbon-models"
sudo s3fs $BUCKET /mnt/sd-data -o iam_role=auto -o allow_other -o default_acl=private -o use_cache=/tmp/s3fs
```

Test from the host instance. Connect to it via ssh 

On your laptop
```Shell
# TODO: 
```

On the instance:
```Shell
# View contents of the S3 bucket and the mounted dir (should match).
aws s3 ls s3://$BUCKET
ll /mnt/sd-data
# TODO: Build Docker image with Dockerfile and linux environment file
# Run container with mount source = host dir and target = container dir
docker run \
--mount type=bind,source=/mnt/sd-data,target=/data,readonly \
<your-container-image>
```
You're now at the command line on the container. Follow the usage instructions to generate AI images.

[Learn more about s3fs](https://github.com/s3fs-fuse/s3fs-fuse/blob/master/doc/man/s3fs.1.in)
[Learn more about canned ACLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl)
[Larn more about cleanup to prevent charges when you're no longer using the instance](https://docs.aws.amazon.com/dlami/latest/devguide/launch-config-cleanup.html)
Now you have a container running on a Linux instance with NVIDIA GPUs and CUDA in the cloud. Connect to it via ssh and follow the steps in the next section as if you were working directly on the Linux machine.

# Option B - Local deployment

If you have a Linux amd64 laptop you can have a simple setup that holds everything on your machine but still decouples compute and storage (or at least the largest model files) by setting up a Docker volume.