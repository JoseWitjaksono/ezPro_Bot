import logging
import time
import mysql.connector


class DB:
    conn = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host='10.112.82.94',
            database='daman',
            user='ikrom',
            password='akuadmindb')

    def query(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except (AttributeError, mysql.connector.OperationalError):
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
        return cursor

    def commit(self):
        self.conn.commit()
