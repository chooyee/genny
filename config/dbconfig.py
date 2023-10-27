from config.config import globalConfig

def MysqlConnStr():
    return f'user={globalConfig["mysql"]["user"]}, 
    password={globalConfig["mysql"]["pwd"]},host={globalConfig["mysql"]["host"]},
    database={globalConfig["mysql"]["name"]}'