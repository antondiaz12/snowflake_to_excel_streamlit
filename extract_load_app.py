import streamlit
import pandas
import requests #New section to display fruityvice API response
import snowflake.connector
from urllib.error import URLError

streamlit.title("Exportación de SF a Excel")

my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
my_cur = my_cnx.cursor()
my_cur.execute("select * from pc_rivery_db.public.fruit_load_list")
my_data_rows = my_cur.fetchall()
streamlit.text("Fruit list")
streamlit.dataframe(my_data_rows)



