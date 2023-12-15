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

if streamlit.button('Get Fruit List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  info = streamlit.dataframe(my_data_rows)


def insert_row_snowflake(new_fruit, new_qty, new_color):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("insert into fruit_load_list(FRUIT_NAME, FRUIT_QTY, FRUIT_COLOR) values ('"+new_fruit+"','"+new_qty+"','"+new_color+"')")
    return "Thanks for adding fruit datd"

#def remove_row_snowflake(remove_data):
#  with my_cnx.cursor() as my_cur:
#    my_cur.execute("delete from fruit_load_list where  ('"+new_fruit+"','"+new_qty+"','"+new_color+"')")
#    return "Thanks for adding fruit datd"

add_fruit = streamlit.text_input('Add a fruit')
add_qty = streamlit.text_input('Add a quantity')
add_color = streamlit.text_input('Add a color')
if streamlit.button('Click to add data'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  back_from_function = insert_row_snowflake(add_fruit, add_qty, add_color)
  streamlit.text(back_from_function)

streamlit.header("Would you like to remove a fruit? Specify it!")
my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
my_data_rows = get_fruit_load_list()
my_cnx.close()
info = streamlit.dataframe(my_data_rows)
fruit_box = streamlit.selectbox('Choose the data', my_data_rows([0],[0])


## STOP!!
streamlit.stop()
