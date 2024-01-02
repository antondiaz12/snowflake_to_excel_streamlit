import streamlit
import pandas
import requests #New section to display fruityvice API response
import snowflake.connector
from urllib.error import URLError

streamlit.title("Import - from Streamlit to Snowflake")


def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  return fruityvice_normalized

def get_fruit_load_list():
  with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()

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

if streamlit.button('Get Fruit List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  table = pandas.DataFrame(my_data_rows)
  table.columns = ["Fruits"]
  streamlit.dataframe(table)

# FUNCTIONS: ADD, REMOVE, UPDATE
def insert_row_snowflake(new_fruit):
  with my_cnx.cursor() as my_cur:
      my_cur.execute("insert into fruit_load_list(FRUIT_NAME) values ('"+new_fruit.lower()+"')")
      message = "Fruit added!"
      return message

def remove_row_snowflake(remove_fruit):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("delete from fruit_load_list where FRUIT_NAME = ('"+remove_fruit+"')")
    return "Data removed!"

def update_row_snowflake(update_fruit, old_fruit):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("update fruit_load_list set FRUIT_NAME = ('"+update_fruit+"') WHERE FRUIT_NAME = ('"+old_fruit+"'")
    return "Data updated!"

# -- ADD
streamlit.header("Would you like to add a fruit?")
add_fruit = streamlit.text_input('Add a fruit')
if streamlit.button('Click to add data'):
  if not add_fruit:
    streamlit.text("Please add a fruit")
  else:
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    my_data_rows = get_fruit_load_list()
    my_cnx.close()
    info = pandas.DataFrame(my_data_rows)
    if add_fruit.lower() not in info.values:
      my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
      back_from_function = insert_row_snowflake(add_fruit)
      streamlit.text(back_from_function)
    elif add_fruit.lower() in info.values:
      streamlit.text("That fruit is already on the list")

  
# -- REMOVE 
streamlit.header("Would you like to remove a fruit?")
try:
  fruit_box = streamlit.text_input('Specify the fruit')
  if not fruit_box:
    streamlit.text("Please select a fruit from the list")
  else:
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    my_data_rows = get_fruit_load_list()
    my_cnx.close()
    info = pandas.DataFrame(my_data_rows)
    if fruit_box in info.values:
      my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
      back_from_function = remove_row_snowflake(fruit_box)
      streamlit.text(back_from_function)
    else:
      streamlit.text('Please enter a valid fruit')
except URLError as e:
  streamlit.error()

# -- UPDATE
streamlit.header("Would you like to update a fruit?")
old_fruit = streamlit.text_input('Which fruit to update?')
new_fruit = streamlit.text_input('Write the update')
if streamlit.button('Click to update data'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  back_from_function = update_row_snowflake(new_fruit, old_fruit)
  streamlit.text(back_from_function)

## STOP!!
streamlit.stop()
