# Rook Ceph

Make sure you meet the [prerequisites](https://rook.io/docs/rook/v1.12/Getting-Started/Prerequisites/prerequisites/). It's recommended to add another disk for Ceph storage instead of trying to resize the root partition or prevent it from expanding to the entire disk.
```sh
lsmod | grep rbd 
# if not present:
sudo apt install linux-modules-extra-$(uname -r) 

sudo apt install lvm2
microk8s kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.11.1/cert-manager.yaml
```

Use `parted` to set up/resize the SSD partitions and file systems as desired. For example, leave a raw partition (no formatted filesystem) for use by a Ceph storage cluster.  

1. [Resize the filesystem](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_file_systems/getting-started-with-an-ext4-file-system_managing-file-systems#resizing-an-ext4-file-system_getting-started-with-an-ext4-file-system).
2. If needed, [shrink the partition](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_file_systems/partition-operations-with-parted_managing-file-systems#proc_resizing-a-partition-with-parted_partition-operations-with-parted) to leave space to be used by Ceph.


