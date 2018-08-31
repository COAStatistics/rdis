import pyodbc
import sys

class DatabaseConnection:
    FARMER_INSURANCE =\
    """
    SELECT [id]
    FROM [farmer_insurance].[dbo].[105Peasant]
    WHERE id = convert(nvarchar(255), ?)
    """
    
    ELDER_ALLOWANCE =\
    """
    SELECT [身份證字號]
    FROM [elderly_allowance].[dbo].[105]
    WHERE [身份證字號] = convert(nvarchar(255), ?)
    """
    
    LANDLORD =\
    """
    SELECT [ownerID]
    FROM [small & big].[dbo].[105rent_oid_index_view]
    WHERE [ownerID] = convert(nvarchar(255), ?)
    """
    
    TENANT =\
    """
    SELECT [appID]
    FROM [small & big].[dbo].[105rent_id_index_view]
    WHERE [appID] = convert(nvarchar(255), ?)
    """
    
    TENANT_TRANSFER_SUBSIDY =\
    """
    SELECT [大佃農身份證號], SUM([補貼金額]) AS money
    FROM [small & big].[dbo].[105r_farm_temp]
    WHERE [大佃農身份證號] = convert(nvarchar(255), ?)
    GROUP BY [大佃農身份證號]
    """
    
    LANDLORD_RENT =\
    """
    SELECT [地主身份證號], SUM([政府應付]) AS money
    FROM [small & big].[dbo].[105r_pay]
    WHERE [地主身份證號] = convert(nvarchar(255), ?)
    GROUP BY [地主身份證號]
    """
    
    LANDLORD_RETIRE =\
    """
    SELECT [地主身份證號], SUM([政府應付]) AS money
    FROM [small & big].[dbo].[105r_paya]
    WHERE [地主身份證號]= convert(nvarchar(255), ?)
    GROUP BY [地主身份證號]
    """
    
    DISASTER =\
    """
    SELECT evt_name, applyCrop, applyArea as apr_area, subsidyAmount as sbdy_amt
    FROM [disaster].[dbo].[106acdList]
    WHERE [ownerID] = convert(nvarchar(255), ?)
    """
    
    pid = None
    args = 'Driver={SQL Server};Server=172.16.21.8;Database=%s;Trusted_Connection=yes;'
    
    def __init__(self, db_name):
        self.conn = pyodbc.connect(DatabaseConnection.args % db_name)
        self.cur = self.conn.cursor()

    def get_farmer_insurance(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.FARMER_INSURANCE, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return "Y"
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_elder_allowance(self) -> str:
        try:
            self.cur.execute(DatabaseConnection.ELDER_ALLOWANCE, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return "Y"
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_landlord(self):        
        try:
            self.cur.execute(DatabaseConnection.LANDLORD, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return "小"
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_tenant_farmer(self):
        try:
            self.cur.execute(DatabaseConnection.TENANT, DatabaseConnection.pid)
            if self.cur.fetchone() != None:
                return "大"
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
            
    def get_tenant_transfer_subsidy(self):        
        try:
            self.cur.execute(DatabaseConnection.TENANT_TRANSFER_SUBSIDY, DatabaseConnection.pid)
            row = self.cur.fetchone()
            if row != None:
                return str(int(row.money))
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
            
    def get_landlord_rent(self):
        try:
            self.cur.execute(DatabaseConnection.LANDLORD_RENT, DatabaseConnection.pid)
            row = self.cur.fetchone()
            if row != None:
                return str(int(row.money))
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
    
    def get_landlord_retire(self):
        try:
            self.cur.execute(DatabaseConnection.LANDLORD_RETIRE, DatabaseConnection.pid)
            row = self.cur.fetchone()
            if row != None:
                return str(int(row.money))
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
            
    def get_disaster(self):
        try:
            d_l = []
            self.cur.execute(DatabaseConnection.DISASTER, DatabaseConnection.pid)
            rows = self.cur.fetchall()
            if rows != None:
                for i in rows:
                    l = [i.evt_name, i.applyCrop, i.apr_area, int(i.sbdy_amt)]
                    d_l.append(l)
            return d_l
        except Exception:
            info = sys.exc_info()
            print(info[0], '\n', info[1])
        
    def close_conn(self):
        self.cur.close()
        self.conn.close()
    
db = DatabaseConnection('farmer_insurance')
DatabaseConnection.pid = 'L120248702'
db.get_farmer_insurance()
db.get_elder_allowance()
db.get_tenant_transfer_subsidy()
db.get_landlord_rent()
db.get_landlord()
db.get_landlord_retire()
db.get_disaster()
db.close_conn()