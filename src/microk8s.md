Suitable for Raspberry Pi and other lightweight environments. [Learn  more](https://microk8s.io/docs/install-raspberry-pi).

### Cloud native setup

#### Prerequisites

1. Set up your Raspberry Pi devices with `cloud-init` as defined in the [Raspberry Pi](/reference/rpi/) section.
2. Assign static IPs to all the nodes. 
3. `sudo nano /etc/hosts` on each node and add the IP and hostnames of the other nodes so they can resolve during the join process.

These are the high level steps we'll be following:

1. Create the storage cluster with MicroCeph.
2. Add all nodes to the MicroK8s cluster.
3. Connect the MicroK8s cluster to the Ceph cluster.
4. Enable the rook-ceph MicroK8s addon and any other addons you need.

#### MicroCeph Clustering

Ceph provides [block](https://docs.ceph.com/en/latest/rbd/), [object](https://docs.ceph.com/en/latest/radosgw/), and [file](https://docs.ceph.com/en/latest/cephfs/) storage. It supports both replicated and erasure coded storage.

1. Install [MicroCeph](https://microk8s.io/docs/how-to-ceph)
    ```sh title="On all nodes"
    sudo snap install microceph --channel=latest/edge
    snap info microceph # if you want to see instructions
    ```
    ```sh title="On the control plane node"
    sudo microceph cluster bootstrap
    ```
2. Join all nodes to the cluster
    ```sh title="On the control plane, for each node you want to add"
    sudo microceph cluster add $NODE_HOSTNAME
    # get the join token for the node
    ```
    It's best to have an [odd number of monitors](https://access.redhat.com/documentation/en-us/red_hat_ceph_storage/3/html/operations_guide/managing-the-storage-cluster-size) because Ceph needs a majority of monitors to be running e.g. 2 out of 3.
    ```sh title="On each node you want to add to the cluster"
    sudo microceph cluster join $JOIN_TOKEN
    ```
3. Allocate disks and add the disks as OSDs.
    ```sh title="On the control plane"
    sudo ceph status # microceph.ceph status
    # HEALTH_WARN with no OSDs
    ```
    ```sh title="On each node"
    # After adding physical or virtual disks to your node/VM
    # for each disk
    sudo microceph disk add /dev/sdb --wipe # whatever device name your disk has
    ```
    Alternatively, you can create virtual disks as loop devices (a special block device that maps to a file).
    ```sh title="On each node"
    for l in a b; do
        loop_file="$(sudo mktemp -p /mnt XXXX.img)"
        sudo truncate -s 60G "${loop_file}"
        loop_dev="$(sudo losetup --show -f "${loop_file}")"
        # the block-devices plug doesn't allow accessing /dev/loopX
        # devices so we make those same devices available under alternate
        # names (/dev/sdiY)
        minor="${loop_dev##/dev/loop}"
        sudo mknod -m 0660 "/dev/sdi${l}" b 7 "${minor}"
        sudo microceph disk add --wipe "/dev/sdi${l}"
    done
    ```
4. Verify
    ```sh title="On each node"
    lsblk
    ```
    ```sh title="On the control plane (or any ceph node, really)"
    sudo microceph status # deployment summary
    sudo microceph disk list
    sudo ceph osd metadata $OSD_ID | grep osd_objectstore # check that it's a bluestore OSD
    
    sudo ceph status # detailed status
    # HEALTH_OK with all OSDs showing
    
    sudo ceph osd pool ls detail -f json-pretty # list the pools with all details
    sudo ceph osd pool stats # obtain stats from all pools, or from specified pool
    ```
    Learn more about [pools](https://docs.ceph.com/en/latest/rados/operations/pools/).

#### MicroK8s Clustering

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

2. Connect your MicroK8s cluster to your MicroCeph cluster. We'll be using [Rook Ceph](https://rook.io/docs/rook/v1.12/Getting-Started/quickstart/#storage).
    ```sh title="On the control plane"
    microk8s enable rook-ceph
    microk8s kubectl --namespace rook-ceph get pods -l "app=rook-ceph-operator"
    # wait for the operator pod to be `Running`
    sudo microk8s connect-external-ceph
    ```

Now you can create a pod that uses the `ceph-rdb` storage class (which uses the `microk8s-rbd0` pool) for a persistent volume.  
But to get more control you can [provision and consume storage](https://rook.io/docs/rook/v1.12/Storage-Configuration/Block-Storage-RBD/block-storage/) by creating [`CephCluster`](https://github.com/rook/rook/blob/release-1.12/deploy/examples/cluster-external.yaml) and `CephBlockPool` CRs and a `StorageClass` as shown [here](#storage).

#### Configuration

```sh title="On your Pi"
# Check if MicroK8s is intalled and running with the addons enabled
microk8s status --wait-ready
microk8s kubectl cluster-info

# How to stop/start
microk8s stop
microk8s start

# Add-on Examples:
microk8s enable metrics-server
microk8s enable ingress
microk8s enable dashboard

# If you ever want to update MicroK8s to another channel. Tip: use a specific channel number.
snap info microk8s
sudo snap refresh microk8s --channel=latest/stable
```

##### Storage

Create the storage resources for your cluster using the info below.

1. Review needed info  
    Erasure Coding  

    <table>
        <tr><th>Data chunks (k)</th><th>Coding chunks (m)</th><th>Total storage</th><th>Losses Tolerated (m)</th><th>OSDs required (k+m)</th></tr>
        <tr><td>2</td><td>1</td><td>1.5x</td><td>1</td><td>3</td></tr>
        <tr><td>2</td><td>2</td><td>2x</td><td>2</td><td>4</td></tr>
        <tr><td>4</td><td>2</td><td>1.5x</td><td>2</td><td>6</td></tr>
        <tr><td>3</td><td>3</td><td>2x</td><td>3</td><td>6</td></tr>
        <tr><td>16</td><td>4</td><td>1.25x</td><td>4</td><td>20</td></tr>
    </table>

    ```sh title="On the control plane"
    # Verify the name and namespace of the secrets containing the Ceph cluster admin credentials
    microk8s kubectl get secret -A
    # To see the secrets
    ROOK_NAMESPACE=rook-ceph # rook-ceph-external
    microk8s kubectl get secret rook-csi-rbd-provisioner -n $ROOK_NAMESPACE -o jsonpath='{.data.userID}' | base64 --decode ;echo
    microk8s kubectl get secret rook-csi-rbd-provisioner -n $ROOK_NAMESPACE -o jsonpath='{.data.userKey}' | base64 --decode ;echo
    microk8s kubectl get secret rook-csi-rbd-node -n $ROOK_NAMESPACE -o jsonpath='{.data.userID}' | base64 --decode ;echo
    microk8s kubectl get secret rook-csi-rbd-node -n $ROOK_NAMESPACE -o jsonpath='{.data.userKey}' | base64 --decode ;echo
    ```

2. Download the resource files, adjust for your environment, and apply them.
    ```sh title="On the control plane"
    # To view all resources not included in kubectl get all
    microk8s kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 microk8s kubectl get --ignore-not-found --show-kind -n rook-ceph-external
    microk8s kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 microk8s kubectl get --ignore-not-found --show-kind -n rook-ceph

    wget https://raw.githubusercontent.com/santisbon/reference/main/assets/rook-cluster-external.yaml
    microk8s kubectl apply -f rook-cluster-external.yaml

    wget https://raw.githubusercontent.com/santisbon/reference/main/assets/rook-storage-external.yaml
    microk8s kubectl apply -f rook-storage-external.yaml

    microk8s kubectl get sc -A
    microk8s kubectl get CephCluster -A
    microk8s kubectl get CephBlockPool -A

    microk8s kubectl describe sc -A
    microk8s kubectl describe CephCluster -A
    microk8s kubectl describe CephBlockPool -A
    ```

### Manual setup

!!! attention
    MicroK8s is not available for 32-bit architectures like `armhf`(`arm/v7`), only on 64-bit architectures like `arm64` and `amd64`.

!!! attention 
    On Raspberry Pi your boot parameters file might be in `/boot/cmdline.txt` or in `/boot/firmware/cmdline.txt`. Find it with `sudo find /boot -name cmdline.txt`.  

On Raspberry Pi you need to enable c-groups so the kubelet will work out of the box.  
Add these options at the end of the file, then `sudo reboot`. Some users report needing `cgroup_enable=cpuset` as well but try adding only these:
``` title="cmdline.txt"
cgroup_enable=memory cgroup_memory=1
```

!!! attention
    On Orange Pi boards these parameters are handled in `/boot/boot.cmd` by checking:  
    `if test "${docker_optimizations}" = "on"`.  

    Don't edit this file, instead `sudo nano /boot/orangepiEnv.txt` and set `docker_optimizations` to `on`.

If your image doesn't already include it, [install](https://snapcraft.io/docs/installing-snap-on-raspbian) `snap`.
```zsh title="On your Pi"
sudo apt update
sudo apt install snapd
sudo reboot
# ...reconnect after reboot
sudo snap install core
```

Then install MicroK8s.
```zsh title="On your Pi"
sudo snap install microk8s --classic
```

To run commands without `sudo` add the user to the `microk8s` group. Example:
```zsh title="On your Pi"
sudo usermod -a -G microk8s pi
sudo chown -R pi ~/.kube
newgrp microk8s
```

Usage:
```zsh title="On your Pi"
microk8s status --wait-ready
microk8s kubectl get all --all-namespaces
# default addons are: dns ha-cluster helm helm3. You can enable more
# but preferably enable them one by one
microk8s enable dashboard ingress metrics-server 
alias mkctl="microk8s kubectl"
alias mkhelm="microk8s helm"
mkctl version --output=yaml
watch microk8s kubectl get all
microk8s reset
microk8s status
microk8s stop # microk8s start
```

You can update a snap package with `sudo snap refresh`.

Configuration file. These are the arguments you can add regarding log rotation `--container-log-max-files` and `--container-log-max-size`. They have default values. [More info](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/).
```zsh
cat /var/snap/microk8s/current/args/kubelet
```

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

* I see `cloud-init` had failures.  
    Based on the `user-data` file:
    Manually run `sudo apt update`, `sudo apt full-upgrade`.  
    Manually run `sudo apt install` on any packages that failed.  
    Manually add any kernel modules you need and make sure `/etc/modules-load.d/modules.conf` has them so they'll be added on every boot.

* I want to check all k8s endpoints or inspect the instance.
    ```sh
    microk8s kubectl get endpoints -A
    microk8s inspect
    ```
* I'm not sure cgroups are enabled.  
    MicroK8s might not recognize that cgroup memory is enabled but you can check with 
    ```sh
    cat /proc/cgroups
    ```
* For other issues see [https://microk8s.io/docs/troubleshooting](https://microk8s.io/docs/troubleshooting)
