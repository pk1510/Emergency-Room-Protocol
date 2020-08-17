import pymysql
import pandas as pd

df = pd.read_excel(r'E:\Prem\python\delta\data.xlsx')
db = pymysql.connect("localhost","username","password","controlRoom")
df = df.to_string(index=False)
try:
    df.to_sql(name='branch',con=db,if_exists='append',index=False)
except:
    db.rollback()
db.close()
