Suitable for Raspberry Pi and other lightweight environments. [Architecture](https://docs.k3s.io/architecture).

## Prerequisites

1. Set up your Raspberry Pi devices with `cloud-init` as defined in the [Raspberry Pi](/reference/rpi/) section.
2. Assign static IPs to all the nodes. 
3. `sudo nano /etc/hosts` on each node and add the IP and hostnames of the other nodes so they can resolve during the join process.

## Installation

* [Ubuntu/Debian requirements](https://docs.k3s.io/advanced#ubuntu--debian).
* [Installation](https://docs.k3s.io/installation).

[Configuration](https://docs.k3s.io/installation/configuration) file to be used on install instead of CLI arguments. Use the version of [iptables](https://docs.k3s.io/advanced#old-iptables-versions) bundled with K3s.
```sh title="On the node being configured"
cat << EOF > /etc/rancher/k3s/config.yaml
prefer-bundled-bin: true
cluster-init: true
EOF
```

[CLI tools](https://docs.k3s.io/cli).

### [Addons](https://docs.k3s.io/installation/packaged-components)

Any manifest found in `/var/lib/rancher/k3s/server/manifests` is tracked as an `AddOn` custom resource in the `kube-system` namespace.  
Included: `coredns`, `traefik`, `local-storage`, and `metrics-server`. You can put your own files in the manifests dir for deployment as an `AddOn`.

!!! note
    The embedded `servicelb` LoadBalancer controller does not have a manifest file, but can be disabled as if it were an `AddOn`.

View any warnings encountered with:
```sh
kubectl get event -n kube-system
# or
kubectl describe {AddOn resource}
```

!!! important
    It's your responsibility to ensure that files stay in sync across server nodes.

### Datastore

* Embedded SQLite - Default. For clusters with only 1 server (control plane) node.
* [Embedded etcd](https://docs.k3s.io/datastore/ha-embedded) - Allows HA with multiple server nodes.
* External database - - Allows HA with multiple server nodes. Supports etcd, MySQL, MariaDB, PostgreSQL.

### Service

```sh title="Server node (control plane)"
ufw disable
sudo apt install linux-modules-extra-raspi

curl -sfL https://get.k3s.io | sh -
```
```sh
SERVER=`uname -n`
TOKEN=`cat /var/lib/rancher/k3s/server/node-token`
```

```sh title="Agent node (worker node)"
ufw disable
sudo apt install linux-modules-extra-raspi

curl -sfL https://get.k3s.io | K3S_URL=https://$SERVER:6443 K3S_TOKEN=$TOKEN sh -
```

`curl`

* `s`ilent, no progress meter or error messages.
* `f`ail silently on server errors.
* If moved, redo the request on the new `L`ocation.

`sh`

* `-s` Read commands from standard input.
* A `--` signals the end of options.
* Any arguments after the `--` are treated as filenames and arguments.  
* An argument of `-` is equivalent to `--`.

Checking the service with systemd.  
Logs are in `/var/log/syslog`.  
Pod logs at `/var/log/pods`.  
Containerd logs at `/var/lib/rancher/k3s/agent/containerd/containerd.log`.
```sh title="On server nodes"
systemctl status k3s
journalctl -u k3s
```
```sh title="On agent nodes"
journalctl -u k3s-agent
```

When running with systemd, logs will be created in `/var/log/syslog` and viewed using journalctl -u k3s (or journalctl -u k3s-agent on agents).

## Deploying workloads

```sh title="On the control plane"
cat << EOF > ~/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: local-path-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 2Gi
EOF
```
```sh
cat << EOF > ~/pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-test
  namespace: default
spec:
  containers:
  - name: volume-test
    image: nginx:stable-alpine
    imagePullPolicy: IfNotPresent
    volumeMounts:
    - name: volv
      mountPath: /data
    ports:
    - containerPort: 80
  volumes:
  - name: volv
    persistentVolumeClaim:
      claimName: local-path-pvc
EOF
```
```sh
kubectl create -f pvc.yaml
kubectl create -f pod.yaml

kubectl get pv
kubectl get pvc
# The status should be `Bound` for each.
```

[Helm](https://docs.k3s.io/helm) is also supported through a controller that allows using a `HelmChart` CRD.