import MySQLdb
import os
import numpy as np
import matplotlib.pyplot as ply
from functionSet import *

username = "root"
password = "admin"

f_initConn(username, password, "eecs564")
f_executeScriptsFromFile("tbl_create.sql")

print "this may take roughly 10 minutes"
f_run()
print "finish feeding data to table Data"

print "begin forming table Name"
f_formNameTable()
print "finish creating table Name "

print "begin forming table NameInfo"
f_formNameInfoTable()
print "finish creating table NameInfo"

print "the prepare work is done! Have fun!"