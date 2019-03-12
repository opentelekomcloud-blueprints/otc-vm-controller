#!/bin/env python3
import json
import logging
import os.path
import sys
import tempfile
import urllib.request

import gnupg
import yaml
from exitstatus import ExitStatus
from logging.handlers import RotatingFileHandler

# create logging
logger = logging.getLogger("OTCC")
logger.setLevel(logging.DEBUG)

fh = RotatingFileHandler('debug.log',maxBytes=20971520,backupCount=5)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


def loadConfig(file: str, cfgpasswd: str) -> yaml:
    """

    :rtype: yaml
    """
    gpg = gnupg.GPG(gnupghome=os.path.join(os.getcwd(), ".crypt"), use_agent=False, verbose=False)
    gpg.encoding = "utf-8"
    CfgLoaderLogger = logging.getLogger("CFGL")
    CfgLoaderLogger.setLevel(logging.ERROR)
    CfgLoaderLogger.addHandler(fh)
    CfgLoaderLogger.addHandler(ch)
    if os.path.isfile("config.gpgyml"):
        with tempfile.SpooledTemporaryFile(encoding="utf-8", mode="rw") as tmp:
            with open("config.gpgyml", "rb") as configCry:
                data = str(gpg.decrypt_file(configCry, passphrase=cfgpasswd))
            tmp.write(data)
            tmp.seek(0)
            cfg = yaml.load(tmp)
        if cfg == None:
            CfgLoaderLogger.error("Can't decrypt config")
            sys.exit(ExitStatus.failure)
        return cfg
    else:
        msg = "The file " + file + " does not exist, is not a file or has no access rights to it."
        CfgLoaderLogger.error(msg)
        sys.exit(ExitStatus.failure)


def GetTokenFromIAM(URL: str, UserName: str, Domain: str, Password: str, PID: str) -> str:
    """This function connects to the IAM service of the OTC.
It is using username, password, domain and the project id for auth.
it will give you the auth token for other functions. You can turn it on/off in the config

    :rtype: str
    :param URL: the URL to the IAM of OTC
    :param UserName: your username
    :param Domain: the domain used
    :param Password: your password (this is why the config is crypted)
    :param PID: some project id
    """
    GetTokenLogger = logging.getLogger("OTCGT")
    GetTokenLogger.setLevel(logging.DEBUG)
    GetTokenLogger.addHandler(fh)
    GetTokenLogger.addHandler(ch)
    req = urllib.request.Request(URL)
    GetTokenLogger.info('Using the URL ' + URL + " for the IAM service")
    GetTokenLogger.info(
        'Using the Username ' + str(UserName) + " and Domain " + Domain + " for the request of auth-token")
    GetTokenLogger.info("A password will be used for this request")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    body = {"auth": {
        "identity": {
            "methods": ["password"],
            "password": {
                "user": {
                    "name": str(UserName),
                    "password": Password,
                    "domain": {
                        "name": Domain
                    }
                }
            }
        },
        "scope": {
            "project": {"id": PID}
        }
    }}

    jsondata = json.dumps(body)
    jsonbytes = jsondata.encode("utf-8")
    req.add_header("Content-Length", len(jsonbytes))
    try:
        response = urllib.request.urlopen(req, jsonbytes)
    except urllib.error.HTTPError as ErrorMSG:
        GetTokenLogger.error(ErrorMSG)
        sys.exit(ExitStatus.failure)
    r = {"token": response.getheader("X-Subject-Token"), "data": response.read().decode("utf-8")}
    return r


def getServers(TokenData, TheToken, Service="nova"):
    getServersLogger = logging.getLogger("OTCGS")
    getServersLogger.setLevel(logging.DEBUG)
    getServersLogger.addHandler(fh)
    getServersLogger.addHandler(ch)

    # print(TokenData["token"]["catalog"])
    MyToken = None
    for token in TokenData["token"]["catalog"]:
        if token["name"] == Service:
            MyToken = token

    req = urllib.request.Request(MyToken["endpoints"][0]["url"] + "/servers/detail")
    getServersLogger.info("Using endoint " + MyToken["endpoints"][0]["url"])
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("X-Auth-Token", TheToken)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as ErrorMSG:
        getServersLogger.error(ErrorMSG)
        sys.exit(ExitStatus.failure)
    servers = json.loads(response.read().decode("utf-8"))["servers"]
    returnservers = []
    for server in servers:
        getServersLogger.info(server["name"] + " is " + server["status"])
        for link in server["links"]:
            if link["rel"] == "self":
                theLink = link["href"]
        returnservers.append({"name": server["name"], "status": server["status"], "URL": theLink + "/action"})
    return returnservers


def StopServers(OTClist, WishList, token):
    getStopperLogger = logging.getLogger("OTCStopper")
    getStopperLogger.setLevel(logging.DEBUG)
    getStopperLogger.addHandler(fh)
    getStopperLogger.addHandler(ch)
    body = {"os-stop": {}}
    jsondata = json.dumps(body)
    jsonbytes = jsondata.encode("utf-8")
    for server in OTClist:
        if server["name"] in WishList:
            getStopperLogger.info("stopping " + server["name"])
            req = urllib.request.Request(server["URL"])
            req.add_header("Content-Type", "application/json; charset=utf-8")
            req.add_header("X-Auth-Token", token)
            req.add_header("Content-Length", len(jsonbytes))
            try:
                response = urllib.request.urlopen(req, jsonbytes)
            except urllib.error.HTTPError as ErrorMSG:
                if ErrorMSG.code == 409:
                    getStopperLogger.warning(server["name"] + " is already stopped and can therefore not be stopped")
                else:
                    getStopperLogger.error(ErrorMSG)
                    sys.exit(ExitStatus.failure)
        else:
            getStopperLogger.info("will not touch  " + server["name"])


def StartServers(OTClist, WishList, token):
    getStartLogger = logging.getLogger("OTCStarter")
    getStartLogger.setLevel(logging.DEBUG)
    getStartLogger.addHandler(fh)
    getStartLogger.addHandler(ch)
    body = {"os-start": {}}
    jsondata = json.dumps(body)
    jsonbytes = jsondata.encode("utf-8")
    for server in OTClist:
        if server["name"] in WishList:
            getStartLogger.info("starting " + server["name"])
            req = urllib.request.Request(server["URL"])
            req.add_header("Content-Type", "application/json; charset=utf-8")
            req.add_header("X-Auth-Token", token)
            req.add_header("Content-Length", len(jsonbytes))
            try:
                response = urllib.request.urlopen(req, jsonbytes)
            except urllib.error.HTTPError as ErrorMSG:
                if ErrorMSG.code == 409:
                    getStartLogger.warning(server["name"] + " is already started and can therefore not be started")
                else:
                    getStartLogger.error(ErrorMSG)
                    sys.exit(ExitStatus.failure)
        else:
            getStartLogger.info("will not touch  " + server["name"])



def main(argv):

    logger.info('start loding the main config file')
    maincfg = loadConfig(os.path.join(os.path.dirname(os.path.realpath(__file__)),"config.gpgyml"), argv[0])
    logger.info('done loding the main config file')

    if maincfg["steering"]["getAuthToken"]:
        logger.info('start talking to IAM to get a auth-token')
        tokensMeta = GetTokenFromIAM(maincfg["OTC"]["IAMurl"], maincfg["OTC"]["AUTH"]["Username"],
                                     maincfg["OTC"]["AUTH"]["Domain"],
                        maincfg["OTC"]["AUTH"]["Password"], maincfg["Customer"]["projectID"])

    if not tokensMeta:
        logger.error("No Tokens loaded")
        sys.exit(ExitStatus.failure)
    else:
        # loads token in dict and give it to the next part for geting servers
        servers = getServers(json.loads(tokensMeta["data"]), tokensMeta["token"])
        if len(argv) < 2:
            logger.error('TELL ME WHAT TO DO')
            sys.exit(ExitStatus.failure)

        if argv[1] == "start":
            StartServers(servers, maincfg["Servers"], tokensMeta["token"])
        elif argv[1] == "stop":
            StopServers(servers, maincfg["Servers"], tokensMeta["token"])
        else:
            logger.error('what should I do? I can not ' + argv[1])
            sys.exit(ExitStatus.failure)



if __name__ == '__main__':
    main(sys.argv[1:])
