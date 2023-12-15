import streamlit
import pandas
import requests #New section to display fruityvice API response
import snowflake.connector
from urllib.error import URLError

streamlit.title("Import - from Streamlit to Snowflake")

##  
def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  return fruityvice_normalized

streamlit.header("Fruityvice Fruit Advice!")
try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error("Please select a fruit to get information")
  else:
    back_from_function = get_fruityvice_data(fruit_choice)
    streamlit.dataframe(back_from_function)
except URLError as e:
  streamlit.error()

streamlit.header("View Our Fruit List - Add You Favorites!")
def get_fruit_load_list():
  with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()

if streamlit.button('Get Fruit Load List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  info = streamlit.dataframe(my_data_rows)
  info.columns = ['FRUIT', 'QUANTITY', 'COLOR']


def insert_row_snowflake(new_fruit, new_qty, new_color):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("insert into fruit_load_list(FRUIT_NAME) values ('"+new_fruit+"')")
    my_cur.execute("insert into fruit_load_list(FRUIT_QTY) values ('"+new_qty+"')")
    my_cur.execute("insert into fruit_load_list(FRUIT_COLOR) values ('"+new_color+"')")
    return "Thanks for adding " + new_fruit + new_qty + new_color

add_fruit = streamlit.text_input('Which fruit')
add_qty = streamlit.text_input('Quantity?')
add_color = streamlit.text_input('Which color')
if streamlit.button('Add a Fruit to the List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  back_from_function = insert_row_snowflake(add_fruit, add_qty, add_color)
  streamlit.text(back_from_function)
  

## STOP!!
streamlit.stop()
