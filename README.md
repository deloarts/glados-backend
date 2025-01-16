# glados backend

![state](https://img.shields.io/badge/State-beta-brown.svg?style=for-the-badge)
![version](https://img.shields.io/github/v/release/deloarts/glados-backend?style=for-the-badge&color=orange)
[![python](https://img.shields.io/badge/Python-3.11-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
![OS](https://img.shields.io/badge/OS-UNIX-blue.svg?style=for-the-badge)

> ✏️ Glados is in use at my company for handling bought items. Its meant to be the interface between the engineering department and the purchase department. Therefore this software must reach certain requirements, which cannot be changed due to company guidelines.

Table of contents:

- [glados backend](#glados-backend)
  - [1 introduction](#1-introduction)
  - [2 installation](#2-installation)
    - [2.1 requirements](#21-requirements)
    - [2.2 setup](#22-setup)
    - [2.3 first login](#23-first-login)
  - [3 update](#3-update)
  - [4 developing](#4-developing)
  - [5 user levels](#5-user-levels)
    - [5.1 user](#51-user)
    - [5.2 superuser](#52-superuser)
    - [5.3 adminuser](#53-adminuser)
    - [5.4 guestuser](#54-guestuser)
    - [5.5 systemuser](#55-systemuser)
  - [6 license](#6-license)
  - [7 changelog](#7-changelog)

## 1 introduction

Glados is a resource planning software with a web ui: *Create and manage your projects and items with ease, keep your purchase process in perfect order*.

Glados is a free open source software, so feel free to use it if it fits your needs. Glados is still in development and has not reached major version 1.0.0 yet, meaning it can change in its appearance and functionality at any time without notice.

![Device Mockup](/assets/device-mockup.png)

How to use glados? See **USAGE.md** in the **docs** at the frontend github repository. The frontend is located at [github.com/deloarts/glados-frontend](https://github.com/deloarts/glados-frontend).

## 2 installation

For a guided installation see [INSTALL.md](/docs/INSTALL.md)

> ✏️ Frontend and backend require the same major and minor version to work together

### 2.1 requirements

System requirements:

- Unix (tested on Debian 11)
- Approx. 250GB free space
- Sudo rights required
- Open port at TCP 5000
- Python 3.11

Package requirements (apt):

- cifs-utils
- nfs-common
- gcc
- pkg-config
- libcairo2-dev

### 2.2 setup

Python venv can be created inside the installation folder as `.env`.

- recommended installation folder: `/opt/glados/glados-backend/`
- use the latest git tag
- copy the [config.sample.yml](/config.sample.yml) file and paste it as `config.yml` file, then edit it to fit your needs
- do the same for all template files in the templates folder
- database migration: `python -m alembic upgrade head`

### 2.3 first login

- username: `system`
- password: The password you've setup in the `config.yml`

## 3 update

For a guided update process see [UPDATE.md](/docs/UPDATE.md)

## 4 developing

For contributors: [DEV.md](/docs/DEV.md)

## 5 user levels

All user levels share a common `active` state. A user must be active to login to Glados.

### 5.1 user

The **user** is the default level for new users in the app. The following rules are applied to the **user**:

- A **user** can create projects, but cannot assign other users as designated user
- A **user** can edit their projects
- A **user** can create items
- A **user** can edit their own items, as long as the items state is `open` and the project is active
- A **user** can delete their own items, as long as the items state is `open`
- A **user** cannot make changes to the settings of the app

### 5.2 superuser

The **superuser** has a bit more permissions, compared to the **user**. The following rules are applied to the **superuser**:

- A **superuser** can create, edit and delete projects and can assign other users as designated user
- A **superuser** can edit their projects
- A **superuser** can create items
- A **superuser** can edit all items from all users at any state, as long as the project is active
- A **superuser** can delete all items from all users at any state
- A **superuser** cannot make changes to the settings of the app

### 5.3 adminuser

The **adminuser** has the highest level of permissions. Elevate an **user** or a **superuser** to this right only if the person understands the consequences! The following rules are applied to the **adminuser**:

- A **adminuser** can create, edit and delete projects and can assign other users as designated user
- A **adminuser** can create items
- A **adminuser** can edit all items from all users at any state, as long as the project is active
- A **adminuser** can delete all items from all users at any state
- A **adminuser** can make changed to the settings of the app
- A **adminuser** can create new users and change their level

### 5.4 guestuser

The **guestuser** has the lowest level of permissions. This user exist, so people can view the state of items. The following rules are applied to the **guestuser**:

- A **guestuser** flag in the user permission settings overrules all other levels (forbidden before allow)
- A **guestuser** can only view projects (cannot create, nor edit, nor delete)
- A **guestuser** can only view items (cannot create, nor edit, nor delete)
- A **guestuser** cannot make changed to the settings of the app

### 5.5 systemuser

The **systemuser** is created at DB init. The credentials for the **systemuser** must be applied in the *config.yml* file before the first run of the app. The following rules are applied to the **systemuser**:

- There can only be one **systemuser**
- The **systemuser** has the same rights as the **adminuser**
- The **systemuser** is a fallback user for changing the configuration

## 6 license

MIT

## 7 changelog

**v0.13.0**: Add pagination.  
**v0.12.3**: Add proxy config.  
**v0.12.2**: Add rfid auth. Fix user init error.  
**v0.12.1**: Fix import error.  
**v0.12.0**: Add api key endpoint. Add rfid to user.  
**v0.11.0**: Add item validation endpoint.  
**v0.10.0**: Add language and theme.  
**v0.9.2**: Add project customer and project description to bought item api.  
**v0.9.1**: Block item edit when project is inactive.  
**v0.9.0**: Add unit api to bought items. Fix minor bugs.  
**v0.8.3**: Add welcome mail for new users.  
**v0.8.2**: Allow normal user to create projects.  
**v0.8.1**: Fix pat creation schema.  
**v0.8.0**: Rename item definition and machine number. Add project api to pat endpoint.  
**v0.7.3**: Update user permissions for projects.  
**v0.7.2**: Fix bug on bought item query.  
**v0.7.1**: Fix bug on project filter.  
**v0.7.0**: Add projects.  
**v0.6.0**: Add stock cut 2d. Model & schema refactor.  
**v0.5.0**: Add weblink.  
**v0.4.2**: Add item validation.  
**v0.4.1**: Better bought item changelog.  
**v0.4.0**: Add new permission levels. Add tools. Add config editor.  
**v0.3.2**: Update env.  
**v0.3.1**: Add missing status in response schema.  
**v0.3.0**: Add api for changing items.  
**v0.2.4**: Fix excel import.  
**v0.2.3**: Fix db session.  
**v0.2.2**: Fix pending mails.  
**v0.2.1**: Fix db session.  
**v0.2.0**: Add units api.  
**v0.1.3**: Fix excel import header loop.  
**v0.1.2**: Add order by ID.  
**v0.1.1**: Update log handler.  
**v0.1.0**: Initial commit.
