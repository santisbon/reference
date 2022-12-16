# Kubernetes

## Table of Contents

* [Kubernetes Essentials](#kubernetes-essentials)
* [Designing Applications for Kubernetes](#designing-applications-for-kubernetes)
  * [Building a Kubernetes Cluster](#building-a-kubernetes-cluster)
  * [Installing Docker](#installing-docker)
  * [Kubernetes configuration with ConfigMaps and Secrets](#kubernetes-configuration-with-configmaps-and-secrets)
  * [Build, Release, Run with Docker and Deployments](#build-release-run-with-docker-and-deployments)
  * [Processes with stateless containers](#processes-with-stateless-containers)
      * [Persistent Volumes](#persistent-volumes)
  * [Port Binding with Pods](#port-binding-with-pods)
  * [Concurrency with Containers and Scaling](#concurrency-with-containers-and-scaling)
  * [Disposability with Stateless Containers](#disposability-with-stateless-containers)
  * [Dev/Prod Parity with Namespaces](#devprod-parity-with-namespaces)
  * [Logs with k8s Container Logging](#logs-with-k8s-container-logging)
  * [Admin Processes with Jobs](#admin-processes-with-jobs)
* [microk8s](#microk8s)
  * [Registry](#registry)
  * [Dashboard](#dashboard)
  * [Troubleshooting](#troubleshooting)
* [Kubernetes Dashboard](#kubernetes-dashboard)

## Kubernetes Essentials
[Interactive Diagram](https://lucid.app/lucidchart/6d5625be-9ef9-411d-8bea-888de55db5cf/view?page=0_0#)  
[Working with k8s objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)  
[Log rotation](https://kubernetes.io/docs/concepts/cluster-administration/logging/#log-rotation)  

In order for Kubernetes to pull your container image you need to first push it to an image repository like Docker Hub.  
To avoid storing your Docker Hub password unencrypted in $HOME/.docker/config.json when you `docker login` to your account, use a [credentials store](https://docs.docker.com/engine/reference/commandline/login/#credentials-store). A helper program lets you interact with such a keychain or external store. 

If you're doing this on your laptop with **Docker Desktop** it **already provides a store**.  
**Otherwise**, **use** one of the stores supported by the [**`docker-credential-helper`**](https://docs.docker.com/engine/reference/commandline/login/#credential-helpers). Now `docker login` on your terminal or on the Docker Desktop app.  


## Designing Applications for Kubernetes
Based on the [12-Factor App Design Methodology](https://12factor.net/)

A Cloud Guru course. It uses Ubuntu 20.04 Focal Fossa LTS and the Calico network plugin instead of Flannel.  
Example with 1 control plane node and 2 worker nodes.

### Building a Kubernetes Cluster

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1658326918182-Building%20a%20Kubernetes%20Cluster.pdf)  
[Installing kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)  
[Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/)  
* kubeadm sometimes doesn't work with the latest and greatest version of docker right away.

`kubeadm` simplifies the process of setting up a k8s cluster.  
`containerd` manages the complete container lifecycle of its host system, from image transfer and storage to container execution and supervision to low-level storage to network attachments.  
`kubelet` handles running containers on a node.  
`kubectl` is a tool for managing the cluster.  

If you wish, you can set an appropriate hostname for each node.  
**On the control plane node**:  
```Shell
sudo hostnamectl set-hostname k8s-control
```

**On the first worker node**:  
```Shell
sudo hostnamectl set-hostname k8s-worker1
```
**On the second worker node**:  
```Shell
sudo hostnamectl set-hostname k8s-worker2
```

**On all nodes**, set up the hosts file to enable all the nodes to reach each other using these hostnames.
```Shell
sudo nano /etc/hosts
```

**On all nodes**, add the following at the end of the file. You will need to supply the actual private IP address for each node.
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
[Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)  
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
III. Config
Store config in the environment

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
V. Build, release, run
Strictly separate build and run stages

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215185856-1082%20-%20S03L02%20V.%20Build%2C%20Release%2C%20Run%20with%20Docker%20and%20Deployments.pdf)  
[Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)  
[Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)  

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

Edit the app manifest `my-app.yml` to use the `0.0.2` image version and then:
```Shell
kubectl apply -f my-app.yml -n production
```

Get the list of Pods to see the new version rollout:
```Shell
kubectl get pods -n production
```

### Processes with stateless containers
VI. Processes
Execute the app as one or more stateless processes

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1632153847308-1082%20-%20S03L03%20VI.%20Processes%20with%20Stateless%20Containers.pdf)  
[Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)  

Edit the app deployment YAML `my-app.yml`. In the deployment Pod spec, add a new emptyDir volume under volumes:
```Shell
volumes:
- name: added-items-log
  emptyDir: {}
...
```

Mount the volume to the server container:
```Shell
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
```Shell
containers:
...
- name: my-app-server
  securityContext:
    readOnlyRootFilesystem: true
  ...
```

Deploy the changes:
```Shell
kubectl apply -f my-app.yml -n production
```

#### Persistent Volumes
[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1604349952306-devops-wb002%20-%20S10-L04%20Using%20K8s%20Persistent%20Volumes.pdf)  
[Persistent Volumes (PV)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)  
[`local` PV](https://kubernetes.io/docs/concepts/storage/volumes/#local)  

Create a `StorageClass` that supports volume expansion as `localdisk-sc.yml`
```Shell
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: localdisk
provisioner: kubernetes.io/no-provisioner
allowVolumeExpansion: true
```
```Shell
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

Create a PersistentVolume in `my-pv.yml`.
```Shell
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
```Shell
kubectl create -f my-pv.yml
```

Check the status of the PersistentVolume.
```Shell
kubectl get pv
```

Create a PersistentVolumeClaim that will bind to the PersistentVolume as `my-pvc.yml`
```Shell
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
```Shell
kubectl create -f my-pvc.yml
```

Check the status of the PersistentVolume and PersistentVolumeClaim to verify that they have been bound.
```Shell
kubectl get pv
kubectl get pvc
```

Create a Pod that uses the PersistentVolumeClaim as `pv-pod.yml`.
```
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
```Shell
kubectl create -f pv-pod.yml
```

Expand the PersistentVolumeClaim and record the process.
```Shell
kubectl edit pvc my-pvc --record
```
```Shell
...
spec:
...
  resources:
    requests:
      storage: 200Mi
```

Delete the Pod and the PersistentVolumeClaim.
```Shell
kubectl delete pod pv-pod
kubectl delete pvc my-pvc
```

Check the status of the PersistentVolume to verify that it has been successfully recycled and is available again.
```
kubectl get pv
```

### Port Binding with Pods
VII. Port binding
Export services via port binding

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215167150-1082%20-%20S03L04%20VII.%20Port%20Binding%20with%20Pods.pdf)  
[Cluster Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)  

Challenge: only 1 process can listen on a port per host. So how do all apps on the host use a unique port?  
In k8s, each pod has its own network namespace and cluster IP address.  
That IP address is unique within the cluster even if there are multiple worker nodes in the cluster.  
Tht means ports only need to be unique within each pod.  
2 pods can listen on the same port because they each have their own unique IP address within the cluster network.  
The pods can communicate across nodes simply using the unique IPs.

Get a list of Pods in the production namespace:
```Shell
kubectl get pods -n production -o wide
```

Copy the name of the IP address of the application Pod.  
Example: Use the IP address to make a request to the port on the Pod that serves the frontend content:
```Shell
curl <Pod Cluster IP address>:5000
```

### Concurrency with Containers and Scaling
VIII. Concurrency
Scale out via the process model

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215269199-1082%20-%20S04L01%20VIII.%20Concurrency%20with%20Containers%20and%20Scaling.pdf)  
[Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)  

By using `services` to manage access to the app, the service automaticaly picks up the additional pods created during scaling and route traffic to those pods.
When you have `services` alongside `deployments` you can dynamically change the number of replicas that you have and k8s will take care of everything.

Edit the application deployment `my-app.yml`.  
Change the number of replicas to 3:
```Shell
...
replicas: 3
```

Apply the changes:
```Shell
kubectl apply -f my-app.yml -n production
```

Get a list of Pods:
```Shell
kubectl get pods -n production
```

Scale the deployment up again in `my-app.yml`.  
Change the number of replicas to 5:
```Shell
...
replicas: 5
```

Apply the changes:
```Shell
kubectl apply -f my-app .yml -n production
```

Get a list of Pods:
```Shell
kubectl get pods -n production
```

### Disposability with Stateless Containers
IX. Disposability
Maximize robustness with fast startup and graceful shutdown

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215259805-1082%20-%20S04L02%20IX.%20Disposability%20with%20Stateless%20Containers.pdf)  
[Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)  
[Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)  

Deployments can be used to maintain a specified number of running replicas automatically replacing pods that fail or are deleted.

Get a list of Pods:
```Shell
kubectl get pods -n production
```

Locate one of the Pods from the my-app deployment and copy the Pod's name.  
Delete the Pod using the Pod name:
```Shell
kubectl delete pod <Pod name> -n production
```

Get the list of Pods again. You will notice that the deployment is automatically creating a new Pod to replace the one that was deleted:
```Shell
kubectl get pods -n production
```

### Dev/Prod Parity with Namespaces
X. Dev/prod parity
Keep development, staging, and production as similar as possible

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215371092-1082%20-%20S05L01%20X.%20Dev%3AProd%20Parity%20with%20Namespaces.pdf)
[Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)  

k8s namespaces allow us to have multiple environments in the same cluster. A namespace is like a virtual cluster.

Create a new namespace:
```Shell
kubectl create namespace dev
```

Make a copy of the my-app app YAML:
```
cp my-app.yml my-app-dev.yml
```

`NodePort` `services` need to be unique within the cluster. We need to choose unique ports so dev doesn't conflict with production.  
Edit the my-app-svc service in the `my-app-dev.yml` file to select different `nodePort`s. You will also need to edit the my-app-config ConfigMap to reflect the new port. 
Set the nodePorts on the service:
```Shell
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

Update the configured port in the ConfigMap:
```Shell
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
```Shell
kubectl apply -f k8s-my-app-mongodb.yml -n dev
kubectl apply -f my-app-mongodb.yml -n dev
```

Deploy the app in the new namespace:
```Shell
kubectl apply -f my-app-dev.yml -n dev
```
Check the status of the Pods:
```Shell
kubectl get pods -n dev
```

Once all the Pods are up and running, you should be able to test the dev environment in a browser at  
```<Control Plane Node Public IP>:30082```.

### Logs with k8s Container Logging
XI. Logs
Treat logs as event streams

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215382492-1082%20-%20S05L02%20XI.%20Logs%20with%20k8s%20Container%20Logging.pdf)  
[Logging Architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)  
[Kubectl cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/#interacting-with-running-pods)  

k8s captures log data written to stdout by containers. We can use the k8s API, `kubectl logs` or external tools to interact with container logs.  

Edit the source code for the server e.g. `src/server/index.js`. There is a log function that writes to a file. Change this function to simply write log data to the console:  
```Javascript
log = function(data) {
console.log(data);
}
```

Build a new server image because we changed the source code:
```Shell
docker build -t <Your Docker Hub username>/my-app-server:0.0.4 --target server .
```

Push the image:
```Shell
docker push <Your Docker Hub username>/my-app-server:0.0.4
```

Deploy the new code. Edit `my-app.yml`. Change the image version for the server to the new image:
```Shell
containers:
- name: my-app-server
  image: <Your Docker Hub username>/my-app-server:0.0.4
```

```Shell
kubectl apply -f my-app.yml -n production
```

Get a list of Pods:
```Shell
kubectl get pods -n production
```

Copy the name of one of the my-app deployment Pods and view its logs specifying the pod, namespace, and container.
```Shell
kubectl logs <Pod name> -n production -c my-app-server
```

### Admin Processes with Jobs
XII. Admin processes
Run admin/management tasks as one-off processes

[Reference](https://acloudguru-content-attachment-production.s3-accelerate.amazonaws.com/1631215407613-1082%20-%20S05L03%20XII.%20Admin%20Processes%20with%20Jobs.pdf)  
[Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)  

A `Job` e.g. a database migration runs a container until its execution completes. Jobs handle re-trying execution if it fails.  
Jobs have a `restartPolicy` of `Never` because once they complete they don't run again. 
This example adds the administrative job to the server image but you could package it into its own image.  

Edit the source code for the admin process in e.g. `src/jobs/deDeuplicateJob.js`.  
Locate the block of code that begins with // Setup MongoDb backing database .  
Change the code to make the database connection configurable:  

```Javascript
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
```Shell
...
COPY --from=build /usr/src/app/src/jobs .
```

Build and push the server image:
```Shell
docker build -t <Your Docker Hub username>/my-app-server:0.0.5 --target server .
docker push <Your Docker Hub username>/my-app-server:0.0.5
```

Create a Kubernetes Job to run the admin job:
Create `de-duplicate-job.yml`.
Supply your Docker Hub username in the image tag:
```Shell
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
```Shell
kubectl apply -f de-duplicate-job.yml -n production
```

Check the Job status:
```Shell
kubectl get jobs -n production
```
Get the name of the Job Pod:
```Shell
kubectl get pods -n production
```

Use the Pod name to view the logs for the Job Pod:
```Shell
kubectl logs <Pod name> -n production
```

## microk8s

[On Raspberry Pi](https://microk8s.io/docs/install-raspberry-pi)  
Note: Your boot parameters might be in `/boot/cmdline.txt`. Add these options at the end of the file, then `sudo reboot`.
```Shell
cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1
```

For Raspberry Pi OS [install](https://snapcraft.io/docs/installing-snap-on-raspbian) `snap` first.
```Shell
sudo apt update
sudo apt install snapd
sudo reboot
# ...reconnect after reboot
sudo snap install core
```
Then install microk8s.
```Shell
pi@raspberrypi4:~ $ sudo snap install microk8s --classic
pi@raspberrypi4:~ $ microk8s status --wait-ready
pi@raspberrypi4:~ $ microk8s kubectl get all --all-namespaces
pi@raspberrypi4:~ $ microk8s enable dns dashboard registry hostpath-storage # or any other addons
pi@raspberrypi4:~ $ alias mkctl="microk8s kubectl"
pi@raspberrypi4:~ $ mkctl create deployment nginx --image nginx
pi@raspberrypi4:~ $ mkctl expose deployment nginx --port 80 --target-port 80 --selector app=nginx --type ClustetIP --name nginx
pi@raspberrypi4:~ $ watch microk8s kubectl get all
pi@raspberrypi4:~ $ microk8s reset
pi@raspberrypi4:~ $ microk8s status
pi@raspberrypi4:~ $ microk8s stop # microk8s start
```

### Registry
[Registry doc](https://microk8s.io/docs/registry-built-in)
```Shell
microk8s enable registry
```
The containerd daemon used by MicroK8s is configured to trust this insecure registry. To upload images we have to tag them with localhost:32000/your-image before pushing them.

### Dashboard
If RBAC is not enabled access the dashboard using the token retrieved with:
```Shell
microk8s kubectl describe secret -n kube-system microk8s-dashboard-token
```
Use this token in the https login UI of the kubernetes-dashboard service.
In an RBAC enabled setup (microk8s enable RBAC) you need to create a user with restricted permissions as shown [here](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md)

### Troubleshooting
```Shell
microk8s inspect
```
microk8s might not recognize that cgroup memory is enabled but you can check with `cat /proc/cgroups`.


## Kubernetes Dashboard

[Documentation](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/)
```Shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.1/aio/deploy/recommended.yaml

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

kubectl apply -f dashboard-adminuser.yaml

kubectl proxy
# Kubectl will make Dashboard available at 
# http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

kubectl -n kubernetes-dashboard create token admin-user
# Now copy the token and paste it into the Enter token field on the login screen. 
```