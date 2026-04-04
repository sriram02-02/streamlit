import data_extraction 
# from data_extraction import get_map_insurance, get_map_transaction, get_map_user
# from data_extraction import get_top_insurance, get_top_transaction, get_top_user
import pymysql
from sqlalchemy import create_engine

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="NewStrongPassword123"
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS phonepe")

engine = create_engine("mysql+pymysql://root:NewStrongPassword123@localhost:3306/phonepe")





tables = {
    "agg_insurance":    data_extraction.get_agg_insurance(),
    "agg_transaction": data_extraction.get_agg_transaction(),
    "agg_user": data_extraction.get_agg_user(),
    "map_insurance": data_extraction.get_map_insurance(),
    "map_transaction": data_extraction.get_map_transaction(),
    "map_user": data_extraction.get_map_user(),
    "top_insurance": data_extraction.get_top_insurance(),
    "top_transaction": data_extraction.get_top_transaction(),
    "top_user": data_extraction.get_top_user()
}

for name, df in tables.items():
    df.to_sql(name, con=engine, if_exists="replace", index=False)

print("All tables stored successfully in the database.")
