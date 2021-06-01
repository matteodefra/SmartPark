import pymysql.cursors

# Connect to the database


class Database:
    connection = None

    def __init__(self):
        print("Instantiating!")

    def connect_dbs(self):

        if self.connection is not None:
            return self.connection
        else:
            self.connection = pymysql.connect(host='localhost',
                 user='root',
                 password='PASSWORD',
                 database='datacollector',
                 cursorclass=pymysql.cursors.DictCursor)
            return self.connection
