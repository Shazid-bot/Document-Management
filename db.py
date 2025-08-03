import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smart_file_manager'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
