import pyodbc
import sys
import re

class DatabaseConnection:
    FARMER_INSURANCE =\
    """
    SELECT [id]
    FROM [farmer_insurance].[dbo].[106Peasant]
    WHERE id = convert(nvarchar(255), ?)
    """
    
    ELDER_ALLOWANCE =\
    """
    SELECT [身份證字號]
    FROM [elderly_allowance].[dbo].[raw_106]
    WHERE [appID] = convert(nvarchar(255), ?)
    """
    
    LANDLORD =\
    """
    SELECT [ownerID]
    FROM [small & big].[dbo].[107tenantList_oid_index_view]
    WHERE [ownerID] = convert(nvarchar(255), ?)
    """
    
    TENANT =\
    """
    SELECT [appID]
    FROM [small & big].[dbo].[107tenantList_id_index_view]
    WHERE [appID] = convert(nvarchar(255), ?)
    """
    
    TENANT_TRANSFER_SUBSIDY =\
    """
    SELECT [大佃農身份證號], SUM([補貼金額]) AS money
    FROM [small & big].[dbo].[106tenantTransfer]
    WHERE [大佃農身份證號] = convert(nvarchar(255), ?)
    GROUP BY [大佃農身份證號]
    """
    
    LANDLORD_RENT =\
    """
    SELECT [地主身份證號], SUM([政府應付]) AS money
    FROM [small & big].[dbo].[106landlordRent]
    WHERE [地主身份證號] = convert(nvarchar(255), ?)
    GROUP BY [地主身份證號]
    """
    
    LANDLORD_RETIRE =\
    """
    SELECT [地主身份證號], SUM([政府應付]) AS money
    FROM [small & big].[dbo].[106landlordRetire]
    WHERE [地主身份證號]= convert(nvarchar(255), ?)
    GROUP BY [地主身份證號]
    """
    
    DISASTER =\
    """
    SELECT [evt_name], [apr_crop], [apr_area], [sbdy_amt]
    FROM [disaster].[dbo].[105acdList_farmerSurvey]
    WHERE [pid] = convert(nvarchar(255), ?)
    """
    
    DECLARATION =\
    """
    SELECT [RICE1], [RICE2], [RICE3], [CHGCD1], [CHGCD2], [CHGCD3]
    FROM [fallow].[dbo].[107DCL_farmerSurvey]
    WHERE [appID] = convert(nvarchar(255), ?)
    """
    
    CROP_SUBSIDY =\
    """
    SELECT [crop], [price], [period]
    FROM [fallow].[dbo].[107transferSubsidy_farmerSurvey]
    WHERE [id] = convert(nvarchar(255), ?)
    """
    
    LIVESTOCK =\
    """
    SELECT *
    FROM [nais3].[dbo].[107farmerSurvey_livestock]
    WHERE [FarmerId] = convert(nvarchar(255), ?)
    """
    
    SCHOLARSHIP =\
    """
    SELECT [name],[scholarship]
    FROM [scholarships].[dbo].[105Y_farmerSurvey]
    WHERE [id] = convert(nvarchar(255), ?)
    """
    
    pid = None
    args = 'Driver={SQL Server};Server=172.16.21.8;Database=%s;Trusted_Connection=yes;'
    
    def __init__(self, db_name='fallow'):
        self.conn = pyodbc.connect(DatabaseConnection.args % db_name)
        self.cur = self.conn.cursor()

    def get_farmer_insurance(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.FARMER_INSURANCE, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return "Y"
            else:
                return ''
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_elder_allowance(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.ELDER_ALLOWANCE, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return 'Y'
            else:
                return ''
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_landlord(self) -> str:        
        try:
            self.cur.execute(DatabaseConnection.LANDLORD, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return '小'
            else:
                return ''
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_tenant_farmer(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.TENANT, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return '大'
            else:
                return ''
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
            
    def get_tenant_transfer_subsidy(self) -> str:        
        try:
            self.cur.execute(DatabaseConnection.TENANT_TRANSFER_SUBSIDY, DatabaseConnection.pid)
            row = self.cur.fetchone()
            if row != None:
                return str(int(row.money))
            else:
                return '0'
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
            
    def get_landlord_rent(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.LANDLORD_RENT, DatabaseConnection.pid)
            row = self.cur.fetchone()
            if row != None:
                return str(int(row.money))
            else:
                return '0'
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_landlord_retire(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.LANDLORD_RETIRE, DatabaseConnection.pid)
            row = self.cur.fetchone()
            if row != None:
                return str(int(row.money))
            else:
                return '0'
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
            
    def get_disaster(self) -> list:
        d_l = []
        try:
            self.cur.execute(DatabaseConnection.DISASTER, DatabaseConnection.pid)
            rows = self.cur.fetchall()
            if rows != None:
                for i in rows:
                    l = [i.evt_name, i.apr_crop, str(round(i.apr_area, 4)), str(int(i.sbdy_amt))]
                    d_l.append(l)
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
        else:
            return d_l
    
    def get_declaration(self) -> str:
        l = []
        try:
            self.cur.execute(DatabaseConnection.DECLARATION, DatabaseConnection.pid)
            rows = self.cur.fetchall()
            if rows != None:
                for i in rows:
                    if i.RICE1 > 0:
                        l.append('梗稻')
                    if i.RICE2 > 0:
                        l.append('秈稻')
                    if i.RICE3 > 0:
                        l.append('糯稻')
                    if i.CHGCD1 != '無':
                        for j in i.CHGCD1.split(','):
                            if j not in l:
                                l.append(j)
                    if i.CHGCD2 != '無':
                        for j in i.CHGCD2.split(','):
                            if j not in l:
                                l.append(j)
                    if i.CHGCD3 != '無':
                        for j in i.CHGCD3.split(','):
                            if j not in l:
                                l.append(j)
            if len(l) > 0:
                return ','.join(l)
            else:
                return ''
                        
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_crop_subsidy(self) -> list:
        c_s_l = []
        try: 
            self.cur.execute(DatabaseConnection.CROP_SUBSIDY, DatabaseConnection.pid)
            rows = self.cur.fetchall()                
            if rows != None:
                for i in rows:
                    c_s = [None] * 3
                    c_s[0] = i.crop
                    c_s[1] = i.price
                    c_s[2] = i.period
                    c_s_l.append(c_s)
            return c_s_l
        
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_livestock(self) -> dict:
        result = {}
        try:
            self.cur.execute(DatabaseConnection.LIVESTOCK, DatabaseConnection.pid)
            rows = self.cur.fetchall()
            if rows != None:
                for i in rows: 
                    livestock = [None] * 7
                    field_name = i.FieldName
                    livestock[0] = i.InvSeason.strip()
                    livestock[1] = i.Name
                    livestock[2] = str(i.RaiseCount)
                    livestock[3] = str(i.SlaughterCount)
                    livestock[4] = '無'
                    livestock[5] = '0'
                    livestock[6] = '105' if i.InvYear == '2016' else '106'
                    if re.match('^蛋.*[雞|鴨|鵝|鵪鶉|鴿]', livestock[1].strip()):
                        if livestock[2] == '0':
                            if livestock[3] == '0':
                                break
                            else:
                                livestock[2] = '出清'
                        livestock[3] = ''
                    if i.MilkCount != 0:
                        livestock[4] = '牛乳' if '牛' in livestock[1] else '羊乳'
                        livestock[5] = str(i.MilkCount)
                    if i.AntlerCount != 0:
                        livestock[4] = '鹿茸'
                        livestock[5] = str(i.AntlerCount)
                    if i.EggCount != 0:
                        livestock[4] = '蛋'
                        livestock[5] = str(i.EggCount)
                    if field_name in result:
                        result.get(field_name).append(livestock)
                    else:
                        livestock_data = []
                        livestock_data.append(livestock)
                        result[field_name] = livestock_data
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
        return result
    
    def get_scholarship(self) -> str:
        s = ''
        try:
            self.cur.execute(DatabaseConnection.SCHOLARSHIP, DatabaseConnection.pid)
            rows = self.cur.fetchall()             
            if rows != None:
                for i in rows:
                    s += i.name + '-' + str(i.scholarship) + ','
        
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
        return s[:-1]
    
    def close_conn(self) -> None:
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':
    db = DatabaseConnection('farmer_insurance')
    DatabaseConnection.pid = 'P101953950'
    db.get_farmer_insurance()
    db.get_elder_allowance()
    db.get_tenant_transfer_subsidy()
    db.get_landlord_rent()
    db.get_landlord()
    db.get_landlord_retire()
    db.get_disaster()
    db.get_declaration()
    db.get_crop_subsidy()
    db.get_livestock()
    db.get_scholarship()
    db.close_conn()