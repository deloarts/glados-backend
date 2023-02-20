# glados backend

Backend for the glados project.

![state](https://img.shields.io/badge/State-beta-brown.svg?style=for-the-badge)
![version](https://img.shields.io/badge/Version-0.1.1-orange.svg?style=for-the-badge)

[![python](https://img.shields.io/badge/Python-3.10-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
![OS](https://img.shields.io/badge/OS-UNIX-blue.svg?style=for-the-badge)

Glados is a resource planning software with a web ui. The frontend is located at [github.com/deloarts/glados-frontend](https://github.com/deloarts/glados-frontend).

Table of contents:

- [glados backend](#glados-backend)
  - [1 installation](#1-installation)
    - [1.1 system requirements](#11-system-requirements)
    - [1.2 filesystem](#12-filesystem)
      - [1.2.1 glados directory](#121-glados-directory)
      - [1.2.2 glados database backup directory](#122-glados-database-backup-directory)
    - [1.3 software requirements](#13-software-requirements)
      - [1.3.1 install python](#131-install-python)
      - [1.3.2 install git](#132-install-git)
    - [1.4 clone the repository](#14-clone-the-repository)
    - [1.5 create the environment](#15-create-the-environment)
    - [1.6 setup the config file \& all templates](#16-setup-the-config-file--all-templates)
    - [1.7 create the database](#17-create-the-database)
    - [1.8 setup startup scripts](#18-setup-startup-scripts)
    - [1.9 create the service](#19-create-the-service)
    - [1.10 first login](#110-first-login)
  - [2 update](#2-update)
    - [2.1 stop the service](#21-stop-the-service)
    - [2.2 git](#22-git)
    - [2.3 update the config file](#23-update-the-config-file)
    - [2.4 migrate the database](#24-migrate-the-database)
    - [2.5 restart the service](#25-restart-the-service)
  - [3 developing](#3-developing)
    - [3.1 repository](#31-repository)
      - [3.1.1 cloning](#311-cloning)
      - [3.1.2 main branch protection](#312-main-branch-protection)
      - [3.1.3 branch naming convention](#313-branch-naming-convention)
      - [3.1.4 issues](#314-issues)
    - [3.2 poetry](#32-poetry)
      - [3.2.1 setup](#321-setup)
      - [3.2.2 install](#322-install)
      - [3.2.3 tests](#323-tests)
    - [3.3 pre-commit hooks](#33-pre-commit-hooks)
    - [3.4 api docs](#34-api-docs)
    - [3.5 new revision checklist](#35-new-revision-checklist)
  - [4 license](#4-license)
  - [5 changelog](#5-changelog)
  - [6 to do](#6-to-do)

## 1 installation

### 1.1 system requirements

- Unix (tested on Debian 11)
- Approx. 250GB free space
- Sudo rights required
- Open port at TCP 5000

### 1.2 filesystem

#### 1.2.1 glados directory

Create the glados app directory:

```bash
sudo mkdir /opt/glados
```

> ✏️ All bash commands for the glados directory refer to /opt/glados. If you change this, you'll have to keep in mind to change /opt/glados to your path.

#### 1.2.2 glados database backup directory

This can be any folder on the system, but it can also be a mounted share. Here's an example on how to mount a Windows share:

```bash
sudo apt install cifs-utils nfs-common -y
sudo mkdir /mnt/glados-backup
```

In the following chapters you'll find a description on how to create an alias for creating the mount.

### 1.3 software requirements

```bash
sudo apt update -y
```

#### 1.3.1 install python

Install build dependencies:

```bash
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev python3-distutils -y
```

Download and extract python 3.10:

```bash
wget https://www.python.org/ftp/python/3.10.7/Python-3.10.7.tgz
tar -xvf Python-3.10.7.tgz
```

Build and install python:

```bash
cd Python-3.10.7
sudo ./configure --enable-optimizations
sudo make -j 2
sudo make altinstall
```

Add alias to bashrc:

```bash
# Open file
sudo nano ~/.bashrc

# In .bashrc file:
alias python='python3.10'
# Save & close with CTRL+O then CTRL+X

# Load bashrc
source ~/.bashrc
```

Verify the installation:

```bash
python --version

# This should print the following output:
Python 3.10.7
```

#### 1.3.2 install git

```bash
sudo apt install git -y
```

### 1.4 clone the repository

To perform this you'll need:

- A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with repo-wide rights.
- At least read access to the repository.

```bash
cd /opt/glados
sudo git clone https://github.com/deloarts/glados-backend.git
cd glados-backend
git checkout {TAG_NAME}
```

Enter your username and your access token when prompted. Replace `{TAG_NAME}` with the version you want to clone, e.g. `v0.1.0`.

> ✏️ You can use this command to update the app as well. Just modify the tag name.
>
> ⚠️ Only clone the repository with a published version tag!
> 
> ✏️ The glados backend lives now in `/opt/glados/glados-backend/`.

### 1.5 create the environment

Create your python env and install all dependencies:

```bash
cd /opt/glados/glados-backend
sudo python -m venv .env
source .env/bin/activate
python -m pip install -r requirements.txt
```

### 1.6 setup the config file & all templates

- Copy the `config.sample.yml` file and paste it as `config.yml` file. Then edit the config file to fit your needs.
- Do the same for all template files in the templates folder.

### 1.7 create the database

To create the database run:

```bash
python -m alembic upgrade head
```

> ✏️ You need to active the python env first.

### 1.8 setup startup scripts

To be able to run all startup scripts, you'll need to make them executable:

```bash
sudo chmod +x /opt/glados/glados-backend/scripts/glados-welcome.sh
sudo chmod +x /opt/glados/glados-backend/scripts/glados-aliases.sh
```

Now you have to create an alias and a run-command to your .bashrc file:

```bash
sudo nano ~/.bashrc

# Append the following lines at the end
# Glados
alias watch-glados-service='watch -c SYSTEMD_COLORS=1 systemctl status glados.service'
alias mount-glados-backup='sudo mount -t cifs "//{SHARE_HOST}/{SHARE_NAME}" "/mnt/glados-backup" -o username={WINDOWS_USER}'
bash /opt/glados/glados-backend/scripts/glados-welcome.sh
source /opt/glados/glados-backend/scripts/glados-aliases.sh
```

- SHARE_HOST: The IP address of the Windows server, which holds the share.
- SHARE_NAME: The name of the shared folder.
- WINDOWS_USER: The username of any domain-user with write access to the share.

### 1.9 create the service

Copy the glados.service file into /etc/systemd/system/:

```bash
sudo cp /opt/glados/glados-backend/services/glados.service /etc/systemd/system/glados.service
sudo systemctl enable glados.service
sudo systemctl start glados.service
```

### 1.10 first login

Login to Glados at the IP address you've specified in the config file (this requires the frontend to be set up):

- Username: `system`
- Password: The password you've setup in the config file.

No you're ready to create new users.

## 2 update

> ⚠️ Very important: The frontend depends on a certain server version. Make sure your frontend has the correct version when updating in production!

### 2.1 stop the service

```bash
sudo systemctl stop glados.service
```

### 2.2 git

To update the app use:

```bash
cd /opt/glados/glados-backend
source .env/bin/activate

git fetch --all --tags
git checkout {TAG_NAME}

python -m pip install -r requirements.txt
```

Where `{TAG_NAME}` is the version of the app you want to use, e.g. `v0.1.1`.

### 2.3 update the config file

Compare the `config.sample.yml` file with your `config.yml` file and adjust, if necessary.

### 2.4 migrate the database

To upgrade the database to the latest version run:

```bash
cd /opt/glados/glados-backend
source .env/bin/activate
python -m alembic upgrade head
```

> ⚠️ Be sure to have a backup of your database before migrating!

### 2.5 restart the service

```bash
sudo systemctl start glados.service
```

## 3 developing

Dependency management is done with [Poetry](https://python-poetry.org/docs/master/#installation).

### 3.1 repository

#### 3.1.1 cloning

Clone the repo to your local machine:

```powershell
git clone git@github.com:deloarts/glados-backend.git
```

You'll need access to the repository.

#### 3.1.2 main branch protection

> ❗️ Never develop new features and fixes in the main branch!

The main branch is protected: it's not allowed to make changes directly to it. Create a new branch in order work on issues. The new branch should follow the naming convention from below.

#### 3.1.3 branch naming convention

1. Use grouping tokens at the beginning of your branch names, such as:
    - feature: A new feature that will be added to the project
    - fix: For bugfixes
    - tests: Adding or updating tests
    - docs: For updating the docs
    - wip: Work in progress, won't be finished soon
    - junk: Just for experimenting
2. Use slashes `/` as delimiter in branch names (`feature/docket-export`)
3. Avoid long descriptive names, rather refer to an issue
4. Do not use bare numbers as leading parts (`fix/108` is bad, `fix/issue108` is good)

#### 3.1.4 issues

Use the issue templates for creating an issue. Please don't open a new issue if you haven't met the requirements and add as much information as possible. Further:

- Format your code in an issue correctly with three backticks, see the [markdown guide](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
- Add the full error trace.
- Do not add screenshots for code or traces.

### 3.2 poetry

#### 3.2.1 setup

If you prefer the environment inside the projects root, use:

```powershell
poetry config virtualenvs.in-project true
```

> ⚠️ Make sure not to commit the virtual environment to GitHub. See [.gitignore](.gitignore) to find out which folders are ignored.

#### 3.2.2 install

Install all dependencies (assuming you are inside the projects root folder):

```powershell
poetry install
```

Check your active environment with:

```powershell
poetry env list
poetry env info
```

Update packages with:

```powershell
poetry update
```

#### 3.2.3 tests

Tests are done with pytest. For testing with poetry run:

```powershell
poetry run pytest
```

### 3.3 pre-commit hooks

Don't forget to install the pre-commit hooks:

```powershell
pre-commit install
```

### 3.4 api docs

The API docs are available only when the app runs in debug mode (see config.yml for details).
The docs can be viewed at `localhost:port/docs`, where the port is the port you've defined in the config file.

### 3.5 new revision checklist

1. Update **dependencies**: `poetry update`
2. Update the **version** in
   - [pyproject.toml](pyproject.toml)
   - [const.py](app/const.py)
   - [README.md](README.md)
3. Run all **tests**: `poetry run pytest`
4. Check **pylint** output: `poetry run pylint app/`
5. Update the **lockfile**: `poetry lock`
6. Update the **requirements.txt**: `poetry export -f requirements.txt -o requirements.txt`

## 4 license

No license.

## 5 changelog

**v0.1.1**: Update log handler.  
**v0.1.0**: Initial commit.

## 6 to do

Using VS Code [Comment Anchors](https://marketplace.visualstudio.com/items?itemName=ExodiusStudios.comment-anchors) to keep track of to-dos.
