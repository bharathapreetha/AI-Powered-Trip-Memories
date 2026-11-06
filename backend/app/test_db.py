from app.database import get_db_connection

try:
    connection = get_db_connection()
    
    if connection.is_connected():
        print("Connection Sucessful")
        
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    
    tables = cursor.fetchall()
    
    print("Available tables", tables)
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print("DB Connection Failed", e)
    
              