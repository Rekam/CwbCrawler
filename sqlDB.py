import sqlite3
import os

class sqlDB:
    def __init__(self, dbName):
        # 建立資料夾 若不存在的話
        self.__create_dir('data')
        self.conn = sqlite3.connect(os.path.join('data', f"{dbName}.db"))
        print("Database Opened successfully")
        # 建立cursor變數
        self.cursorObj = self.conn.cursor()
        # 建立表格
        self.__createAllTables()
        # 若沒有數據則上網抓數據

    def __createAllTables(self):
        # 先檢查是否表格存在，若不存在的話，則建立表格
        if self.__checkTableExist("County") is False:
            self.__createCountyTable()
        if self.__checkTableExist("Station") is False:
            self.__createStationTable()
            
    def __create_dir(self, dirPath):
        if os.path.isdir(dirPath):
            print("資料夾存在")
        else:
            print("資料夾不存在，創建新的")
            os.makedirs(dirPath)
    
    def __createCountyTable(self):
        self.cursorObj.execute(f"CREATE TABLE County (countyName TEXT, countyIndex INTEGER, PRIMARY KEY(countyIndex))")
        print('County, Table created')
    
    def __createStationTable(self):
        self.cursorObj.execute(f"CREATE TABLE Station (StationCode TEXT, StationName TEXT, CountyIndex INTEGER NOT NULL, FOREIGN KEY(CountyIndex) REFERENCES County(countyIndex) ON UPDATE CASCADE ON DELETE CASCADE, PRIMARY KEY(StationCode))")
        print('Station, Table created')
    
    
    def checkTableIfEmpty(self, tableName):
        # 檢查 Table裏頭是否空的
        if self.__checkTableExist(tableName):
            result = self.cursorObj.execute(f"select count(*) from {tableName} Limit 1")
            if result.fetchall()[0][0]==0:
                return True
            else: return False
        else:
            return False
    
    def getTableList(self, tableName):
        self.cursorObj.execute(f'SELECT * FROM {tableName}')
        rows = self.cursorObj.fetchall()
        return rows
    
    def getStationListatCounty(self, tableName, countyIndex):
        rows = self.getTableList("Station")
        station = []
        for value in rows:
            if value[2]==countyIndex:
                station.append(value[1])
        return station
    
    def __checkTableExist(self, tableName):
        # 檢查資料表是否存在
        # https://pythonexamples.org/python-sqlite3-check-if-table-exists/
        #get the count of tables with the name
        self.cursorObj.execute(f" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tableName}' ")
        #if the count is 1, then table exists
        if self.cursorObj.fetchone()[0]==1:
            print(f'{tableName}, Table existed')
            exist = True
        else:
            print(f'{tableName}, Table does not exist')
            exist = False    
        return exist  
    
    def insertCountyTable(self, cwbInstance):
        # 放置所有城市
        tableName = "County"
        for idx, county in enumerate(cwbInstance.counties):
            try:
                self.cursorObj.execute(f"INSERT INTO {tableName} VALUES('{county}',{idx})")
            except Exception as e:
                print(f'錯誤訊息 {e}')
        self.conn.commit()
    
    def insertStationTable(self, cwbInstance):
        stationList = []
        tableName = "Station"
        for idx,station in enumerate(cwbInstance.allStations):
            for key, value in station.items():
                #print(key, value, idx)
                stationList.append((key,value,idx))
        try:
            self.cursorObj.executemany(f"INSERT INTO {tableName} VALUES(?,?,?)",stationList)
        except Exception as e:
            print(f'錯誤訊息 {e}')
        self.conn.commit()


    def deleteTableAllRows(self, tableName):
        sql = f'DELETE FROM {tableName}'
        self.cursorObj.execute(sql)
        self.conn.commit()