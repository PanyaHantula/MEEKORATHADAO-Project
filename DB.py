# ###########################################
#       Data Base SQL Class                 #
#       used mysql.comnector library        #
# ###########################################
import mysql.connector

class Database:
    def __init__(self,):
        self.connect_db()
    
    # Connect DB           
    def connect_db(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="p@ssw0rd",
                database="meekorat5dow"
                )    
            self.cursor = self.db.cursor()
            print("#: Connect SQL Database complete")
        except:
            print("#: Error connecting Database")   
        
    def select_all(self):
        cmd = "SELECT * FROM dataLoger"
        self.cursor.execute(cmd)
        for row in self.cursor.fetchall():
            print (row)
    
    def query(self,cmd):
        self.cursor.execute(cmd)
        return self.cursor.fetchall()
    
    
if __name__ == "__main__":
    db = Database()
    
    cmd = "SELECT * FROM dataLoger WHERE total_product = 9"
    resultes = db.query(cmd)
    for row in resultes:
        print (row)   
        
        
        
# import sys,sqlite3
# import mysql.connector

# try:
#     db = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="raspberry",
#         database="meekorat5dow"
#         )    

#     # Create a Cursor object to execute queries.
#     cur = db.cursor()
    
#     # Select data from table using SQL query.
#     cur.execute("SELECT * FROM dataLoger")
    
#     # print the first and second columns      
#     for row in cur.fetchall():
#         print (row)
# except:
#     print("Error connecting Database")       
