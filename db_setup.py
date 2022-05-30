import mysql.connector

mydb = mysql.connector.connect(
    host = "drowsyweb.c1cfape2fuwv.us-east-1.rds.amazonaws.com",
    user = "admin",
    password = "netflix123",
    database = "mydb"
)

mycursor = mydb.cursor()

print(mydb)

# mycursor.execute("SELECT username FROM auth_user")
# users = mycursor.fetchall()
# print(users, type(users))

# for i in users:
#     print(i[0])