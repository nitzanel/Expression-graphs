import os
import sqlite3
from win32com.client import constants, Dispatch

#----------------------------------------
# get data from excel file
#----------------------------------------
XLS_FILE = os.getcwd() + "\\Female_Male_exp_levels_norm.xlsx"
ROW_SPAN = (2, 64871)
COL_SPAN = (1, 28)
app = Dispatch("Excel.Application")
app.Visible = True
index = 1
ws = app.Workbooks.Open(XLS_FILE).Sheets(1)
exceldata = [[ws.Cells(row, col).Value 
              for col in xrange(COL_SPAN[0], COL_SPAN[1])] 
             for row in xrange(ROW_SPAN[0], ROW_SPAN[1])]

#----------------------------------------
# create SQL table and fill it with data
#----------------------------------------
conn = sqlite3.connect('Female_Male_exp_levels_norm2.db')
c = conn.cursor()
c.execute('''CREATE TABLE exceltable (
   id TEXT,
   gene_name TEXT,
   chr INTEGER,
   start INTEGER,
   end INTEGER,
   GN_female TEXT,
   GN_male TEXT,
   MF_female TEXT,
   MF_male TEXT,
   DC_female TEXT,
   DC_male TEXT,
   B1ab_female TEXT,
   B1ab_male TEXT,
   CD19_female TEXT,
   CD19_male TEXT,
   NK_female TEXT,
   NK_male TEXT,
   T8_female TEXT,
   T8_male TEXT,
   T4_female TEXT,
   T4_male TEXT,
   Treg_female TEXT,
   Treg_male TEXT,
   NKT_female TEXT,
   NKT_male TEXT,
   Tgd_female TEXT,
   Tgd_male TEXT
 
)''')

for row in exceldata:
	c.execute('INSERT INTO exceltable VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
conn.commit()

#----------------------------------------
# display SQL data
#----------------------------------------
c.execute('SELECT * FROM exceltable')
for row in c:
    print row