import mysql.connector

db_conn = mysql.connector.connect(host="kafka-acit3855-lab6a.eastus2.cloudapp.azure.com", user="root", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE weather_forecast 
          (id INT NOT NULL AUTO_INCREMENT, 
           location_id INT NOT NULL,
           location_name VARCHAR(250) NOT NULL,
           weather VARCHAR(250) NOT NULL,
           temperature INT NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT weather_forecast_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE misc_weather
          (id INT NOT NULL AUTO_INCREMENT, 
           location_id INT NOT NULL,
           location_name VARCHAR(250) NOT NULL,
           precipitation VARCHAR(250) NOT NULL,
           humidity VARCHAR(250) NOT NULL,
           wind VARCHAR(250) NOT NULL,
           air_quality VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT misc_weather_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()