# Kubernetes

## Kubernetes Essentials
[Interactive Diagram](https://lucid.app/lucidchart/6d5625be-9ef9-411d-8bea-888de55db5cf/view?page=0_0#)  
[Working with K8s objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)  
[Log rotation](https://kubernetes.io/docs/concepts/cluster-administration/logging/#log-rotation)  

In order for Kubernetes to pull your container image you need to first push it to an image repository like Docker Hub.  
To avoid storing your Docker Hub password unencrypted in $HOME/.docker/config.json when you `docker login` to your account, use a [credentials store](https://docs.docker.com/engine/reference/commandline/login/#credentials-store). A helper program lets you interact with such a keychain or external store. 

If you're doing this on your laptop with **Docker Desktop** it **already provides a store**.  
**Otherwise**, **use** one of the stores supported by the [**`docker-credential-helper`**](https://docs.docker.com/engine/reference/commandline/login/#credential-helpers). Now `docker login` on your terminal or on the Docker Desktop app.  


## Designing Applications for Kubernetes
Implements the [12-Factor App Design Methodology](https://12factor.net/) and based on a Cloud Guru course. It uses Ubuntu 20.04 Focal Fossa LTS and the Calico network plugin instead of Flannel. Example with 1 control plane node and 2 worker nodes.

### Prerequisites

#### Building a Kubernetes Cluster

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1658326918182-Building%20a%20Kubernetes%20Cluster.pdf)  
[Installing kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)  
[Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)  

* kubeadm sometimes doesn't work with the latest and greatest version of docker right away.

`kubeadm` simplifies the process of setting up a K8s cluster.  
`containerd` manages the complete container lifecycle of its host system, from image transfer and storage to container execution and supervision to low-level storage to network attachments.  
`kubelet` handles running containers on a node.  
`kubectl` is a tool for managing the cluster.  

If you wish, you can set an appropriate hostname for each node.  
**On the control plane node**:  
```zsh
sudo hostnamectl set-hostname k8s-control
```

**On the first worker node**:  
```zsh
sudo hostnamectl set-hostname k8s-worker1
```
**On the second worker node**:  
```zsh
sudo hostnamectl set-hostname k8s-worker2
```

**On all nodes**, set up the hosts file to enable all the nodes to reach each other using these hostnames.
```zsh
sudo nano /etc/hosts
```

**On all nodes**, add the following at the end of the file. You will need to supply the actual private IP address for each node.
```zsh
<control plane node private IP> k8s-control
<worker node 1 private IP> k8s-worker1
<worker node 2 private IP> k8s-worker2
```

Log out of all three servers and log back in to see these changes take effect.  

**On all nodes, set up containerd**. You will need to load some kernel modules and modify some system settings as part of this
process.  
```zsh
# Enable them when the server start up
cat << EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF

# Enable them right now without having to restart the server
sudo modprobe overlay
sudo modprobe br_netfilter

# Add network configurations K8s will need
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

# Apply them immediately
sudo sysctl --system
```

Install and configure containerd.  
```zsh
sudo apt-get update && sudo apt-get install -y containerd
sudo mkdir -p /etc/containerd
# Generate the contents of a default config file and save it
sudo containerd config default | sudo tee /etc/containerd/config.toml
# Restart containerd to make sure it's using that configuration
sudo systemctl restart containerd
```

**On all nodes, disable swap**.
```zsh
sudo swapoff -a
```
**On all nodes, install kubeadm, kubelet, and kubectl**.
```zsh
# Some required packages
sudo apt-get update && sudo apt-get install -y apt-transport-https curl
# Set up the package repo for K8s packages. Download the key for the repo and add it
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
# Configure the repo
cat << EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
sudo apt-get update
# Install the K8s packages. Make sure the versions for all 3 are the same.
sudo apt-get install -y kubelet=1.24.0-00 kubeadm=1.24.0-00 kubectl=1.24.0-00
# Make sure they're not automatically upgraded. Have manual control over when to update K8s
sudo apt-mark hold kubelet kubeadm kubectl
```

**On the control plane node only**, initialize the cluster and set up kubectl access.
```zsh
sudo kubeadm init --pod-network-cidr 192.168.0.0/16 --kubernetes-version 1.24.0
# Config File to authenticate and interact with the cluster with kubectl commands
# These are in the output of the previous step
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Verify the cluster is working. It will be in Not Ready status because we haven't configured the networking plugin.
```zsh
kubectl get nodes
```

Install the Calico network add-on.
```zsh
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

Get the join command (this command is also printed during kubeadm init . Feel free to simply copy it from there).
```zsh
kubeadm token create --print-join-command
```

Copy the join command from the control plane node. Run it **on each worker node** as root (i.e. with sudo ).
```zsh
sudo kubeadm join ...
```

**On the control plane node**, verify all nodes in your cluster are ready. Note that it may take a few moments for all of the nodes to
enter the READY state.
```zsh
kubectl get nodes
```

#### Installing Docker

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631214923454-1082%20-%20S01L03%20Installing%20Docker.pdf)  
[Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)  
[Docker credentials store](https://docs.docker.com/engine/reference/commandline/login/#credentials-store) 
to avoid storing your Docker Hub password unencrypted in `$HOME/.docker/config.json` when you `docker login` and `docker push` your images.  

**On the system that will build Docker images from source code** e.g. a CI server, install and configure Docker.  
For simplicity we'll use the control plane server just so we don't have to create another server for this exercise.  

Create a docker group. Users in this group will have permission to use Docker on the system:
```zsh
sudo groupadd docker
```

Install required packages.  
Note: Some of these packages may already be present on the system, but including them here will not cause any problems:
```zsh
sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
```

Set up the Docker GPG key and package repository:
```zsh
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install the Docker Engine:
```zsh
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli
# Type N (default) or enter to keep your current containerd configuration
```

Test the Docker setup:
```zsh
sudo docker version
```

Add cloud_user to the docker group in order to give cloud_user access to use Docker:
```zsh
sudo usermod -aG docker cloud_user
```
Log out of the server and log back in.  
Test your setup:
```zsh
docker version
```

### I. Codebase
**One codebase tracked in revision control, many deploys**  

Keep your codebase in a version control system like Git. There's a one-to-one relationship between the codebase and the app.  
If there are multiple codebases it's not an app - it's a distributed system where each component is an app.  
Factor shared code into libraries which can be included through the dependency manager.  
A deploy is a running instance of the app.

Your apps can be implemented as containers/pods, built and deployed independently of other apps.

### II. Dependencies
**Explicitly declare and isolate dependencies**

Don't rely on implicit existence of system-wide packages. Declare all dependencies, completely and exactly, via a dependency declaration manifest.
With containers, your app and its dependencies are deployed as a unit, allowing it to run almost anywhere - a desktop, a traditional IT infrastructure, or the cloud.

### III. Config 
**Store config in the environment**

#### ConfigMaps and Secrets

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631214961641-1082%20-%20S02L03%20III.%20Config%20with%20ConfigMaps%20and%20Secrets.pdf)  

[Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)  
[ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)  
[Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)  

Create a production Namespace:
```zsh
kubectl create namespace production
```

Get base64-encoded strings for a db username and password:
```zsh
echo -n my_user | base64
echo -n my_password | base64
```

Example: Create a `ConfigMap` and `Secret` to configure the backing service connection information for the app, including the base64-encoded credentials:
```zsh
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

```zsh
kubectl apply -f my-app-config.yml -n production
```

Create a temporary `Pod` to test the configuration setup. Note that you need to supply your Docker Hub username as part of the image name in this file.
This passes configuration data in env variables but you could also do it in files that will show up on the containers filesystem.
```zsh
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

```zsh
kubectl apply -f test-pod.yml -n production
```

Check the logs to verify the config data is being passed to the container:
```zsh
kubectl logs test-pod -n production
```

Clean up the test pod:
```zsh
kubectl delete pod test-pod -n production --force
```

### IV. Backing services
**Treat backing services as attached resources**

Makes no distinction between local and third party services. To the app, both are attached resources, accessed via a URL or other locator/credentials stored in the config. You should be able to swap out a local MySQL database with one managed by a third party (such as Amazon RDS) without any changes to the app’s code.

By implementing attached resources as containers/pods you achieve loose coupling between those resources and the deploy they are attached to.

### V. Build, release, run
**Strictly separate build and run stages**

#### Build, Release, Run with Docker and Deployments

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215185856-1082%20-%20S03L02%20V.%20Build%2C%20Release%2C%20Run%20with%20Docker%20and%20Deployments.pdf)  
[Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)  
[Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)  

Example: After you `docker build` and `docker push` your image to a repository, create a deployment file for your app.
The `selector` selects pods that have the specified label name and value.  
`template` is the pod template.  
This example puts 2 containers in the same pod for simplicity but in the real world you'll want separate deployments to scale them independently.

```zsh
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
```zsh
kubectl apply -f my-app.yml -n production
```

Create a new container image version to test the rollout process:
```zsh
docker tag <Your Docker Hub username>/my-app-frontend:0.0.1 <Your Docker Hub username>/my-app-frontend:0.0.2
docker push <Your Docker Hub username>/my-app-frontend:0.0.2
```

Edit the app manifest `my-app.yml` to use the `0.0.2` image version and then:
```zsh
kubectl apply -f my-app.yml -n production
```

Get the list of Pods to see the new version rollout:
```zsh
kubectl get pods -n production
```

### VI. Processes
**Execute the app as one or more stateless processes**

#### Processes with stateless containers

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1632153847308-1082%20-%20S03L03%20VI.%20Processes%20with%20Stateless%20Containers.pdf)  
[Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)  

Edit the app deployment `my-app.yml`. In the deployment Pod spec, add a new `emptyDir` volume under `volumes`:
```yaml
volumes:
- name: added-items-log
  emptyDir: {}
...
```

Mount the volume to the server container:
```yaml
containers:
...
- name: my-app-server
  ...
  volumeMounts:
  - name: added-items-log
    mountPath: /usr/src/app/added_items.log
    subPath: added_items.log
    readOnly: false
  ...
```

Make the container file system read only:
```yaml
containers:
...
- name: my-app-server
  securityContext:
    readOnlyRootFilesystem: true
  ...
```

Deploy the changes:
```zsh
kubectl apply -f my-app.yml -n production
```

#### Persistent Volumes
[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1604349952306-devops-wb002%20-%20S10-L04%20Using%20K8s%20Persistent%20Volumes.pdf)  
[Persistent Volumes (PV)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)  
[`local` PV](https://kubernetes.io/docs/concepts/storage/volumes/#local)  

Create a `StorageClass` that supports volume expansion as `localdisk-sc.yml`
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: localdisk
provisioner: kubernetes.io/no-provisioner
allowVolumeExpansion: true
```
```zsh
kubectl create -f localdisk-sc.yml
```

`persistentVolumeReclaimPolicy` says how storage can be reused when the volume's associated claims are deleted.  

- Retain: Keeps all data. An admin must manually clean up and prepare the resource for reuse.
- Recycle: Automatically deletes all data, allowing  the volume to be reused.
- Delete: Deletes underlying storage resource automatically (applies to cloud only).  

[`accessModes`](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes) can be:

- ReadWriteOnce: The volume can be mounted as read-write by a single node. Still can allow multiple pods to access the volume when the pods are running on the same node.  
- ReadOnlyMany: Can be mounted as read-only by many nodes.
- ReadWriteMany: Can be mounted as read-write by many nodes.
- ReadWriteOncePod: Can be mounted as read-write by a single Pod. Use ReadWriteOncePod access mode if you want to ensure that only one pod across whole cluster can read that PVC or write to it. This is only supported for CSI volumes.

Create a `PersistentVolume` in `my-pv.yml`.
```yaml
kind: PersistentVolume
apiVersion: v1
metadata:
  name: my-pv
spec:
  storageClassName: localdisk
  persistentVolumeReclaimPolicy: Recycle
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /var/output
```
```zsh
kubectl create -f my-pv.yml
```

Check the status of the `PersistentVolume`.
```zsh
kubectl get pv
```

Create a `PersistentVolumeClaim` that will bind to the `PersistentVolume` as `my-pvc.yml`
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  storageClassName: localdisk
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
```
```zsh
kubectl create -f my-pvc.yml
```

Check the status of the `PersistentVolume` and `PersistentVolumeClaim` to verify that they have been bound.
```zsh
kubectl get pv
kubectl get pvc
```

Create a `Pod` that uses the `PersistentVolumeClaim` as `pv-pod.yml`.
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pv-pod
spec:
  restartPolicy: Never
  containers:
  - name: busybox
    image: busybox
    command: ['sh', '-c', 'echo Success! > /output/success.txt']
    volumeMounts:
    - name: pv-storage
      mountPath: /output
  volumes:
  - name: pv-storage
    persistentVolumeClaim:
      claimName: my-pvc
```
```zsh
kubectl create -f pv-pod.yml
```

Expand the `PersistentVolumeClaim` and record the process.
```zsh
kubectl edit pvc my-pvc --record
```
```yaml
...
spec:
...
  resources:
    requests:
      storage: 200Mi
```

Delete the `Pod` and the `PersistentVolumeClaim`.
```zsh
kubectl delete pod pv-pod
kubectl delete pvc my-pvc
```

Check the status of the `PersistentVolume` to verify that it has been successfully recycled and is available again.
```zsh
kubectl get pv
```

### VII. Port binding
**Export services via port binding**

#### Port Binding with Pods

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215167150-1082%20-%20S03L04%20VII.%20Port%20Binding%20with%20Pods.pdf)  
[Cluster Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)  

!!! note
    Challenge: Only 1 process can listen on a port per host. So how do all apps on the host use a unique port?  
    In K8s, each pod has its own network namespace and cluster IP address.  
    That IP address is unique within the cluster even if there are multiple worker nodes in the cluster.  
    That means ports only need to be unique within each pod.  
    Two pods can listen on the same port because they each have their own unique IP address within the cluster network.  
    The pods can communicate across nodes simply using the unique IPs.

Get a list of Pods in the production namespace:
```zsh
kubectl get pods -n production -o wide
```

Copy the name of the IP address of the application Pod.  
Example: Use the IP address to make a request to the port on the Pod that serves the frontend content:
```zsh
curl <Pod Cluster IP address>:5000
```

### VIII. Concurrency
**Scale out via the process model**

#### Concurrency with Containers and Scaling

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215269199-1082%20-%20S04L01%20VIII.%20Concurrency%20with%20Containers%20and%20Scaling.pdf)  
[Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)  

By using `services` to manage access to the app, the service automaticaly picks up the additional pods created during scaling and route traffic to those pods.
When you have `services` alongside `deployments` you can dynamically change the number of replicas that you have and K8s will take care of everything.

Edit the application deployment `my-app.yml`.  
Change the number of replicas to 3:
```yaml
...
replicas: 3
```

Apply the changes:
```zsh
kubectl apply -f my-app.yml -n production
```

Get a list of Pods:
```zsh
kubectl get pods -n production
```

Scale the deployment up again in `my-app.yml`.  
Change the number of replicas to 5:
```yaml
...
replicas: 5
```

Apply the changes:
```zsh
kubectl apply -f my-app .yml -n production
```

Get a list of Pods:
```zsh
kubectl get pods -n production
```

### IX. Disposability
**Maximize robustness with fast startup and graceful shutdown**

#### Disposability with Stateless Containers

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215259805-1082%20-%20S04L02%20IX.%20Disposability%20with%20Stateless%20Containers.pdf)  
[Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)  
[Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)  

Deployments can be used to maintain a specified number of running replicas automatically replacing pods that fail or are deleted.

Get a list of Pods:
```zsh
kubectl get pods -n production
```

Locate one of the Pods from the `my-app` deployment and copy the Pod's name.  
Delete the Pod using the Pod name:
```zsh
kubectl delete pod <Pod name> -n production
```

Get the list of Pods again. You will notice that the deployment is automatically creating a new Pod to replace the one that was deleted:
```zsh
kubectl get pods -n production
```

### X. Dev/prod parity
**Keep development, staging, and production as similar as possible**

#### Dev/Prod Parity with Namespaces

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215371092-1082%20-%20S05L01%20X.%20Dev%3AProd%20Parity%20with%20Namespaces.pdf)  
[Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)  

K8s namespaces allow us to have multiple environments in the same cluster. A namespace is like a virtual cluster.

Create a new `namespace`:
```zsh
kubectl create namespace dev
```

Make a copy of the my-app app YAML:
```zsh
cp my-app.yml my-app-dev.yml
```

`NodePort` `services` need to be unique within the cluster. We need to choose unique ports so dev doesn't conflict with production.  
Edit the `my-app-svc` service in the `my-app-dev.yml` file to select different `nodePort`s. You will also need to edit the `my-app-config` `ConfigMap` to reflect the new port. 
Set the `nodePort`s on the service:
```yaml
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
    port: 30082
    nodePort: 30082
    targetPort: 5000
  - name: server
    protocol: TCP
    port: 30083
    nodePort: 30083
    targetPort: 3001
```

Update the configured port in the `ConfigMap`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
data:
  mongodb.host: "my-app-mongodb"
  mongodb.port: "27017"
  .env: |
    REACT_APP_API_PORT="30083"
```

Deploy the backing service setup in the new namespace:
```zsh
kubectl apply -f k8s-my-app-mongodb.yml -n dev
kubectl apply -f my-app-mongodb.yml -n dev
```

Deploy the app in the new namespace:
```zsh
kubectl apply -f my-app-dev.yml -n dev
```
Check the status of the Pods:
```zsh
kubectl get pods -n dev
```

Once all the Pods are up and running, you should be able to test the dev environment in a browser at  
```
<Control Plane Node Public IP>:30082
```

### XI. Logs
**Treat logs as event streams**

#### Logs with K8s Container Logging

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215382492-1082%20-%20S05L02%20XI.%20Logs%20with%20k8s%20Container%20Logging.pdf)  
[Logging Architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)  
[Kubectl cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/#interacting-with-running-pods)  

K8s captures log data written to stdout by containers. We can use the K8s API, `kubectl logs` or external tools to interact with container logs.  

Edit the source code for the server e.g. `src/server/index.js`. There is a log function that writes to a file. Change this function to simply write log data to the console:  
```javascript
log = function(data) {
console.log(data);
}
```

Build a new server image because we changed the source code:
```zsh
docker build -t <Your Docker Hub username>/my-app-server:0.0.4 --target server .
```

Push the image:
```zsh
docker push <Your Docker Hub username>/my-app-server:0.0.4
```

Deploy the new code. Edit `my-app.yml`. Change the image version for the server to the new image:
```yaml
containers:
- name: my-app-server
  image: <Your Docker Hub username>/my-app-server:0.0.4
```

```zsh
kubectl apply -f my-app.yml -n production
```

Get a list of Pods:
```zsh
kubectl get pods -n production
```

Copy the name of one of the my-app deployment Pods and view its logs specifying the pod, namespace, and container.
```zsh
kubectl logs <Pod name> -n production -c my-app-server
```

### XII. Admin processes
**Run admin/management tasks as one-off processes**

#### Admin Processes with Jobs

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215407613-1082%20-%20S05L03%20XII.%20Admin%20Processes%20with%20Jobs.pdf)  
[Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)  

A `Job` e.g. a database migration runs a container until its execution completes. Jobs handle re-trying execution if it fails.  
Jobs have a `restartPolicy` of `Never` because once they complete they don't run again. 
This example adds the administrative job to the server image but you could package it into its own image.  

Edit the source code for the admin process in e.g. `src/jobs/deDeuplicateJob.js`.  
Locate the block of code that begins with // Setup MongoDb backing database .  
Change the code to make the database connection configurable:  

```javascript
// Setup MongoDb backing database
const MongoClient = require('mongodb').MongoClient
// MongoDB credentials
const username = encodeURIComponent(process.env.MONGODB_USER || "my-app_user");
const password = encodeURIComponent(process.env.MONGODB_PASSWORD || "ILoveTheList");
// MongoDB connection info
const mongoPort = process.env.MONGODB_PORT || 27017;
const mongoHost = process.env.MONGODB_HOST || 'localhost';
// MongoDB connection string
const mongoURI = `mongodb://${username}:${password}@${mongoHost}:${mongoPort}/my-app`;
const mongoURISanitized = `mongodb://${username}:****@${mongoHost}:${mongoPort}/my-app`;
console.log("MongoDB connection string %s", mongoURISanitized);
const client = new MongoClient(mongoURI);
```

Edit the `Dockerfile` to include the admin job code in the server image.  
Add the following line after the other COPY directives for the server image:
```dockerfile
...
COPY --from=build /usr/src/app/src/jobs .
```

Build and push the server image:
```zsh
docker build -t <Your Docker Hub username>/my-app-server:0.0.5 --target server .
docker push <Your Docker Hub username>/my-app-server:0.0.5
```

Create a Kubernetes Job to run the admin job:
Create `de-duplicate-job.yml`.
Supply your Docker Hub username in the image tag:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: de-duplicate
spec:
  template:
    spec:
      containers:
      - name: my-app-server
        image: <Your Docker Hub username>/my-app-server:0.0.5
        command: ["node", "deDeuplicateJob.js"]
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
      restartPolicy: Never
  backoffLimit: 4
```

Run the Job:
```zsh
kubectl apply -f de-duplicate-job.yml -n production
```

Check the Job status:
```zsh
kubectl get jobs -n production
```
Get the name of the Job Pod:
```zsh
kubectl get pods -n production
```

Use the Pod name to view the logs for the Job Pod:
```zsh
kubectl logs <Pod name> -n production
```

## MicroK8s

[On Raspberry Pi](https://microk8s.io/docs/install-raspberry-pi)  
Note: Your boot parameters might be in `/boot/cmdline.txt`. Add these options at the end of the file, then `sudo reboot`.
```
cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1
```

For Raspberry Pi OS [install](https://snapcraft.io/docs/installing-snap-on-raspbian) `snap` first.
```zsh
sudo apt update
sudo apt install snapd
sudo reboot
# ...reconnect after reboot
sudo snap install core
```
Then install MicroK8s.
```zsh
pi@raspberrypi4:~ $ sudo snap install microk8s --classic
pi@raspberrypi4:~ $ microk8s status --wait-ready
pi@raspberrypi4:~ $ microk8s kubectl get all --all-namespaces
pi@raspberrypi4:~ $ microk8s enable dns dashboard registry hostpath-storage # or any other addons
pi@raspberrypi4:~ $ alias mkctl="microk8s kubectl"
pi@raspberrypi4:~ $ alias mkhelm="microk8s helm"
pi@raspberrypi4:~ $ mkctl create deployment nginx --image nginx
pi@raspberrypi4:~ $ mkctl expose deployment nginx --port 80 --target-port 80 --selector app=nginx --type ClustetIP --name nginx
pi@raspberrypi4:~ $ watch microk8s kubectl get all
pi@raspberrypi4:~ $ microk8s reset
pi@raspberrypi4:~ $ microk8s status
pi@raspberrypi4:~ $ microk8s stop # microk8s start
pi@raspberrypi4:~ $ microk8s kubectl version --output=yaml
```

You can update a snap package with `sudo snap refresh`.

Configuration file. These are the arguments you can add regarding log rotation `--container-log-max-files` and `--container-log-max-size`. They have default values. [More info](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/).
```zsh
cat /var/snap/microk8s/current/args/kubelet
```

### Registry
[Registry doc](https://microk8s.io/docs/registry-built-in)
```zsh
microk8s enable registry
```
The containerd daemon used by MicroK8s is configured to trust this insecure registry. To upload images we have to tag them with `localhost:32000/your-image` before pushing them.

### MicroK8s dashboard
If RBAC is not enabled access the dashboard using the token retrieved with:
```zsh
microk8s kubectl describe secret -n kube-system microk8s-dashboard-token
```
Use this token in the https login UI of the `kubernetes-dashboard` service.
In an RBAC enabled setup (`microk8s enable rbac`) you need to create a user with restricted permissions as shown [here](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md).

To access remotely from anywhere with [`port-forward`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#port-forward):
```zsh
microk8s kubectl port-forward -n kube-system service/kubernetes-dashboard 10443:443 --address 0.0.0.0
```

You can then access the Dashboard with IP or hostname as in https://raspberrypi4.local:10443/


### Troubleshooting
```zsh
microk8s inspect
```
MicroK8s might not recognize that cgroup memory is enabled but you can check with `cat /proc/cgroups`.


## Kubernetes Dashboard

[Documentation](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)
```zsh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.1/aio/deploy/recommended.yaml
```
```zsh
cat << EOF > dashboard-adminuser.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard

---

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
EOF
```

```zsh
kubectl apply -f dashboard-adminuser.yaml

kubectl proxy
# Kubectl will make Dashboard available at 
# http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

kubectl -n kubernetes-dashboard create token admin-user
# Now copy the token and paste it into the Enter token field on the login screen. 
```

