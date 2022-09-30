# Docker

## Install

### macOS
```Shell
brew install --cask docker
```
* You must use the --cask version. Otherwise only the client is included and can't run the Docker daemon. Then open the Docker app and grant privileged access when asked. Only then will you be able to use docker.

### Linux:  
```Shell
curl https://get.docker.com > /tmp/install.sh
chmod +x /tmp/install.sh
/tmp/install.sh
```

If you don't want to have to prefix commands with sudo add your user to the `docker` group. This is equivalent to giving that user root privileges.
```Shell
sudo usermod -aG docker
```

On Ubuntu this may mess up DNS resolution. To fix it: (To-Do).

## Use

### Architecture

[Supported Architectures](https://github.com/docker-library/official-images#architectures-other-than-amd64)  

[Platform specifiers](https://github.com/containerd/containerd/blob/v1.4.3/platforms/platforms.go#L63)  

| Value   | Normalized |                 | 
| :-----: | :--------: | :-------------: |
| aarch64 | arm64      | M1/M2           |
| armhf   | arm        |                 |
| armel   | arm/v6     |                 |   
| i386    | 386        |                 |
| x86_64  | amd64      | Default (Intel) |
| x86-64  | amd64      | Default (Intel) |

Docker Desktop for Apple silicon can run (or build) an Intel image using emulation.  
The ```--platform``` option sets the platform if server is multi-platform capable.  

Macbook **M1/M2** is based on **ARM**. The Docker host is detected as **linux/arm64/v8** by Docker.  

On a Macbook M1/M2 running a native arm64 linux image instead of an amd64 (x86-64 Intel) image with emulation:  
When installing apps on the container either install the package for the ARM platform if they provide one, or run an amd64 docker image (Docker will use emulation). 

See Docker host info.  
You need to use the real field names (not display names) so we'll grab the info in json to get the real field names and use ```jq``` to display it nicely. Then we'll render them using Go templates.

```Shell
docker info --format '{{json .}}' | jq .

docker info --format "{{.Plugins.Volume}}"
docker info --format "{{.OSType}} - {{.Architecture}} CPUs: {{.NCPU}}"
```

With the default images, Docker Desktop for Apple silicon warns us the requested image's platform (linux/amd64) is different from the detected host platform (linux/arm64/v8) and no specific platform was requested.  
```--platform linux/amd64``` is the default and the same as  ```--platform linux/x86_64```. It runs (or builds) an Intel image.  
```--platform linux/arm64``` runs (or builds) an aarch64 (arm64) image. Architecture used by Appple M1/M2.  

```Shell
docker run -it --name container1 debian # WARNING. uname -m -> x86_64 (amd64)
docker run -it --platform linux/amd64 --name container1 debian # NO warning. uname -m -> x86_64 (amd64). On Mac it emulates Intel.
docker run -it --platform linux/arm64 --name container1 debian # NO warning. uname -m -> aarch64 (arm64). Mac native.

# On a Mac M2 you can also use this image
docker run -it --name mycontainer arm64v8/debian bash # NO warning. uname -m -> aarch64 (arm64). Mac native.
```


### Examples

Running containers
```Shell
# sanity check
docker version
docker --help

# "docker run" = "docker container run"

docker run --name container1 debian # created and Exited
docker run -it --name container2 debian # created and Up. Interactive tty
docker run --detach --name container3 debian # created and Exited
docker run -it --detach --name container4 debian # created and Up. Running in background

docker stop container4 # Exited
docker restart container4 # Up
docker attach container4 # Interactive tty

# To have it removed automatically when it's stopped 
docker run -it --rm --name mycontainer debian # created and Up. Interactive tty. 

# Run bash in a new container with interactive tty, based on debian image.
docker run -it --name mycontainer debian bash

# Get the IDs of all stopped containers. Options: all, quiet (only IDs), filter.
docker ps -aq -f status=exited

```

Working with images and volumes
```Shell

# Show all images (including intermediate images)
docker image ls -a

# Build an image from a Dockerfile and give it a name (or name:tag).
docker build -f mydockerfile -t santisbon/myimage .
docker builder prune -a		# Remove all unused build cache, not just dangling ones

# Volumes
docker volume create my-vol
docker volume ls
docker volume inspect my-vol
docker volume prune
docker volume rm my-vol

# Start a container from an image.
docker run \
--name mycontainer \
--hostname mycontainer \
--mount source=my-vol,target=/data \
santisbon/myimage

# Get rid of all stopped containers. Options: remove **anonymous volumes** associated with the container.
docker rm -v $(docker ps -aq -f status=exited)
# You might want to make an alias:
alias drm='docker rm -v $(docker ps -aq -f status=exited)'
# or
alias drm='sudo docker rm -v $(sudo docker ps -aq -f status=exited)'

# on macOS the volume mountpoint (/var/lib/docker/volumes/) is in the VM that Docker Desktop uses to provide the Linux environment.
# You can read it through a container given extended privileges. 
# Use: 
# - the "host" PID namespace, 
# - an image e.g. debian, 
# - the nsenter command to run a program (sh) in a different namespace
# - the target process with PID 1
# - enter following namspaces of the target process: mount, UTS, network, IPC.
docker run -it --privileged --pid=host debian nsenter -t 1 -m -u -n -i sh
```