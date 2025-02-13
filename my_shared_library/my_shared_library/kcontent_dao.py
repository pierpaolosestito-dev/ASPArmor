from .database_connection import DatabaseConnection 
from datetime import datetime
class KContent:
	def __init__(self,content,last_row,creation_date):
		self.content = content
		self.last_row = last_row  
		self.creation_date = creation_date

	def __str__(self):
		return f"{self.content} created at {self.creation_date}"


class KContentDAO:
	def __init__(self,cursor):
		self.cursor = cursor 

	def create(self, content:str,last_row:int):
		creation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		query = """INSERT INTO kcontent (content,last_row,creation_date)
					VALUES (?,?,?);"""
		self.cursor.execute(query,(content,last_row,creation_date))
		self.cursor.connection.commit()
		return self.cursor.lastrowid

	def read_last_record(self):
		query = """SELECT content,last_row,creation_date
					FROM kcontent
					ORDER BY id DESC
					LIMIT 1;"""
		self.cursor.execute(query)
		result = self.cursor.fetchone()
		if result:
			return KContent(content=result[0],last_row=result[1],creation_date=result[2])
		return None

	def read_all(self):
		query = """SELECT content,last_row,creation_date
					FROM kcontent;"""
		self.cursor.execute(query)
		results = self.cursor.fetchall()
		kcontent_list = []
		for result in results:
			kcontent_list.append(KContent(content=result[0],last_row=result[1],creation_date=result[2]))
		return kcontent_list 

	def delete_last_record(self):
		query = """DELETE FROM kcontent
					WHERE id = (
						SELECT id 
						FROM kcontent
						ORDER BY id DESC
						LIMIT 1 
						);"""
		self.cursor.execute(query)
		self.cursor.connection.commit()
		return self.cursor.rowcount()
	
	def delete_all(self):
		query = "DELETE FROM kcontent;"			
		self.cursor.execute(query)
		self.cursor.connection.commit()
		return self.cursor.rowcount
