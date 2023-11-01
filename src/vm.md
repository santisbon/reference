# Apple Silicon Macs

Free options:

* [Multipass](https://dev.to/santisbon/running-an-ubuntu-vm-on-apple-silicon-fem) - Supports Ubuntu VMs and cloud-init but does **not** support [attaching additional virtual disks](https://github.com/canonical/multipass/issues/2303).
    ```sh
    brew install --cask multipass
    ```
* [UTM](https://mac.getutm.app) - Supports multiple OSs and attaching virtual disks but does **not** support [cloud-init](https://github.com/utmapp/UTM/discussions/3618). If using a Linux **server** VM without a desktop, [clipboard sharing does not work](https://github.com/utmapp/UTM/issues/1204). You'll need to add a serial device to the VM. That way when the VM starts you'll get an extra console window and that one will have a [shared clipboard](https://docs.getutm.app/settings-qemu/sharing/). 
    ```sh
    brew install --cask utm
    ```