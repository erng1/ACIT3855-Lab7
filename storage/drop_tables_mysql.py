import mysql.connector

db_conn = mysql.connector.connect(host="kafka-acit3855-lab6a.eastus2.cloudapp.azure.com", user="root", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  DROP TABLE weather_forecast, misc_weather
                  ''')

db_conn.commit()
db_conn.close()