import streamlit
import pandas
import io
from snowflake.connector import connect
from pandas.api.types import (
    is_categorical_dtype,
    is_numeric_dtype)
 
 
# ------------- HEADERS -------------
streamlit.title("From Snowflake to Streamlit")
streamlit.header("Check out our fruit list!")

#------------ SNOWFLAKE CONNECTION
def snow_connection(query):
  my_cnx = connect(
    user = "marucarrillog",
    password = "Boehringer1.",
    account = "XQGYYIV-SA20142",
    warehouse = "compute_wh" ,
    database = "pc_rivery_db" ,
    schema = "public",
    role = "accountadmin")
  with my_cnx.cursor() as my_cur:
    my_cur.execute(query)
    return my_cur.fetchall()


if streamlit.button('🍉 Get Fruit List 🍉'):
  my_data_rows = snow_connection("select * from fruit_load_list")
  table = pandas.DataFrame(my_data_rows)
  table.columns = ["Fruits"]
  streamlit.dataframe(table)

# ----- ACTIONS:ADD/REMOVE/UPDATE 
# 1. Connect to snowflake
# 2. Add, remove or update the data 
# 4. Close the connection

# ACTION - ADD VALUES
streamlit.header("Would you like to add a fruit?")
add_fruit = streamlit.text_input('Write a fruit 🍌').lower()
if not add_fruit:
  streamlit.text("Please add a fruit")
else:
  my_data_rows = snow_connection("select * from fruit_load_list")
  if add_fruit not in pandas.DataFrame(my_data_rows).values:
    query = "insert into fruit_load_list(FRUIT_NAME) values ('"+add_fruit+"')"
    my_data_rows = snow_connection(query)
    streamlit.text("Fruit added!")
  else:
    streamlit.text("That fruit is already on the list")

# ACTION - REMOVE VALUES
streamlit.header("Would you like to remove a fruit?")
remove_data = streamlit.text_input('Specify the fruit 🥝').lower()
if not remove_data:
  streamlit.text("Please select a fruit from the list")
else:
  my_data_rows = snow_connection("select * from fruit_load_list")
  if remove_data in pandas.DataFrame(my_data_rows).values:
    query = "delete from fruit_load_list where FRUIT_NAME = ('"+remove_data+"')"
    my_data_rows = snow_connection(query)
    streamlit.text("Data removed!")
  else:
    streamlit.text('Please enter a valid fruit')

# ACTION - UPDATE VALUES
streamlit.header("Would you like to update a fruit?")
old_fruit = streamlit.text_input('Which fruit to update? 🍇').lower()
new_fruit = streamlit.text_input('Type the change 🥭').lower()
if not old_fruit or not new_fruit:
  streamlit.text("Please check the fields")
else:
  my_data_rows = snow_connection("select * from fruit_load_list")
  if old_fruit in pandas.DataFrame(my_data_rows).values:
    query = "update fruit_load_list set FRUIT_NAME = ('"+new_fruit+"') WHERE FRUIT_NAME = ('"+old_fruit+"')"
    my_data_rows = snow_connection(query)
    streamlit.text("Data updated!")
  else:
    streamlit.text("Please check the fields")

# ----- FILTER
# Categorical and numerical data are filtered differently 
streamlit.header("See detailed information of each fruit")
query = "select name, id, family, orders, genus, calories, fat, sugar, carbohydrates, protein from fruit_load_list join fruityvice_table on lower(name) = fruit_name"
fruit_info = snow_connection(query)
snow_fruit = pandas.DataFrame(fruit_info)
snow_fruit.columns = ["NAME", "ID", "FAMILY", "ORDER", "GENUS", "CALORIES", "FAT", "SUGAR", "CARBOHYDRATES", "PROTEIN"]
modify = streamlit.checkbox("Apply filters to obtain the desired table")
if not modify:
  snow_fruit
else:
  container = streamlit.container()
  with container:
    filter_columns = streamlit.multiselect("Choose the columns you want to filter", snow_fruit.columns)
    for column in filter_columns:
      left, right = streamlit.columns((1,20))
      if is_categorical_dtype(snow_fruit[column]) or snow_fruit[column].nunique() < 10:
        user_input = right.multiselect(
          f"Values for {column}", 
          snow_fruit[column].unique(),
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
    snow_fruit

# ----- EXPORT TO EXCEL 
@streamlit.cache_data()
def create_xlsx(snow_fruit):
    buffer = io.BytesIO()
    with pandas.ExcelWriter(buffer) as writer:
        snow_fruit.to_excel(writer)
    return buffer
 
if streamlit.download_button(
        label="Download ✅",
        data=create_xlsx(snow_fruit) ,
        file_name='exp_fruit_data.xlsx',
        mime="application/vnd.ms-excel"):
    streamlit.write("Thank you for downloading!")

# ----- STOP STREAMLIT CONNECTION
streamlit.stop()
