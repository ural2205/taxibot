import sqlite3 as sql

class DataBase:
    def __init__(self, path: str):
        self.connection = sql.connect(path)
        self.cursor = self.connection.cursor()

    def getColumnNames(self, table_name:str) -> list:
        columns =self.cursor.execute(f'pragma table_info({table_name})').fetchall()
        col_names = [i[1] for i in columns]
        return col_names


    def addRow(self, table_name:str, *argv):
        col_names = self.getColumnNames(table_name)
        if len(col_names) != len(argv):
            return None
        with self.connection:
            self.cursor.execute(f'''
                INSERT OR IGNORE INTO {table_name}({', '.join(col_names)})
                    VALUES ({', '.join(['?'] * len(argv))})
                ''', argv)
            self.connection.commit()
            return True
    
    def deleteRow(self, table_name:str, id:int):
        self.cursor.execute(f''' 
                DELETE FROM {table_name}
                    WHERE id = {id}
        ''')
        self.connection.commit()
    
    def getRow(self, table_name:str, serch_value, serch_column:str, fetch_column: str)->list:
        return self.cursor.execute(f'''
                            SELECT {fetch_column}
                            FROM {table_name}
                            WHERE {serch_column} = ?
                                ''', [serch_value]).fetchone()
    
    def showAll(self, table_name:str = 'Users'):
        return self.cursor.execute(f"SELECT * From {table_name}").fetchall()

    def getTelNum(self, table_name: str, col_name: str, id: int):
        return self.cursor.execute(f"SELECT {col_name} FROM {table_name} WHERE id = {id}").fetchone()

    def incCell(self, table_name:str, id:int, *args):
        columns = ', '.join([f"{arg} = {arg} + 1" for arg in args])
        query = f"UPDATE {table_name} SET {columns} WHERE id = ?"
        self.cursor.execute(query, (id,))
        self.connection.commit()


    def isExist(self, table_name:str, col_name:str, value)-> bool:
        count = self.cursor.execute(f''' 
            SELECT COUNT(*)
                FROM {table_name}
                WHERE {col_name} = ?
        ''', (value,)).fetchone()
        return count[0] != 0
    
    def OnlineCount(self):
        count = self.cursor.execute(f'''
            SELECT COUNT(*)
                FROM drivers
                WHERE is_online = 1
''').fetchone()
        return count[0]
    
    def nullColmn(self, table_name:str, col_name:str):
        self.cursor.execute(f"UPDATE {table_name} SET {col_name} = 0")
        self.connection.commit()
    
    def makeOnline(self, id:int):
        self.cursor.execute(f"UPDATE drivers set is_online = 1 WHERE id =  {id}")
        self.connection.commit()

    def makeOflineAll(self):
        self.cursor.execute(f"UPDATE drivers set is_online = 0")
        self.connection.commit()

    
    def makeOfline(self,id:int):
        self.cursor.execute(f"UPDATE drivers set is_online = 0 WHERE id =  {id}")
        self.connection.commit()
    
    
    
 
