#!/usr/bin/env python3

import mysql.connector

def connect():
    cnx = mysql.connector.connect(
        host = "localhost",
        user = "fulu",
        password = "fulu",
        database = "fulu"
    )
    cursor = cnx.cursor()

    return (cnx, cursor)
