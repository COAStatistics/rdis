import linecache
import pyodbc
import sys
import re
from log import err_log, log

INFO_PATH = '..\\..\\info.txt'
class DatabaseConnection:
    FARMER_INSURANCE =\
    """
    SELECT [id]
    FROM [farmer_insurance].[dbo].[106Peasant]
    WHERE id = convert(nvarchar(255), ?)
    """
    
    ELDER_ALLOWANCE =\
    """
    SELECT [appID]
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
    SELECT [evt_name], [approveCrop], [apr_area], [sbdy_amt]
    FROM [disaster].[dbo].[107acdList_farmerSurvey]
    WHERE [appID] = convert(nvarchar(255), ?)
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
#     args = 'Driver={SQL Server};Server=172.16.21.8;Database=%s;Trusted_Connection=yes;'
    username = linecache.getline(INFO_PATH, 1)
    pwd = linecache.getline(INFO_PATH, 2)
    args = 'Driver={SQL Server};Server=172.16.21.8;Database=%s;UID='+ username.strip() +';PWD='+ pwd.strip() +''
    
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
            err_log.error(info[0], '\t', info[1])
    
    def get_elder_allowance(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.ELDER_ALLOWANCE, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return 'Y'
            else:
                return ''
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
    
    def get_landlord(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.LANDLORD, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return '小'
            else:
                return ''
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
    
    def get_tenant_farmer(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.TENANT, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return '大'
            else:
                return ''
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
            
    def get_tenant_transfer_subsidy(self) -> str:
        s = '0'
        try:
            self.cur.execute(DatabaseConnection.TENANT_TRANSFER_SUBSIDY, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            row = self.cur.fetchone()
            if row:
                s = str(int(row.money))
                try:
                    assert len(s) != 0 and s.isnumeric()
                except AssertionError:
                    err_log.error('AssertionError: ', self.get_crop_subsidy.__name__, ' id=', DatabaseConnection.pid, ' ', s)
        return s
            
    def get_landlord_rent(self) -> str:
        s = '0'
        try:
            self.cur.execute(DatabaseConnection.LANDLORD_RENT, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            row = self.cur.fetchone()
            if row:
                s = str(int(row.money))
                try:
                    assert len(s) != 0 and s.isnumeric()
                except AssertionError:
                    err_log.error('AssertionError: ', self.get_landlord_rent.__name__, ' id=', DatabaseConnection.pid, ' ', s)
        return s
    
    def get_landlord_retire(self) -> str:
        s = '0'
        try:
            self.cur.execute(DatabaseConnection.LANDLORD_RETIRE, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            row = self.cur.fetchone()
            if row:
                s = str(int(row.money))
                try:
                    assert len(s) != 0 and s.isnumeric()
                except AssertionError:
                    err_log.error('AssertionError: ', self.get_landlord_retire.__name__, ' id=', DatabaseConnection.pid, ' ', s)
        return s
            
    def get_disaster(self) -> list:
        d_l = []
        try:
            self.cur.execute(DatabaseConnection.DISASTER, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            rows = self.cur.fetchall()
            if rows:
                for i in rows:
                    l = [i.evt_name, i.approveCrop, str(round(i.apr_area, 4)), str(int(i.sbdy_amt))]
                    try:
                        assert len(l[0]) != 0 and len(l[1]) !=0 and float(l[2]) > 0 and int(l[3]) > 0
                    except AssertionError:
                        err_log.error('AssertionError: ', self.get_disaster.__name__, ' id=', DatabaseConnection.pid, ' ', l)
                    else:
                        d_l.append(l)
        return d_l
    
    def get_declaration(self) -> str:
        l = []
        try:
            self.cur.execute(DatabaseConnection.DECLARATION, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            rows = self.cur.fetchall()
            if rows:
                for record in rows:
                    if record.RICE1 > 0:
                        l.append('梗稻')
                    if record.RICE2 > 0:
                        l.append('秈稻')
                    if record.RICE3 > 0:
                        l.append('糯稻')
                    if record.CHGCD1 != '無':
                        for crop_name in record.CHGCD1.split(','):
                            if crop_name not in l:
                                l.append(crop_name)
                    if record.CHGCD2 != '無':
                        for crop_name in record.CHGCD2.split(','):
                            if crop_name not in l:
                                l.append(crop_name)
                    if record.CHGCD3 != '無':
                        for crop_name in record.CHGCD3.split(','):
                            if crop_name not in l:
                                l.append(crop_name)
            if l:
                return ','.join(l)
            else:
                return ''

    def get_crop_subsidy(self) -> list:
        c_s_l = []
        try: 
            self.cur.execute(DatabaseConnection.CROP_SUBSIDY, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            rows = self.cur.fetchall()                
            if rows:
                for record in rows:
                    l = list(record)
                    try:
                        assert float(l[1]) > 0 and l[2] == '1'
                    except AssertionError:
                        err_log.error('AssertionError: ', self.get_crop_subsidy.__name__, ' id=', DatabaseConnection.pid, ' ', l)
                    else:
                        c_s_l.append(l)
        return c_s_l

    def get_livestock(self) -> dict:
        result = {}
        try:
            self.cur.execute(DatabaseConnection.LIVESTOCK, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            rows = self.cur.fetchall()
            if rows:
                for i in rows: 
                    livestock = [None] * 7
                    field_name = i.FieldName
                    livestock[0] = i.InvSeason.strip()
                    livestock[1] = i.Name
                    livestock[2] = str(i.RaiseCount)
                    livestock[3] = str(i.SlaughterCount)
                    livestock[4] = '無'
                    livestock[5] = '0'
                    livestock[6] = '106' if i.InvYear == '2017' else '107'
                    
                    if re.match('[^蛋].*[雞|鴨|鵝|鵪鶉|鴿]', livestock[1].strip()) or livestock[1].strip().find('蛋鴨') != -1:
                        if livestock[2] == '0':
                            if livestock[3] == '0':
                                break
                            else:
                                livestock[2] = '出清'
                        if livestock[1].strip() != '蛋雞':
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
        return result
    
    def get_scholarship(self) -> str:
        s = ''
        try:
            self.cur.execute(DatabaseConnection.SCHOLARSHIP, DatabaseConnection.pid)
        except Exception:
            info = sys.exc_info()
            err_log.error(info[0], '\t', info[1])
        else:
            rows = self.cur.fetchall()             
            if rows:
                for i in rows:
                    s += i.name + '-' + str(i.scholarship) + ','
        
                log.info(DatabaseConnection.pid, ', scholarship = ', s)
        return s[:-1]
    
    def close_conn(self) -> None:
        self.cur.close()
        self.conn.close()


# db = DatabaseConnection('farmer_insurance')
# DatabaseConnection.pid = 'Q121362090'
# db.get_tenant_transfer_subsidy()
# db.get_landlord_rent()
# db.get_disaster()
# db.get_landlord_retire()
# db.get_declaration()
# db.get_crop_subsidy()
# db.get_livestock()
# db.get_scholarship()