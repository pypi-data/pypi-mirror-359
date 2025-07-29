# MAAS dev env utilities

Helper I use to manage my MAAS dev environment.

It's based on a YAML configuration file, so it's easily extensible and configurable.

It provides 4 different commands:
- `init`: to init an lxd container and install MAAS on it with its dependencies
- `sync`: to sync changes with overlayfs (look at 'dirs' and 'files' in the yaml)
- `unsync`: to unmount the overlayfs
- `destroy`: to destroy the lxd container

# Install
You can install it through snap:
```sh
sudo snap install maas-dev-env --classic
```

Or build it locally, via [pipx](https://github.com/pypa/pipx) for example:
```sh
pipx install .
```

Then the command will be available as `maas-dev-env`.

# Usage

The script can be executed both inside the host and inside the container. It will automatically recognize it through the `hostname` command, so be careful when changing the 'name' config or if your host is called either 'maas-snap' or 'maas-deb'.

It will work under the assumptions that the CWD is the one where the maas source code is located.

Example usage:
```sh
maas-dev-env init --deb
maas-dev-env sync --deb
```

Or for a snap environment:
```sh
maas-dev-env init --snap
maas-dev-env sync --snap
```

