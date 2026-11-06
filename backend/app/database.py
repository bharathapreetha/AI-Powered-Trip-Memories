import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Ai_Engineer_2026",
        database="ai_powered_trip_memories",
        port=3306
    )
    
    return connection

