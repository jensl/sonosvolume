# Sonos volume controller

This is a simple web-app for controlling the volume setting on Sonos speakers
on the local network.

It's meant to run in a Docker container. For instructions on how to get started
with Docker, if you're unfamiliar, see https://docs.docker.com/get-started/.

## Building

Either clone this repository, and run

```
$ docker build -t sonosvolume .
```

in the root directory, or run

```
$ docker build -t sonosvolume https://github.com/jensl/sonosvolume.git
```

to build from the Git repository without creating a clone manually.

### Configuration

There are some ways to configure the web-app; specifying the port at which it
listens, specifying the address of the network interface on which to
auto-discover speakers, and manually specifying a list of speakers by IP
address.

Overriding the discovery interface may be necessary when running the web-app
on a machine connected to multiple networks, since it might otherwise try to
discover speakers on the wrong network.

Manually specifying speakers may be necessary if auto-discovery doesn't work at
all for some reason, or if not all speakers should be included.

#### Listen port

To specify the listen port, add the build argument `port` to the `docker build`
command:

```
$ docker build --build-arg port=8080 ...
```

If no `port` build argument is specified, the web-app will run on port `8080`.

#### Discover interface

To specify the discover interface, add the build argument `discover_if` to the
`docker build` command:

```
$ docker build --build-arg discover_if=192.168.1.1 ...
```

where `192.168.1.1` should be replaced with the system's IP address on the
network it shares with the Sonos system.

#### Speaker addresses

To manually specify the address of Sonos speakers to control, add the build
argument `speakers` to the `docker build` command:

```
$ docker build --build-arg speakers=192.168.1.2,192.168.1.3 ...
```

The argument value should be a comma-separated list of full IP addresses (not
DNS names). There should be no white-space.

Note that specifying the `speakers` build argument disables auto-discovery of
speakers.

## Running

To start the web-app, run the command

```
$ docker run --detach --network=host --name=sonosvolume sonosvolume:latest
```

This command is also executed by the script `start` in this repository.

The `--network=host` argument is typically necessary at least for auto-
discovery to work.

The `--name=sonosvolume` argument names the container, to make it easier to
address later on, e.g. when stopping it.

## Stopping, restarting and destroying

To stop and restart the web-app container, run the commands

```
$ docker stop sonosvolume
$ docker start sonosvolume
```

To destroy the container, e.g. to restart with a new version of the image,
run the command

```
$ docker rm sonosvolume
```
