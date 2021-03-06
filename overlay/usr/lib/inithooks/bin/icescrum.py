#!/usr/bin/python
"""Set iceScrum admin password, email and domain to serve

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=www.example.com
"""

import sys
import getopt
import inithooks_cache

import hashlib

from dialog_wrapper import Dialog
from mysqlconf import MySQL
from executil import system

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

DEFAULT_DOMAIN="www.example.com"

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email=', 'domain='])
    except getopt.GetoptError, e:
        usage(e)

    email = ""
    domain = ""
    password = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val
        elif opt == '--domain':
            domain = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "iceScrum Password",
            "Enter new password for the iceScrum 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "iceScrum Email",
            "Enter email address for the iceScrum 'admin' account.",
            "admin@example.com")

    inithooks_cache.write('APP_EMAIL', email)

    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        domain = d.get_input(
            "iceScrum Domain",
            "Enter the domain to serve iceScrum.",
            DEFAULT_DOMAIN)

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    inithooks_cache.write('APP_DOMAIN', domain)

    hash = hashlib.sha256(password).hexdigest()

    m = MySQL()
    m.execute('UPDATE icescrum.is_user SET passwd=\"%s\" WHERE username=\"admin\";' % hash)
    m.execute('UPDATE icescrum.is_user SET email=\"%s\" WHERE username=\"admin\";' % email)

    config = "/etc/icescrum/config.groovy"
    system("sed -i \"s|serverURL =.*|serverURL = \\\"http://%s\\\"|\" %s" % (domain, config))

    # restart tomcat if running so changes will take effect
    try:
        system("/etc/init.d/tomcat7 status >/dev/null")
        system("/etc/init.d/tomcat7 restart")
    except:
        pass


if __name__ == "__main__":
    main()

