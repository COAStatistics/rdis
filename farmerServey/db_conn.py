'''
Created on 2018年7月6日

@author: so6370
'''
import pyodbc

conn = pyodbc.connect('Driver={SQL Server};Server=172.16.21.8;Database=fallow;Trusted_Connection=yes;')
cur = conn.cursor()
# crop_stat = 'select * from cropCode where codeSmall = ?'
# crop_code = '001'
crop_stat = 'select top 100 * from cropCode'
cur.execute(crop_stat)
# cur.execute(crop_stat, crop_code)
rows = cur.fetchall()
cur.close()
conn.close()

for row in rows:
    print(row)