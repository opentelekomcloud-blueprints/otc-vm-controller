# Readme for the OTCC


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
