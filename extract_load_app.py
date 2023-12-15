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
streamlit.dataframe(my_data_rows)
add_my_fruit = st.text_input('What fruit would you like to add?')
streamlit.button('Add a Fruit to the List')
my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
back_from_function = insert_row_snowflake(add_my_fruit)
streamlit.text(back_from_function)
