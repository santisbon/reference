If using an external Ceph cluster to be consumed by Rook.

## Overview

Ceph provides [block](https://docs.ceph.com/en/latest/rbd/), [object](https://docs.ceph.com/en/latest/radosgw/), and [file](https://docs.ceph.com/en/latest/cephfs/) storage. It supports both replicated and erasure coded storage.

We'll work with `CephCluster`, `CephBlockPool` objects, the `rook-ceph.rbd.csi.ceph.com` provisioner pods, the `ceph-rbd` storage class and the Ceph operator pod.

**Option 1**  

Imports external MicroCeph cluster.

Components:

- MicroCeph cluster.
- MicroK8s cluster with rook-ceph addon connected to the external Ceph cluster.
- Ceph cluster with pools e.g.
    ```sh
    pool 2 'microk8s-rbd0' replicated size 3 min_size 2 crush_rule 1 object_hash rjenkins pg_num 32 pgp_num 32 autoscale_mode on last_change 31 lfor 0/0/29 flags hashpspool stripe_width 0 application rbd
    ```
- Kubernetes `StorageClass` objects with paramter `pool=mypool` e.g.
    ```
    Name:                  ceph-rbd
    Provisioner:           rook-ceph.rbd.csi.ceph.com
    Parameters:            clusterID=rook-ceph-external,pool=microk8s-rbd0 ...
    ```

**Option 2**

Deploy Ceph on MicroK8s.

Components:

- MicroK8s cluster with rook-ceph addon.
- Deploy Ceph on the MicroK8s cluster using storage from the k8s nodes.
- Not recommended for clusters with virtual disks backed by loop devices. The `provision` container of the `rook-ceph-osd-prepare` pod for each node will not use them and the pool creation will fail with `skipping OSD configuration as no devices matched the storage settings for this node `.


## Prerequisites

1. Allocate disks. For a MicroCeph test cluster with only 1 node you can create virtual disks as loop devices (a special block device that maps to a file).
    ```sh title="On each node"
    for l in a b c; do
        loop_file="$(sudo mktemp -p /mnt XXXX.img)"
        sudo truncate -s 60G "${loop_file}"
        loop_dev="$(sudo losetup --show -f "${loop_file}")"
        # the block-devices plug doesn't allow accessing /dev/loopX
        # devices so we make those same devices available under alternate
        # names (/dev/sdiY)
        minor="${loop_dev##/dev/loop}"
        sudo mknod -m 0660 "/dev/sdi${l}" b 7 "${minor}"
    done
    ```
    Verify
    ```sh title="On each node"
    lsblk
    ls -al  /dev/sdi*
    ```
2. Review storage concepts like replication vs erasure coding.  
    Erasure Coding  

    <table>
        <tr><th>Data chunks (k)</th><th>Coding chunks (m)</th><th>Total storage</th><th>Losses Tolerated (m)</th><th>OSDs required (k+m)</th></tr>
        <tr><td>2</td><td>1</td><td>1.5x</td><td>1</td><td>3</td></tr>
        <tr><td>2</td><td>2</td><td>2x</td><td>2</td><td>4</td></tr>
        <tr><td>4</td><td>2</td><td>1.5x</td><td>2</td><td>6</td></tr>
        <tr><td>3</td><td>3</td><td>2x</td><td>3</td><td>6</td></tr>
        <tr><td>16</td><td>4</td><td>1.25x</td><td>4</td><td>20</td></tr>
    </table>

## Setup

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
3. Add the disks as OSDs. MicroCeph supports loop devices or disks. At the time of this writing it does not support partitions but [that will change](https://github.com/canonical/microceph/issues/146).
    ```sh title="On each node"
    # After adding physical or virtual disks to your node/VM
    # for each disk (whatever device names your disks have)
    sudo microceph disk add /dev/sdia --wipe 
    sudo microceph disk add /dev/sdib --wipe
    sudo microceph disk add /dev/sdic --wipe
    ```
4. Verify
    ```sh title="On the control plane (or any ceph node, really)"
    sudo ceph status # detailed status
    # HEALTH_OK with all OSDs showing
    ```
    Learn more about [pools](https://docs.ceph.com/en/latest/rados/operations/pools/).

You can also [create](https://docs.ceph.com/en/latest/rados/operations/pools/#creating-a-pool) and [initialize](https://docs.ceph.com/en/latest/rbd/rados-rbd-cmds/) other Ceph pools.

## Usage

```sh
# Ceph
sudo microceph status # deployment summary
sudo microceph disk list
sudo ceph osd metadata {osd-id} | grep osd_objectstore # check that it's a bluestore OSD
sudo ceph osd lspools
sudo ceph osd pool ls
sudo ceph osd pool ls detail -f json-pretty # list the pools with all details
sudo ceph osd pool stats # obtain stats from all pools, or from specified pool
sudo ceph osd pool delete {pool-name} {pool-name} --yes-i-really-really-mean-it
```

## Troubleshooting

* View logs
    ```sh
    sudo ls -al /var/snap/microceph/common/logs/
    ```