#!/bin/env python3
import os
import sys

import gnupg
from exitstatus import ExitStatus

mail = "somemail@server.com"
passwd = "HelloWorld"
inputfile = "config.yml"
outputfile = "config.gpgyml"


def main():
    print(os.path.join(os.getcwd(), ".crypt"))
    gpg = gnupg.GPG(gnupghome=os.path.join(os.getcwd(), ".crypt"), use_agent=False, verbose=True)
    gpg.encoding = "utf-8"

    if os.path.isfile(inputfile):
        with open(inputfile, 'rb') as ymlfile:
            CryptedData = gpg.encrypt(ymlfile.read(), mail)
            with open(outputfile, 'w')  as out:
                out.write(str(CryptedData))



    else:
        msg = "The file " + inputfile + " does not exist, is not a file or has no access rights to it."
        print(msg)
        sys.exit(ExitStatus.failure)


if __name__ == '__main__':
    main()
