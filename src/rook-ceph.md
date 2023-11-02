# Rook Ceph

Make sure you meet the [prerequisites](https://rook.io/docs/rook/v1.12/Getting-Started/Prerequisites/prerequisites/). You can resize the root partition and create a raw partition for Ceph to use but if possible, add another disk for Ceph storage instead.
```sh
lsmod | grep rbd 
# if not present:
sudo apt install linux-modules-extra-$(uname -r) 

sudo apt install lvm2
microk8s kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.11.1/cert-manager.yaml
```

