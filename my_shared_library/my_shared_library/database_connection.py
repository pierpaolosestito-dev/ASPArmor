import sqlite3
import os


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.directory_path = "./tmp/sapparm/"
        self.database_path = os.path.join(self.directory_path,"sapparm.db")

        if not os.path.exists(self.directory_path):
            try:
                os.makedirs(self.directory_path,exist_ok=True)
            except PermissionError:
                print("Permission Error: You do not have the right permission to create the directory")

        try:
            self.connection = sqlite3.connect(self.database_path)
            print(f"Connessione al database: {self.database_path}")
        except sqlite3.Error as e:
            print(f"Errore durante la connessione al database: {e}")
            exit(1)

        # Creazione del cursore e delle tabelle
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Query per creare la tabella info
        create_info_table_query = """
        CREATE TABLE IF NOT EXISTS info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            executable TEXT NOT NULL,
            profile TEXT NOT NULL
        );
        """

        # Query per creare la tabella db_content
        create_db_content_table_query = """
        CREATE TABLE IF NOT EXISTS kcontent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            last_row INTEGER NOT NULL,
            creation_date TEXT NOT NULL
        );
        """

        # Esecuzione delle query
        self.cursor.execute(create_info_table_query)
        self.cursor.execute(create_db_content_table_query)

        # Conferma delle modifiche
        self.connection.commit()


    def get_cursor(self):
        return self.cursor

    def execute_query(self,query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            return False

    def close(self):
        if self.connection:
            self.connection.close()
            DatabaseConnection._instance = None


