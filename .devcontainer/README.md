# Devcontainer

_The easiest way to contribute to and/or test this repository._

## Requirements

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [docker](https://docs.docker.com/install/)
- [VS Code](https://code.visualstudio.com/)
- [Remote - Containers (VSC Extention)](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

[More info about requirements and devcontainer in general](https://code.visualstudio.com/docs/remote/containers#_getting-started)

## How to use Devcontainer for development/test

1. Make sure your computer meets the requirements.
1. Fork this repository.
1. Clone the repository to your computer.
1. Open the repository using VS Code.

When you open this repository with VSCode and your computer meets the requirements you are asked to "Reopen in Container", do that.

![reopen](images/reopen.png)

If you don't see this notification, open the command pallet (ctrl+shift+p) and select `Remote-Containers: Reopen Folder in Container`.

_It will now build the devcontainer._

The container have some "tasks" to help you testing your changes.

## Custom Tasks in this repository

_Start "tasks" by opening the the command pallet (ctrl+shift+p) and select `Tasks: Run Task`_


### Run tests

Will run pypi tests on all tests in the workspace

### Run tests with coverege
Will run pypi tests on all tests in the workspace with code coverege on

### Make package

Builds the package of the current version stated in the Setup.py file

### Upload package to pypi

Uploads all built packages to pypi, please provide credentials in terminal window

### Install TabNine

Installs TabNine config, requires a valid cloud API key to work

