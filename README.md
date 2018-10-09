# Readme for the OTC-VM-controller 🎮
![Python 3.7 works](https://img.shields.io/badge/Python-3.7-green.svg?longCache=true&style=plastic&logo=Python&logoColor=white)
![Python requirements.txt missing](https://img.shields.io/badge/Python_requirements.txt-missing-red.svg?longCache=true&style=plastic&logo=Python&logoColor=white)
![OTC IAM API v3](https://img.shields.io/badge/OTC_IAM_API-3-green.svg?longCache=true&style=plastic)
![OTC ECS API v2](https://img.shields.io/badge/OTC_ECS_API-2-green.svg?longCache=true&style=plastic)
![GNU General Public License v3](https://img.shields.io/badge/license-GPL_v3-blue.svg?longCache=true&style=plastic&logo=GNU&logoColor=white)

![issues](https://img.shields.io/github/issues-raw/OpenTelekomCloud/OTC-VM-controller.svg)
![pr](https://img.shields.io/github/issues-pr-raw/OpenTelekomCloud/OTC-VM-controller.svg)
![size](https://img.shields.io/github/languages/code-size/OpenTelekomCloud/OTC-VM-controller.svg)
![tag](https://img.shields.io/github/tag/OpenTelekomCloud/OTC-VM-controller.svg)

## why Controller and not Controler?
We want to show that controlling the VMs can be as easy as playing a video game.

## What can this tool be used for?
This small tool provides a way to start/stop individual servers in the OTC. It uses the official API of the OTC. Since this tool could be executed from a server, e.g. to perform regular start and stop tasks via cron, the config is encrypted with GPG.

## dependencies
This application was developed in **Python 3.7**. The following modules were used in a virtual Python environment and should be installed on your system.
- PyYAML (MIT License)(Kirill Simonov)
- exitstatus (MIT License) (John Hagen)
- pip (MIT License) (pypa-dev@groups.google.com)
- psutil (BSD License) (Giampaolo Rodola)
- python-gnupg (BSD License) (Vinay Sajip)
- setuptools (MIT License) (distutils-sig@python.org)

Due to the encryption used, you need the application **GnuPG** (GNU General Public License) (Jeroen Ooms) on the system.

## How do I use this software?
For each environment the script startCrypto.py must be executed **once**. In the script an e-mail and a password must be specified. These are used for encryption and decryption.

For every change to the configuration the script CryptConfig.py must be executed and the unencrypted configuration can be deleted afterwards. Deleting the unencrypted configuration is strongly recommended.

The file controller.py is the main program of this tool. It is called with two parameters. The first parameter is the password to decrypt the config and the second parameter is whether the servers should be stopped or started.

## How should your config look?

The configuration file is called config.yml and is not attached in this repo and must be created according to this template.

```yaml
steering:
  #use on and off here
  getAuthToken: on
Customer:
  name: OurBestCustomer
  projectID: b2d1234b21a1234b4d44f1234567888
OTC:
  IAMurl: https://iam.eu-de.otc.t-systems.com/v3/auth/tokens
  AUTH:
    Username: myUserName
    Password: "m¥p4$$w0rd"
    Domain: OTC-EU-DE-00000000000000000000
Servers:
  - Server1
  - Server2
```

## Current limits of this software
This software only works with an encrypted config, which makes troubleshooting difficult. The name of the log file is currently programmed as debug.log.

## wH4t ñ33d$ t0 b3 !mpr0v3d !ñ tH!$ t00l?
- In the source code comments and hints must be added and the readability could be improved.
- Source code parts occur very often, this could be improved by the use of functions.
- It has not yet been tested which Python versions except 3.7 are supported.
