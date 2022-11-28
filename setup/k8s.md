# Kubernetes

## Designing Applications for Kubernetes

A Cloud Guru course. It uses Ubuntu 20.04 Focal Fossa LTS and the Calico network plugin instead of Flannel.  
Example with 1 control plane node and 2 worker nodes.

### Building a Kubernetes Cluster

`kubeadm` simplifies the process of setting up a k8s cluster.  
`containerd` manages the complete container lifecycle of its host system, from image transfer and storage to container execution and supervision to low-level storage to network attachments.  
`kubelet` handles running containers on a node.  
`kubectl` is a tool for managing the cluster.  

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1658326918182-Building%20a%20Kubernetes%20Cluster.pdf)  

If you wish, you can set an appropriate hostname for each node.  
On the control plane node:  
```Shell
sudo hostnamectl set-hostname k8s-control
```

On the first worker node:  
```Shell
sudo hostnamectl set-hostname k8s-worker1
```
On the second worker node:  
```Shell
sudo hostnamectl set-hostname k8s-worker2
```

On all nodes, set up the hosts file to enable all the nodes to reach each other using these hostnames.
```Shell
sudo nano /etc/hosts
```

On all nodes, add the following at the end of the file. You will need to supply the actual private IP address for each node.
```Shell
<control plane node private IP> k8s-control
<worker node 1 private IP> k8s-worker1
<worker node 2 private IP> k8s-worker2
```

Log out of all three servers and log back in to see these changes take effect.  

**On all nodes, set up containerd**. You will need to load some kernel modules and modify some system settings as part of this
process.  
```Shell
# Enable them when the server start up
cat << EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF

# Enable them right now without having to restart the server
sudo modprobe overlay
sudo modprobe br_netfilter

# Add network configurations k8s will need
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

# Apply them immediately
sudo sysctl --system
```

Install and configure containerd.  
```Shell
sudo apt-get update && sudo apt-get install -y containerd
sudo mkdir -p /etc/containerd
# Generate the contents of a default config file and save it
sudo containerd config default | sudo tee /etc/containerd/config.toml
# Restart containerd to make sure it's using that configuration
sudo systemctl restart containerd
```

**On all nodes, disable swap**.
```Shell
sudo swapoff -a
```
**On all nodes, install kubeadm, kubelet, and kubectl**.
```Shell
# Some required packages
sudo apt-get update && sudo apt-get install -y apt-transport-https curl
# Set up the package repo for k8s packages. Download the key for the repo and add it
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
# Configure the repo
cat << EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
sudo apt-get update
# Install the k8s packages. Make sure the versions for all 3 are the same.
sudo apt-get install -y kubelet=1.24.0-00 kubeadm=1.24.0-00 kubectl=1.24.0-00
# Make sure they're not automatically upgraded. Have manual control over when to update k8s
sudo apt-mark hold kubelet kubeadm kubectl
```

**On the control plane node only**, initialize the cluster and set up kubectl access.
```Shell
sudo kubeadm init --pod-network-cidr 192.168.0.0/16 --kubernetes-version 1.24.0
# Config File to authenticate and interact with the cluster with kubectl commands
# These are in the output of the previous step
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Verify the cluster is working. It will be in Not Ready status because we haven't configured the networking plugin.
```Shell
kubectl get nodes
```

Install the Calico network add-on.
```Shell
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

Get the join command (this command is also printed during kubeadm init . Feel free to simply copy it from there).
```Shell
kubeadm token create --print-join-command
```

Copy the join command from the control plane node. Run it **on each worker node** as root (i.e. with sudo ).
```Shell
sudo kubeadm join ...
```

**On the control plane node**, verify all nodes in your cluster are ready. Note that it may take a few moments for all of the nodes to
enter the READY state.
```Shell
kubectl get nodes
```

### Installing Docker

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631214923454-1082%20-%20S01L03%20Installing%20Docker.pdf)  

**On the system that will build Docker images from source code** e.g. a CI server, install and configure Docker.  
For simplicity we'll use the control plane server just so we don't have to create another server for this exercise.  

Create a docker group. Users in this group will have permission to use Docker on the system:
```Shell
sudo groupadd docker
```

Install required packages.  
Note: Some of these packages may already be present on the system, but including them here will not cause any problems:
```Shell
sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
```

Set up the Docker GPG key and package repository:
```Shell
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install the Docker Engine:
```Shell
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli
# Type N (default) or enter to keep your current containerd configuration
```

Test the Docker setup:
```Shell
sudo docker version
```

Add cloud_user to the docker group in order to give cloud_user access to use Docker:
```Shell
sudo usermod -aG docker cloud_user
```
Log out of the server and log back in.  
Test your setup:
```Shell
docker version
```

## Kubernetes Essentials
A Cloud Guru has instructions for their Kubernetes Essentials course using Ubuntu. It uses a specific version of docker in part because Kubeadm sometimes doesn't work with the latest and greatest version of docker right away.

### Interactive Diagram

[Diagram](https://lucid.app/lucidchart/6d5625be-9ef9-411d-8bea-888de55db5cf/view?page=0_0#)

### Use

[Containers and Pods](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1661512878582-Lesson%20Reference-Containers%20and%20Pods.txt)  
[Clustering and nodes](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1597958349080-02_02_Clustering%20and%20Nodes.pdf)  
[Networking in Kubernetes](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1661512922299-Lesson%20Reference-Networking%20in%20Kubernetes.txt)  
[Kubernetes Architecture and components](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1597958377028-02_04_Kubernetes%20Architecture%20and%20Components.pdf)  
[Kubernetes Deployments](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1638556999819-03_01_Kubernetes%20Deployments.txt)  *Corrected script [here](https://gist.github.com/santisbon/78909fd6775288f905e997de73cd46f3)  
[Kubernetes Services](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1661512983062-Lesson%20Reference-Kubernetes%20Services.txt)  
