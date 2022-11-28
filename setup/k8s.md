# Kubernetes

## Designing Applications for Kubernetes
Based on the [12-Factor App Design Methodology](https://12factor.net/)

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
[Docker credentials store](https://docs.docker.com/engine/reference/commandline/login/#credentials-store) 
to avoid storing your Docker Hub password unencrypted in `$HOME/.docker/config.json` when you `docker login` and `docker push` your images.  

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

### Kubernetes configuration with ConfigMaps and Secrets
[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631214961641-1082%20-%20S02L03%20III.%20Config%20with%20ConfigMaps%20and%20Secrets.pdf)  

[Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)  
[ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)  
[Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)  

Create a production Namespace:
```Shell
kubectl create namespace production
```

Get base64-encoded strings for a db username and password:
```Shell
echo -n my_user | base64
echo -n my_password | base64
```

Example: Create a ConfigMap and Secret to configure the backing service connection information for the app, including the base64-encoded credentials:
```Shell
cat > my-app-config.yml <<End-of-message 
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  mongodb.host: "my-app-mongodb"
  mongodb.port: "27017"

---

apiVersion: v1
kind: Secret
metadata:
  name: my-app-secure-config
type: Opaque
data:
  mongodb.username: dWxvZV91c2Vy
  mongodb.password: SUxvdmVUaGVMaXN0

End-of-message
```

```Shell
kubectl apply -f my-app-config.yml -n production
```

Create a temporary Pod to test the configuration setup. Note that you need to supply your Docker Hub username as part of the image name in this file.
This passes configuration data in env variables but you could also do it in files that will show up on the containers filesystem.
```Shell
cat > test-pod.yml <<End-of-message

apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
  - name: my-app-server
    image: <YOUR_DOCKER_HUB_USERNAME>/my-app-server:0.0.1
    ports:
    - name: web
      containerPort: 3001
      protocol: TCP
    env:
    - name: MONGODB_HOST
      valueFrom:
        configMapKeyRef:
          name: my-app-config
          key: mongodb.host
    - name: MONGODB_PORT
      valueFrom:
        configMapKeyRef:
          name: my-app-config
          key: mongodb.port
    - name: MONGODB_USER
      valueFrom:
        secretKeyRef:
          name: my-app-secure-config
          key: mongodb.username
    - name: MONGODB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: my-app-secure-config
          key: mongodb.password

End-of-message
```

```Shell
kubectl apply -f test-pod.yml -n production
```

Check the logs to verify the config data is being passed to the container:
```Shell
kubectl logs test-pod -n production
```

Clean up the test pod:
```Shell
kubectl delete pod test-pod -n production --force
```

### Build, Release, Run with Docker and Deployments
[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215185856-1082%20-%20S03L02%20V.%20Build%2C%20Release%2C%20Run%20with%20Docker%20and%20Deployments.pdf)  

Example: After you `docker build` and `docker push` your image to a repository, create a deployment file for your app.
The `selector` selects pods that have the specified label name and value.  
`template` is the pod template.  
This example puts 2 containers in the same pod for simplicity but in the real world you'll want separate deployments to scale them independently.

```Shell
cat > my-app.yml <<End-of-message
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  mongodb.host: "my-app-mongodb"
  mongodb.port: "27017"
  .env: |
    REACT_APP_API_PORT="30081"

---

apiVersion: v1
kind: Secret
metadata:
  name: my-app-secure-config
type: Opaque
data:
  mongodb.username: dWxvZV91c2Vy
  mongodb.password: SUxvdmVUaGVMaXN0

---

apiVersion: v1
kind: Service
metadata:
  name: my-app-svc
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
  - name: frontend
    protocol: TCP
    port: 30080
    nodePort: 30080
    targetPort: 5000
  - name: server
    protocol: TCP
    port: 30081
    nodePort: 30081
    targetPort: 3001

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app-server
        image: <Your Docker Hub username>/my-app-server:0.0.1
        ports:
        - name: web
          containerPort: 3001
          protocol: TCP
        env:
        - name: MONGODB_HOST
          valueFrom:
            configMapKeyRef:
              name: my-app-config
              key: mongodb.host
        - name: MONGODB_PORT
          valueFrom:
            configMapKeyRef:
              name: my-app-config
              key: mongodb.port
        - name: MONGODB_USER
          valueFrom:
            secretKeyRef:
              name: my-app-secure-config
              key: mongodb.username
        - name: MONGODB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: my-app-secure-config
              key: mongodb.password
      - name: my-app-frontend
        image: <Your Docker Hub username>/my-app-frontend:0.0.1
        ports:
        - name: web
          containerPort: 5000
          protocol: TCP
        volumeMounts:
        - name: frontend-config
          mountPath: /usr/src/app/.env
          subPath: .env
          readOnly: true
      volumes:
      - name: frontend-config
        configMap:
          name: my-app-config
          items:
          - key: .env
            path: .env
End-of-message
```

Deploy the app.
```Shell
kubectl apply -f my-app.yml -n production
```

Create a new container image version to test the rollout process:
```Shell
docker tag <Your Docker Hub username>/my-app-frontend:0.0.1 <Your Docker Hub username>/my-app-frontend:0.0.2
docker push <Your Docker Hub username>/my-app-frontend:0.0.2
```

Edit the app manifest `my-app-app.yml` to use the `0.0.2` image version and then:
```Shell
kubectl apply -f my-app.yml -n production
```

Get the list of Pods to see the new version rollout:
```Shell
kubectl get pods -n production
```

## Kubernetes Essentials
A Cloud Guru course using Ubuntu 18. It uses a specific version of docker in part because Kubeadm sometimes doesn't work with the latest and greatest version of docker right away.

### Interactive Diagram

[Diagram](https://lucid.app/lucidchart/6d5625be-9ef9-411d-8bea-888de55db5cf/view?page=0_0#)

### Use

[Containers and Pods](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1661512878582-Lesson%20Reference-Containers%20and%20Pods.txt)  
[Clustering and nodes](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1597958349080-02_02_Clustering%20and%20Nodes.pdf)  
[Networking in Kubernetes](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1661512922299-Lesson%20Reference-Networking%20in%20Kubernetes.txt)  
[Kubernetes Architecture and components](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1597958377028-02_04_Kubernetes%20Architecture%20and%20Components.pdf)  
[Kubernetes Deployments](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1638556999819-03_01_Kubernetes%20Deployments.txt)  *Corrected script [here](https://gist.github.com/santisbon/78909fd6775288f905e997de73cd46f3)  
[Kubernetes Services](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1661512983062-Lesson%20Reference-Kubernetes%20Services.txt)  
