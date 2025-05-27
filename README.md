# Ldap Users and Groups TO NC
This dockerized python script looks up ldap users and their groups. It creates an xls formatted documentation and places it into a nextcloud folder.
This is a fork of https://github.com/lanbugs/get_ad_right_matrix.git

## config
The configuration is done via a .env file. This file needs the following parameters:
```
## ldapUsersGroupsToNC
LDAP_HOSTNAME=dir.yourdomain.somewhere
LDAP_USER=LDAPDNOfYourUser
LDAP_PASSWORDofThatUser
LDAPXLS_SEARCH_FILTER="(&(objectclass=inetOrgPerson)(memberof=cn=yourGroupContaingAllUsers,ou=groups,dc=yourDomain,dc=local))"
NC_USER=loginnameOFYourNC
NC_PASS=supersecretpasswordofthatuser
NC_URL=https://cloud.yourdomain.somewhere
USERDOCDIR=/directoryToPlaceTeFileInto/
# file name
LDAPXLS_USERSGROUPS='BenutzerUndGruppen.xlsx'
LDAPXLS_ROTATION=45
```
## run
use ```docker compose run --rm ldapxls python ldapxls.py``` as needed / or triggered by crontab
