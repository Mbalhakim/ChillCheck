from db import Database

class User():
    def __init__():
        pass

class MlxData():
    def __init__(self, id_ = 0, min_temp = 0, max_temp = 0, avg_temp = 0, created_at = ""):
        self.id_ = id_
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.avg_temp = avg_temp
        self.created_at = created_at
    
    def find(self, column, value):
        return Database().find("MlxData", column, value)

    def create(self):
        query = 'INSERT INTO MlxData (min_temp, max_temp, avg_temp) values (?, ?, ?)'
        data = (self.min_temp, self.max_temp, self.avg_temp)
        Database().create(query, data)
    
    def delete_by_id(self, id_):
        Database().delete_by_id("MlxData", id_)

class ShtData():
    def __init__():
        pass
