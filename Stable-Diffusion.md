# Stable Diffusion container on AWS

There are many ways to deploy an application on a container. On your laptop for local testing, on the cloud using either a self-managed VM or a managed container service, to name a few.  

There are also different ways to decouple storage and compute e.g. using Docker volumes, attached block storage, a shared file system, or mounting object storage onto the host as a directory and mounting it onto the Docker container. These have tradeoffs regarding ease of use, portability, performance, cost, features, and operational overhead such as backups.  

Since my Macbook Air M2 with an 8-core GPU has an **arm**64 architecture and I don't have an **amd**64 machine with NVIDIA GPUs I'll use a cloud instance to illustrate the process. This example uses AWS but the concepts should translate to other environments fairly easily e.g. other cloud providers or a local installation on Linux on an amd64 machine.  

For flexibility when choosing our container registry and other aspects of our target environment, we'll use a cloud instance to build our own Docker image and run a container. For simplicity we'll store the model files in object storage that can be mounted on our container.


## AWS Deep Learning AMIs 

```Shell
aws ec2 describe-images --region us-east-1 --owners amazon \
--filters 'Name=name,Values=Deep Learning AMI*' \
          'Name=state,Values=available' \
          'Name=architecture,Values=x86_64' \
--query 'reverse(sort_by(Images, &CreationDate))[*].[ImageId,Architecture,PlatformDetails,Name,Description]' --output json

aws ec2 describe-images --region us-east-1 --owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Ubuntu 18.04) Version ??.?' 'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[:1]' --output json

aws ec2 describe-images --region us-east-1 --owners amazon \
--filters 'Name=name,Values=Deep Learning AMI (Ubuntu 18.04) Version ??.?' 'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' --output text
```

AMI: ami-07351ca9581da4fc7

Instance: G4dn instances feature NVIDIA T4 GPUs and custom Intel Cascade Lake CPUs, and are optimized for machine learning inference and small scale training. Ideal for NVIDIA software such as RTX Virtual Workstation and libraries such as CUDA, CuDNN, and NVENC.
g4dn.xlarge: 1 GPU, 4 vCPUs, 16 GiB memory, $0.526 per hour on-demand.
See more: https://docs.aws.amazon.com/dlami/latest/devguide/tutorial-gpu.html

User data:
```Shell
apt update
apt upgrade
```

## Storage

