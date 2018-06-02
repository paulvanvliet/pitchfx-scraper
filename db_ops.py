# -*- coding: utf-8 -*-
"""
Created on Mon May 21 09:56:07 2018

@author: rnpmv01
"""

import sqlite3
import configs


conn = sqlite3.connect(configs.db_path)
c = conn.cursor()
qry = open(configs.sql_create).read()
c.execute(qry)



conn.commit()
conn.close()