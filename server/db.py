
class Database:
    import sqlite3

    def __init__(self):
        pass
    
    def get_connection(self):
        """Get database connection"""
        return Database.sqlite3.connect("acs.db")
    
    def get_cursor(self, con):
        """Get cursor from connection"""
        cur = con.cursor()
        return cur
    
    def find_all(self, table):
        """Get all rows in the table"""
        con = self.get_connection()
        cur = self.get_cursor(con)

        query = f"SELECT rowid, * from {table}"
        rows = cur.execute(query).fetchall()
        cur.close()
        con.close()
        return rows

    def find(self, table, column, value):
        """Get table row by column and value"""
        con = self.get_connection()
        cur = self.get_cursor(con)

        query = f"SELECT rowid, * from {table} WHERE {column} = ?;"
        row = cur.execute(query, (value,)).fetchone()
        cur.close()
        con.close()
        return row

    def create(self, table, data):
        """Insert a new row with data into the table"""
        con = self.get_connection()
        cur = self.get_cursor(con)

        placeholders = '?,' * len(data)
        placeholders = placeholders[:-1]

        query = f"INSERT INTO {table} VALUES ({placeholders});"
        cur.execute(query, data)
        con.commit()
        cur.close()
        con.close()

    def delete_by_id(self, table, rowid):
        """Delete table row by rowid"""
        con = self.get_connection()
        cur = self.get_db_cursor(con)
        
        query = f"DELETE FROM {table} WHERE rowid = ?;"
        cur.execute(query, (rowid,))
        con.commit()
        cur.close()
        con.close()