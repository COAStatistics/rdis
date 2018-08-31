import pyodbc

class DatabaseConnection:
    FARMER_INSURANCE = "select * from [farmer_insurance].[dbo].[105Peasant] where id = convert(nvarchar(255), ?)"

    pid = None
    args = 'Driver={SQL Server};Server=172.16.21.8;Database=%s;Trusted_Connection=yes;'
    
    def __init__(self, db_name):
        self.conn = pyodbc.connect(DatabaseConnection.args % db_name)
        self.cur = self.conn.cursor()

    def get_farmer_insurance(self) -> str:
        self.cur.execute(DatabaseConnection.FARMER_INSURANCE, DatabaseConnection.pid)
        if self.cur.fetchone() != None:
            return "Y"
        
    def close_conn(self):
        self.cur.close()
        self.conn.close()
db = DatabaseConnection('farmer_insurance')
DatabaseConnection.pid = 'A100001651'
db.get_farmer_insurance()
db.close_conn()