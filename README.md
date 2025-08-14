# Ldap Users and Groups TO NC
This dockerized python script looks up ldap users and their groups. It creates an xls formatted documentation and places it into a nextcloud folder.

Pull requests for code cleanup are highly appreciated.

This is a fork of https://github.com/lanbugs/get_ad_right_matrix.git

## config
The configuration is done via a .env file. This file needs the following parameters:
```
## ldapUsersGroupsToNC
LDAP_HOSTNAME=dir.yourdomain.somewhere
LDAP_ADMIN_DN=LDAPDNOfYourUser
LDAP_ADMIN_PASSWORD=ofThatUser
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

# copy files from one nc to the other
copyNcFiles
copies data from one NC to the other if 
* a directory has a file named ${copyto.txt}  
* fhe file is newer

- source host: ${NC_URL}
- source user: ${NC_USER}
- source pass: ${NC_PASS}


- target host: ${NC_TARGET_URL}
- target user: ${NC_TARGET_USER}
- target pass: ${NC_TARGET_PASS}
## config
edit .env file as described above.
## run
``` docker compose run --rm copyNcFiles python copyNcFiles.py```
