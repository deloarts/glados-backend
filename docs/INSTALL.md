# install glados backend

- [install glados backend](#install-glados-backend)
  - [1 system requirements](#1-system-requirements)
  - [2 filesystem](#2-filesystem)
    - [2.1 glados directory](#21-glados-directory)
    - [2.2 glados database backup directory](#22-glados-database-backup-directory)
  - [3 software requirements](#3-software-requirements)
    - [3.1 install python](#31-install-python)
    - [3.2 install git](#32-install-git)
  - [4 clone the repository](#4-clone-the-repository)
  - [5 create the environment](#5-create-the-environment)
  - [6 setup the config file \& all templates](#6-setup-the-config-file--all-templates)
    - [6.1 config.yml](#61-configyml)
  - [7 create the database](#7-create-the-database)
  - [8 setup startup scripts](#8-setup-startup-scripts)
  - [9 create the service](#9-create-the-service)
  - [10 first login](#10-first-login)


## 1 system requirements

- Unix (tested on Debian 11)
- Approx. 250GB free space
- Sudo rights required
- Open port at TCP 5000
- Python 3.11

## 2 filesystem

### 2.1 glados directory

Create the glados app directory:

```bash
sudo mkdir /opt/glados
```

> ✏️ All bash commands for the glados directory refer to /opt/glados. If you change this, you'll have to keep in mind to change /opt/glados to your path.

### 2.2 glados database backup directory

This can be any folder on the system, but it can also be a mounted share. Here's an example on how to mount a Windows share:

```bash
sudo apt install cifs-utils nfs-common -y
sudo mkdir /mnt/glados-backup
```

In the following chapters you'll find a description on how to create an alias for creating the mount.

## 3 software requirements

```bash
sudo apt update -y
sudo apt install gcc pkg-config libcairo2-dev -y
```

### 3.1 install python

Install build dependencies:

```bash
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev python3-distutils -y
```

Download and extract python 3.11:

```bash
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar -xvf Python-3.11.9.tgz
```

Build and install python:

```bash
cd Python-3.11.9
sudo ./configure --enable-optimizations
sudo make -j 2
sudo make altinstall
```

Add alias to bashrc:

```bash
# Open file
sudo nano ~/.bashrc

# In .bashrc file:
alias python='python3.11'
# Save & close with CTRL+O then CTRL+X

# Load bashrc
source ~/.bashrc
```

Verify the installation:

```bash
python --version

# This should print the following output:
Python 3.11.9
```

### 3.2 install git

```bash
sudo apt install git -y
```

## 4 clone the repository

To perform this you'll need:

- A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with repo-wide rights.
- At least read access to the repository.

```bash
cd /opt/glados
sudo git clone https://github.com/deloarts/glados-backend.git
cd glados-backend
git checkout {TAG_NAME}
```

Enter your username and your access token when prompted. Replace `{TAG_NAME}` with the version you want to clone, e.g. `v0.12.3`.

> ✏️ You can use this command to update the app as well. Just modify the tag name.
>
> ⚠️ Only clone the repository with a published version tag!
> 
> ✏️ The glados backend lives now in `/opt/glados/glados-backend/`.

## 5 create the environment

Create your python env and install all dependencies:

```bash
cd /opt/glados/glados-backend
sudo python -m venv .env
source .env/bin/activate
python -m pip install -r requirements.txt
```

## 6 setup the config file & all templates

- Copy the `config.sample.yml` file and paste it as `config.yml` file. Then edit the config file to fit your needs
- Do the same for all template files in the templates folder

### 6.1 config.yml

The config file contains the following:

key | value | description
--- | --- | ---
debug | `bool` | Enable this in your debug/dev environment. This creates a dev.db database, so you do not interfere with your production db
locale/tz | `str` | The timezone
security/min_pw_length | `int` | The minimum password length a use must choose
security/algorithm | `str` | The algorithm used for creating access tokens
security/token_url | `str` | The api where the token can be retrieved
security/expire_minutes | `int` | The expiration time for non-persistent tokens in minutes
security/allow_rfid_login | `bool` | Wether or not to enable authentication via RFID (this is experimental and doesn't meet security standards)
server/host | `str` | The hosts IP address (the IP behind the `local_url`)
server/port | `int` | The port where the backend runs
server/domain | `str` | The url, where glados can be reached. E.g. `glados.company.local` on your intranet
server/static/enable | `bool` | Enable static file serving
server/static/folder | `str` | The folder where the static files can be found
server/static/url | `str` | The url from where the static files are returned
server/ssl/keyfile | `str or null` | The absolute path to the ssl key file. If set to `null` the backend accepts http-requests
server/ssl/certfile | `str or null` | The absolute path to the ssl certificate file. If set to `null` the backend accepts http-requests
server/headers_server | `bool` | Allow server headers
server/headers_proxy | `bool` | Allow proxy headers
server/forwarded_allowed_ips | `str` | The allowed IPs (required when using nginx)
schedules/database_hour | `int` | The hour when db-schedule shall run (automatically set item status to `late`, ...)
schedules/system_hour | `int` | The hour when system-schedule shall run (disc space calculations, ...)
schedules/email_notification_hour | `int` | The hour when users shall be notified by mail (item status updated, ...)
schedules/backup_db_hour | `int` | The hour when the database backup is scheduled
schedules/delete_temp_hour | `int` | The hour when temp files are deleted
schedules/delete_uploads_hour | `int` | The hour when uploaded files are deleted
filesystem/disc_space_warning | `int` | The amount of free space on the system, under which a waring mail is sent
filesystem/db_backup/path | `str` | The path to the db backup
filesystem/db_backup/is_mount | `bool` | If the path to the backup is a network mount (cifs), set this to `True`
items/bought/validation/project | `str` | The validation regex for project numbers
items/bought/validation/product | `str` | The validation regex for product numbers
items/bought/status/open | `str` | The name for status `open`. Do not change this!
items/bought/status/requested | `str` | The name for status `requested`. Do not change this!
items/bought/status/ordered | `str` | The name for status `ordered`. Do not change this!
items/bought/status/late | `str` | The name for status `late`. Do not change this!
items/bought/status/partial | `str` | The name for status `partial`. Do not change this!
items/bought/status/delivered | `str` | The name for status `delivered`. Do not change this!
items/bought/status/canceled | `str` | The name for status `canceled`. Do not change this!
items/bought/status/lost | `str` | The name for status `lost`. Do not change this!
items/bought/units/default | `str` | The default unit for bought items. This must be present in the list below!
items/bought/units/values | `list[str]` | A list of allowed units for bought items
items/bought/order_by/high_priority | `str` | The keyword for ordering by `high_priority`. Do not change this!
items/bought/order_by/created | `str` | The keyword for ordering by `created`. Do not change this!
items/bought/order_by/project | `str` | The keyword for ordering by `project`. Do not change this!
items/bought/order_by/productNumber | `str` | The keyword for ordering by `productNumber`. Do not change this!
items/bought/order_by/group1 | `str` | The keyword for ordering by `group1`. Do not change this!
items/bought/order_by/manufacturer | `str` | The keyword for ordering by `manufacturer`. Do not change this!
items/bought/order_by/supplier | `str` | The keyword for ordering by `supplier`. Do not change this!
excel/header_row | `int` | The row for the header for EXCEL generation
excel/data_row| `int` | The row where the app starts to write data for EXCEL generation (must be higher than the header_row)
excel/style/font | `str` | The font for generated EXCEL files
excel/style/size | `int` | The font size for generated EXCEL files
excel/style/header_color | `str` | The hex color for the header row text
excel/style/header_bg_color | `str` | The hex color for the header row background
excel/style/data_color_1 | `str` | The hex text color for even rows
excel/style/data_bg_color_1 | `str` | The hex background color for even rows
excel/style/data_color_2 | `str` | The hex text color for odd rows
excel/style/data_bg_color_2 | `str` | The hex background color for odd rows
mailing/server | `str` | The mail server used for sending notification mails
mailing/port | `int` | The mail server port
mailing/account | `str` | The mail address used for sending notification mails
mailing/password | `str` | The password for the account
mailing/debug_receiver | `str` | The mail address which is used when `debug` is `True`
mailing/debug_no_send | `bool` | Toggle for disabled mailing when `debug` is `True`
templates/bought_item_excel_import | `str` | The template filename for the bought item batch import
templates/mail_item_notification | `str` | The template filename for notification mails
templates/mail_schedule_error | `str` | The template filename for schedule error mails
templates/mail_disc_space_warning | `str` | The template filename for warning mails (disc space)
templates/mail_welcome | `str` | The template filename for welcome mails
init/full_name | `str` | The full name of the system user (should be a generic user)
init/mail | `str` | The mail of the system user
init/password | `str` | The password for the system user

## 7 create the database

To create the database run:

```bash
python -m alembic upgrade head
```

> ✏️ You need to active the python env first.

## 8 setup startup scripts

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

## 9 create the service

Copy the glados.service file into /etc/systemd/system/:

```bash
sudo cp /opt/glados/glados-backend/services/glados.service /etc/systemd/system/glados.service
sudo systemctl enable glados.service
sudo systemctl start glados.service
```

## 10 first login

Login to Glados at the IP address you've specified in the config file (this requires the frontend to be set up):

- Username: `system`
- Password: The password you set up in the config file at `init/password`

No you're ready to create new users.