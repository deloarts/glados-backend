# update glados backend

- [update glados backend](#update-glados-backend)
  - [1 stop the service](#1-stop-the-service)
  - [2 git](#2-git)
  - [3 update the config file](#3-update-the-config-file)
  - [4 migrate the database](#4-migrate-the-database)
  - [5 restart the service](#5-restart-the-service)

## 1 stop the service

```bash
sudo systemctl stop glados.service
```

## 2 git

To update the app use:

```bash
cd /opt/glados/glados-backend
source .env/bin/activate

git fetch --all --tags
git checkout {TAG_NAME}

python -m pip install -r requirements.txt
```

Where `{TAG_NAME}` is the version of the app you want to use, e.g. `v0.12.2`.

## 3 update the config file

Compare the `config.sample.yml` file with your `config.yml` file and adjust, if necessary.

## 4 migrate the database

To upgrade the database to the latest version run:

```bash
cd /opt/glados/glados-backend
source .env/bin/activate
python -m alembic upgrade head
```

> ⚠️ Be sure to have a backup of your database before migrating!

## 5 restart the service

```bash
sudo systemctl start glados.service
```