Suitable for Raspberry Pi and other lightweight environments. [Learn  more](https://microk8s.io/docs/install-raspberry-pi).

### Prerequisites

1. Set up your Raspberry Pi devices with `cloud-init` as defined in the [Raspberry Pi](/reference/rpi/) section.
2. Assign static IPs to all the nodes. 
3. `sudo nano /etc/hosts` on each node and add the IP and hostnames of the other nodes so they can resolve during the join process.

!!! attention
    MicroK8s is not available for 32-bit architectures like `armhf`(`arm/v7`), only on 64-bit architectures like `arm64` and `amd64`.

If your OS doesn't already include it, [install](https://snapcraft.io/docs/installing-snap-on-raspbian) `snap` before installing MicroK8s.
```sh title="On each node"
sudo apt update
sudo apt install snapd
sudo reboot
# ...reconnect after reboot
sudo snap install core
```

### Clustering

1. [Add all nodes to the cluster](https://microk8s.io/docs/clustering).  
    ```sh title="On the control plane node"
    microk8s add-node
    ```
    You can add it as a worker-only node
    ```sh title="On each node you want to add to the cluster"
    microk8s join $JOIN_STRING --worker
    ```

    ```sh title="On the control plane node"
    microk8s kubectl get no
    ```

2. Connect the MicroK8s cluster to an external Ceph cluster or deploy Ceph to your MicroK8s cluster. We'll use [Rook Ceph](https://rook.io/docs/rook/v1.12/Getting-Started/quickstart/#storage) to operate the Ceph cluster.
    ```sh title="On the control plane"
    microk8s enable rook-ceph # installs crds.yaml, common.yaml, operator.yaml
    microk8s kubectl --namespace rook-ceph get pods -l "app=rook-ceph-operator"
    # wait for the operator pod to be `Running`
    ```

    **Option 1** - If you set up an external MicroCeph cluster:
    ```sh title="On the control plane node"
    sudo microk8s connect-external-ceph
    ```
    Now you can create a pod that uses the `ceph-rdb` storage class, which uses the `microk8s-rbd0` pool.

    **Option 2** - To deploy [Ceph on the MicroK8s cluster using storage from the k8s nodes](https://rook.io/docs/rook/latest-release/CRDs/Cluster/ceph-cluster-crd/)
    ```sh title="On the control plane node"
    # if you want `dataDirHostPath` to specify where config and data should be stored for each of the services
    microk8s enable hostpath-storage
    ```
    Create the cluster and storage resources like in these [examples](https://rook.io/docs/rook/v1.12/Getting-Started/example-configurations/#cluster-crd). You'll probably want a customized version to match your environment.
    ```sh title="On the control plane node"
    wget https://raw.githubusercontent.com/rook/rook/d34d443e0fa2fc946dd56fd2b66968380e68f449/deploy/examples/cluster.yaml
    wget https://raw.githubusercontent.com/rook/rook/d34d443e0fa2fc946dd56fd2b66968380e68f449/deploy/examples/csi/rbd/storageclass.yaml
    wget https://raw.githubusercontent.com/rook/rook/d34d443e0fa2fc946dd56fd2b66968380e68f449/deploy/examples/csi/rbd/storageclass-ec.yaml

    microk8s kubectl apply -f cluster.yaml
    microk8s kubectl get CephCluster -A # wait for the cluster to be `Ready`

    # block devices    
    microk8s kubectl apply -f storageclass.yaml
    microk8s kubectl apply -f storageclass-ec.yaml
    microk8s kubectl get CephBlockPool -A
    microk8s kubectl get StorageClass -A
    ```
    If the `CephBlockPool` creation fails, see [here](https://rook.io/docs/rook/v1.12/Troubleshooting/ceph-common-issues/#investigation_4).

    (Optional) It's good to install the [Rook toolbox](https://rook.io/docs/rook/v1.12/Troubleshooting/ceph-toolbox/) container for running Ceph commands.
    ```sh
    wget https://raw.githubusercontent.com/rook/rook/d34d443e0fa2fc946dd56fd2b66968380e68f449/deploy/examples/toolbox.yaml
    microk8s kubectl apply -f toolbox.yaml
    # Wait for the toolbox pod to download its container and get to the running state:
    microk8s kubectl -n rook-ceph rollout status deploy/rook-ceph-tools
    # Connect to it:
    microk8s kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash
    # you can use e.g. ceph status, ceph osd status, ceph osd pool stats, ceph df, rados df
    ```

### Usage

```sh title="On the control plane node"
# Check if MicroK8s is intalled and running with the addons enabled
microk8s status --wait-ready
microk8s kubectl cluster-info
microk8s kubectl get all --all-namespaces
watch microk8s kubectl get all

# How to stop/start
microk8s reset
microk8s stop
microk8s start

# Add-on examples:
microk8s enable metrics-server
microk8s enable ingress
microk8s enable dashboard

# If you ever want to update MicroK8s to another channel. Tip: use a specific channel number.
snap info microk8s
sudo snap refresh microk8s --channel=latest/stable

# storage classes
microk8s kubectl get sc -A
microk8s kubectl describe sc -A

alias mkctl="microk8s kubectl"
alias mkhelm="microk8s helm"
mkctl version --output=yaml

# Arguments for log rotation `--container-log-max-files` and `--container-log-max-size`. They have default values. 
cat /var/snap/microk8s/current/args/kubelet
```
[More info](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/).

### Deploying workloads

```sh
# StorageClass is ceph-rbd or rook-ceph-block, depending on your setup.
cat << EOF > pod.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pod-pvc
spec:
  storageClassName: ceph-rbd
  accessModes: 
    - ReadWriteOnce
  resources: 
    requests: 
      storage: 5Gi

---

apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  volumes:
    - name: nginx-vol
      persistentVolumeClaim:
        claimName: pod-pvc
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        - containerPort: 80
      volumeMounts:
        - name: nginx-vol
          mountPath: /usr/share/nginx/html
EOF

microk8s kubectl apply -f pod.yaml

microk8s kubectl get pvc -A # pvc status should be `Bound`
microk8s kubectl get pod

microk8s kubectl describe pvc pod-pvc
microk8s kubectl describe pod nginx

microk8s kubectl exec -it nginx -- bash

microk8s kubectl delete -f pod.yaml # cleanup
```

### Other SBCs/OSs

!!! attention 
    Your boot parameters file might be in `/boot/cmdline.txt` or in `/boot/firmware/cmdline.txt`. Find it with `sudo find /boot -name cmdline.txt`.  

!!! attention
    On Orange Pi boards cgroups are handled in `/boot/boot.cmd` by checking:  
    `if test "${docker_optimizations}" = "on"`.  

    Don't edit this file, instead `sudo nano /boot/orangepiEnv.txt` and set `docker_optimizations` to `on`.

### Dashboard

If RBAC is not enabled access the dashboard using the token retrieved with:
```zsh
microk8s kubectl describe secret -n kube-system microk8s-dashboard-token
```
Use this token in the https login UI of the `kubernetes-dashboard` service.
In an RBAC enabled setup (`microk8s enable rbac`) you need to create a user with restricted permissions as shown [here](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md).

To access remotely from outside the cluster:

#### Option A: [`port-forward`](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#port-forward)
  
Note: `kubectl port-forward` [does not return](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/). To type other commands, you'll need to open another terminal.
```zsh
microk8s kubectl port-forward -n kube-system service/kubernetes-dashboard 10443:443 --address 0.0.0.0
```
You can then access the Dashboard with IP or hostname and the forwarded port as in  
`https://raspberrypi4.local:10443/`

#### Option B: `NodePort`
Make the dashboard service a `NodePort` service by changing `type: ClusterIP` to `type: NodePort`.
```zsh
KUBE_EDITOR=nano microk8s kubectl -n kube-system edit service kubernetes-dashboard
# If using vim:
# Enter insert mode with i
# Enter command mode with esc 
# :q! to abort changes 
# :wq to save and exit

microk8s kubectl -n kube-system get service kubernetes-dashboard
```
You can then access the Dashboard with IP or hostname and the automatically assigned `NodePort` as in  
`https://raspberrypi4.local:30772`

### Registry
[Registry doc](https://microk8s.io/docs/registry-built-in)
```zsh
microk8s enable registry
```
The containerd daemon used by MicroK8s is configured to trust this insecure registry. To upload images we have to tag them with `localhost:32000/your-image` before pushing them.

### Other storage addons:
I recommend Ceph for block, file, and object storage but if you want alternatives:

#### OpenEBS

Prerequisite knowledge:
[Huge Pages](https://help.ubuntu.com/community/KVM%20-%20Using%20Hugepages)
[NVMe over Fabrics (NVMe-oF)](https://www.techtarget.com/searchstorage/definition/NVMe-over-Fabrics-Nonvolatile-Memory-Express-over-Fabrics)

Enable:
[Mayastor](https://microk8s.io/docs/addon-mayastor)  
Mayastor will run for all nodes in your MicroK8s cluster by default.

```sh
microk8s enable core/mayastor --default-pool-size 20G

# For Mayastor OpenEBS
# On first boot, the etcd-operator-mayastor pod may be stuck in CrashLoopBackOff state until you reboot
microk8s kubectl get pod -n mayastor 
microk8s kubectl get diskpool -n mayastor

```

#### MinIO

Concepts:  
[https://min.io/docs/minio/linux/operations/concepts.html](https://min.io/docs/minio/linux/operations/concepts.html)

Enable:
[MinIO](https://microk8s.io/docs/addon-minio)  

Usage: `microk8s enable minio [OPTIONS]`
```sh
   -h               Print this help message  
   -k               Do not create default tenant  
   -s STORAGECLASS  Storage class to use for the default tenant (default: microk8s-hostpath)  
   -c CAPACITY      Capacity of the default tenant (default: 20Gi)  
   -n SERVERS       Servers of the default tenant (default: 1)  
   -v VOLUMES       Volumes of the default tenant (default: 1)  
   -t TENANTNAME    Name of the default tenant (default: microk8s)  
   -T               Enable TLS for the default tenant (default: disabled)  
   -p               Enable Prometheus for the default tenant (default: disabled)  
   -r REPOSITORY    Minio Operator GitHub repository (default: https://github.com/minio/operator)  
   -V VERSION       Minio Operator version (default: 4.5.1)  
```
Example with 1 server and 1 volume per server (volumes should be a multiple of servers):
```sh
microk8s enable minio -c 100Gi

# Create a port-forward for the MinIO console with:
microk8s kubectl-minio proxy
```

Filesystem type to use:  
[https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-multi-drive.html](https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-multi-drive.html)

Check status for tenant named *microk8s*
```sh
sudo microk8s kubectl-minio tenant status microk8s
```

### Troubleshooting

* I want to check all k8s endpoints or inspect the instance.
    ```sh
    microk8s kubectl get endpoints -A
    microk8s inspect
    ```
* For other issues see [https://microk8s.io/docs/troubleshooting](https://microk8s.io/docs/troubleshooting)
* View logs
    ```sh
    sudo ls -al /var/snap/microk8s/common/var/log
    ```
* Common issues [https://rook.io/docs/rook/latest/Troubleshooting/common-issues/](https://rook.io/docs/rook/latest/Troubleshooting/common-issues/)
    ```sh title="On the control plane"
     # Inspect the Rook operator container’s logs:
    microk8s kubectl -n rook-ceph logs -l app=rook-ceph-operator
    # Inspect the ceph-mgr container’s logs:
    microk8s kubectl -n rook-ceph logs -l app=rook-ceph-mgr

    # To view all resources not included in kubectl get all
    microk8s kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 microk8s kubectl get --ignore-not-found --show-kind -n rook-ceph-external
    microk8s kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 microk8s kubectl get --ignore-not-found --show-kind -n rook-ceph

    # secrets
    microk8s kubectl get secret rook-csi-rbd-provisioner -n $ROOK_NAMESPACE -o jsonpath='{.data.userID}' | base64 --decode ;echo
    microk8s kubectl get secret rook-csi-rbd-provisioner -n $ROOK_NAMESPACE -o jsonpath='{.data.userKey}' | base64 --decode ;echo
    microk8s kubectl get secret rook-csi-rbd-node -n $ROOK_NAMESPACE -o jsonpath='{.data.userID}' | base64 --decode ;echo
    microk8s kubectl get secret rook-csi-rbd-node -n $ROOK_NAMESPACE -o jsonpath='{.data.userKey}' | base64 --decode ;echo
    ```
* Pods stuck in `ImagePullBackOff`. Errors pulling images or other resources.  
  Make sure the nodes are not running `avahi-daemon` as it messes with name resolution. Check if you're able to pull an image with k8s `crictl` or MicroK8s `ctr`.
    ```sh
    microk8s ctr image ls
    microk8s ctr image pull registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.7.0
    ```
* Connecting an external Ceph cluster to MicroK8s throws *Error: INSTALLATION FAILED: failed to download "rook-release/rook-ceph-cluster"*.  
    ```sh
    microk8s helm pull rook-release/rook-ceph-cluster
    microk8s helm install rook-ceph-external rook-ceph-cluster-v1.12.7.tgz -n rook-ceph-external
    # If you wish to delete this cluster and start fresh, you will also have to wipe the OSD disks using `sfdisk`
    ```
