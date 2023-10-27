import mysql.connector
from config.dbconfig import MysqlConnStr
from sanic.log import logger

class MysqlService:

    def __init__(self):
         self.dbConn = self.getConnection()

    def getConnection(self):
        cnx = mysql.connector.connect(MysqlConnStr)
        return cnx

    def __exit__(self):
        if self.dbConn.is_connected(): 
            self.dbConn.close()    