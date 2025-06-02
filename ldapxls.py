#!/usr/bin/env python3

#
# get_ad_right_matrix.py
# Export AD User -> Group Matrix to Excel
# Written by Maximilian Thoma 2021
# changes by Jörg M. Schulz 2025
import os
import json
import re
import ldap3
import pandas as pd
from io import BytesIO

from nc_py_api import Nextcloud

########################################################################################################################
# NOTE:
# -----
# Following packages must be installed in your python environment:
# pandas, xslxwriter, ldap3
#
# Just install them with:
# pip install pandas xslxwriter, ldap3
#
########################################################################################################################
# Settings

# LDAP server ip or fqdn
LDAP_SERVER = os.environ['LDAP_HOSTNAME']
# LDAP port 389 = unencrypted, 636 = encrypted
PORT = 389
# Use SSL? True/False
USE_SSL = False
# LDAP bind user DN
BIND = os.environ['LDAP_USER']
# LDAP bind user password
BIND_PW = os.environ['LDAP_PASSWORD']
# Base search DN
SEARCH = os.environ['LDAPXLS_SEARCHBASE']
# All users regardless deactivated or activated
SEARCH_FILTER = os.environ['LDAPXLS_SEARCH_FILTER']
# All users who are not deactivated
#SEARCH_FILTER = '(&(objectclass=user)(sAMAccountName=*)(!(UserAccountControl:1.2.840.113556.1.4.803:=2)))'
# All users who are not deactivated and in special group
#SEARCH_FILTER = '(&(objectclass=user)(sAMAccountName=*)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(memberOf=CN=b_testgruppe und restlicher DN))'
# Output file
FILE = os.environ['OUTPUTFILE']

NCDIR = os.environ['NCDIR']
########################################################################################################################
if os.environ['DEBUG_DEVELOP']=='true' :
  import pdb

def main():
    
    # Connect to LDAP and query
    server = ldap3.Server(LDAP_SERVER, port=389, use_ssl=USE_SSL)
    conn = ldap3.Connection(server, BIND, BIND_PW, auto_bind=True)
    conn.search(SEARCH, SEARCH_FILTER, attributes=['memberOf', 'mail', 'uid'])
    response = json.loads(conn.response_to_json())

    def get_cn(cn_str):
        cn = re.findall(r"cn=([^,]*),?", cn_str)[0]
        return cn

    buffer_users = {}
    buffer_user_in_group = {}
    
    
    

    for entry in response['entries']:
        # Get short and long username
        long_username = entry['attributes']['mail'] or get_cn(entry['dn'])
        
        short_username = entry['attributes']['uid'][0]
        

        # append to users dir
        buffer_users[short_username] = long_username
        

        # go trough groups
        for group in entry['attributes']['memberOf']:
            # add to group buffer
            group_name = get_cn(group)
            if group_name not in buffer_user_in_group:
                buffer_user_in_group[group_name] = []
            if short_username not in buffer_user_in_group[group_name]:
                buffer_user_in_group[group_name].append(short_username)

    matrix = {}
    length_cell = 0

    for group, users in buffer_user_in_group.items():
        matrix[group] = {}

        for user, long_user in buffer_users.items():
            index = "%s - %s " % (user, long_user)
            # determine width of 1 column
            index_length = len(index)
            if index_length > length_cell:
                length_cell = index_length

            if user in users:
                matrix[group][index] = "X"
            else:
                matrix[group][index] = "-"
    
    if os.environ['DEBUG_DEVELOP']=='true' :
          pdb.set_trace()
    matrix = dict(sorted(matrix.items()))
    

    # generate data matrix with pandas
    a = pd.DataFrame(matrix)
    bio = BytesIO()

    # create excel file
    # writer = pd.ExcelWriter(OUTPUTDIR+FILE, engine='xlsxwriter')
    writer = pd.ExcelWriter(bio, engine='xlsxwriter')

    # write pandas matrix to sheet1
    a.to_excel(writer, sheet_name="Sheet1", startrow=1, header=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # format header line
    header_format = workbook.add_format(
        {
            'bold': True,
            'valign': 'bottom',
            'fg_color': '#D7E4BC',
            'border': 1,

        }
    )
    rotation = int(os.environ['LDAPXLS_ROTATION'])
    if rotation>0 :
        # set header line text rotation to 90 degree
        header_format.set_rotation(rotation)

    # apply header format
    for col_num, value in enumerate(a.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)

    # format for X cells
    format2 = workbook.add_format(
        {
            'bg_color': '#C6EFCE',
            'font_color': '#006100'
        }
    )

    # set autofilter in first line
    cols_count = len(a.columns.values)
    worksheet.autofilter(0, 0, 0, cols_count)

    # set column width
    worksheet.set_column(0, 0, length_cell+1)
    worksheet.set_column(1, cols_count, 3)

    # freeze panes
    worksheet.freeze_panes(1, 1)

    # conditional formatting
    worksheet.conditional_format('A1:ZA65535', {
        'type': 'cell',
        'criteria': '=',
        'value': '"X"',
        'format': format2
    })

    
    # save excel file
    # fix the formatting
    worksheet.autofit()
    # writer.close()

    writer.close()
    bio.seek(0)
    workbook = bio.read()


    # upload to NC
    
    nc = Nextcloud(nextcloud_url=os.environ['NC_URL'], nc_auth_user=os.environ['NC_USER'], nc_auth_pass=os.environ['NC_PASS'])
    nc.files.upload('/Kollegium/'+FILE,workbook)


if __name__ == "__main__":
    main()


# all credits to: https://github.com/lanbugs/get_ad_right_matrix/blob/main/get_ad_right_matrix.py