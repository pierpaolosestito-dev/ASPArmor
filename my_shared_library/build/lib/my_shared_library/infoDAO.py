from database_connection_manager import DatabaseConnection


class Info:
    def __init__(self,username,executable,profile):
        self.username = username
        self.executable = executable
        self.profile = profile

    def __str__(self):
        return f"{self.username}::{self.executable}::{self.profile}"

class InfoDAO:
    def __init__(self,cursor):
        self.cursor = cursor

    def create(self, info : Info):
        query = """INSERT INTO info (username,executable,profile)
                    VALUES (?,?,?);"""
        self.cursor.execute(query,(info.username,info.executable,info.profile))
        return self.cursor.lastrowid

    def already_exists(self, info : Info):
        query = """SELECT 1 from info
                    WHERE username=? AND executable = ? AND profile = ?"""
        self.cursor.execute(query,(info.username,info.executable,info.profile))
        return self.cursor.fetchone() is not None

    def read_all(self):
        query = "SELECT * FROM info;"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete(self,info : Info):
        query = "DELETE FROM info WHERE username = ? and profile = ?;"
        self.cursor.execute(query,(info.username,info.profile))
        return self.cursor.rowcount > 0

    def delete_all(self):
        query = "DELETE from info;"
        self.cursor.execute(query)
        self.cursor.connection.commit()
        return self.cursor.rowcount

