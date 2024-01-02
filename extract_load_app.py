import streamlit
import pandas
import requests #New section to display fruityvice API response
import snowflake.connector
from urllib.error import URLError

streamlit.title("From Streamlit to Snowflake")
streamlit.header("Check out our fruit list!")

#def get_fruityvice_data(this_fruit_choice):
#  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
#  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
#  return fruityvice_normalized

def get_fruit_load_list():
  with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()
    
#streamlit.header("Fruityvice Fruit Advice!")
#try:
#  fruit_choice = streamlit.text_input('What fruit would you like information about?')
#  if not fruit_choice:
#    streamlit.error("Please select a fruit to get information")
#  else:
#    back_from_function = get_fruityvice_data(fruit_choice)
#    streamlit.dataframe(back_from_function)
#except URLError as e:
#  streamlit.error()

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
      return "Fruit added!"

def remove_row_snowflake(remove_fruit):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("delete from fruit_load_list where FRUIT_NAME = ('"+remove_fruit+"')")
    return "Data removed!"

def update_row_snowflake(update_fruit, old_fruit):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("update fruit_load_list set FRUIT_NAME = ('"+update_fruit+"') WHERE FRUIT_NAME = ('"+old_fruit+"')")
    return "Data updated!"

def fruityvice_selected():
  with my_cnx.cursor() as my_cur:
      my_cur.execute("select fruit_name, id, family, orders, genus, calories, fat, sugar, carbohydrates, protein from fruit_load_list join fruityvice_table on lower(name) = fruit_name")
      return my_cur.fetchall()
    

# -- ADD
streamlit.header("Would you like to add a fruit?")
add_fruit = streamlit.text_input('Write a fruit 🍌')
add_fruit = add_fruit.lower()
if not add_fruit:
  streamlit.text("Please add a fruit")
else:
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  info = pandas.DataFrame(my_data_rows)
  if add_fruit not in info.values:
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    back_from_function = insert_row_snowflake(add_fruit)
    streamlit.text(back_from_function)
  elif add_fruit in info.values:
    streamlit.text("That fruit is already on the list")

  
# -- REMOVE 
streamlit.header("Would you like to remove a fruit?")
fruit_box = streamlit.text_input('Specify the fruit 🥝')
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


# -- UPDATE
streamlit.header("Would you like to update a fruit?")
old_fruit = streamlit.text_input('Which fruit to update? 🍇')
new_fruit = streamlit.text_input('Write the change 🥭')
if not old_fruit or not new_fruit:
  streamlit.text("Please check the fields")
else:
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  info = pandas.DataFrame(my_data_rows)
  if old_fruit in info.values:
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    back_from_function = update_row_snowflake(new_fruit, old_fruit)
    streamlit.text(back_from_function)
  else:
    streamlit.text("Please check the fields")

# TABLE WITH ALL THE INFO 
streamlit.header("See detailed information on each fruit")
if streamlit.button('Get info'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  fruit_info = fruityvice_selected()
  my_cnx.close()
  snow_fruit = pandas.DataFrame(fruit_info)
  snow_fruit.columns = ["NAME", "ID", "FAMILY", "ORDER", "GENUS", "CALORIES", "FAT", "SUGAR", "CARBOHYDRATES", "PROTEIN"]
  streamlit.dataframe(snow_fruit)
  
  modify = streamlit.checkbox("Add filters")
  if not modify:
    snow_fruit
  else:
    container = streamlit.container()
    with container:
      filter_columns = streamlit.multiselect("Choose filters", snow_fruit.columns)
      for column in filter_columns:
        left, right = streamlit.columns((1,20))
        if is_categorical_dtype(snow_fruit[column]) or snow_fruit[column].unique() < 10:
          user_input = right.multiselect(
            f"Values for {column}", 
            df[column].unique(),
            default=list(snow_fruit[column].unique()),)
          snow_fruit = snow_fruit[snow_fruit[column].isin(user_input)]
        elif is_numeric_dtype(snow_fruit[column]):
          _min = float(snow_fruit[column].min())
          _max = float(snow_fruit[column].max())
          step = (_max - _min) / 100
          user_input_num = right.slider(
            f"Values for {column}",
            min_value = _min,
            max_value = _max,
            value = (_min, _max),
            step=step,)
          snow_fruit = snow_fruit[snow_fruit[column].between(*user_input_num)]


## STOP!!
streamlit.stop()
