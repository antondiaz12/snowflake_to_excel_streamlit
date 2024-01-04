import streamlit
import pandas
import io
import requests #New section to display fruityvice API response
import snowflake.connector
from urllib.error import URLError
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from openpyxl import Workbook
from io import BytesIO



# ------------- HEADERS -------------
streamlit.title("From Snowflake to Streamlit")
streamlit.header("Check out our fruit list!")

# ----------- FUNCTIONS ------------
def get_fruit_load_list():
  with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()

if streamlit.button('🥑 Get Fruit List 🥑'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  table = pandas.DataFrame(my_data_rows)
  table.columns = ["Fruits"]
  streamlit.dataframe(table)


def insert_row_snowflake(new_fruit):
  with my_cnx.cursor() as my_cur:
      my_cur.execute("insert into fruit_load_list(FRUIT_NAME) values ('"+new_fruit+"')")
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
      my_cur.execute("select name, id, family, orders, genus, calories, fat, sugar, carbohydrates, protein from fruit_load_list join fruityvice_table on lower(name) = fruit_name")
      return my_cur.fetchall()

# ----------- ACTION: ADD -----------
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

# ----------- ACTION: REMOVE ----------
streamlit.header("Would you like to remove a fruit?")
fruit_box = streamlit.text_input('Specify the fruit 🥝')
fruit_box = fruit_box.lower()
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

# ----------- ACTION: UPDATE -----------
streamlit.header("Would you like to update a fruit?")
old_fruit = streamlit.text_input('Which fruit to update? 🍇')
new_fruit = streamlit.text_input('Type the change 🥭')
old_fruit = old_fruit.lower()
new_fruit = new_fruit.lower()
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

# ----------- ACTION: FILTER ----------
streamlit.header("See detailed information of each fruit")
my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
fruit_info = fruityvice_selected()
my_cnx.close()
snow_fruit = pandas.DataFrame(fruit_info)
snow_fruit.columns = ["NAME", "ID", "FAMILY", "ORDER", "GENUS", "CALORIES", "FAT", "SUGAR", "CARBOHYDRATES", "PROTEIN"]
#show_table = streamlit.dataframe(snow_fruit)

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

# -------- ACTION: EXPORT TO EXCEL ----------
workbook = Workbook()

with NamedTemporaryFile() as tmp:
     workbook.save(snow_fruit.name)
     data = BytesIO(snow_fruit.read())
if streamlit.download_button(
        label="Download",
        data=data,
        file_name='exp_fruit_data.xlsx',
        mime="application/vnd.ms-excel"):
    streamlit.write("thank you for downloading!")

#@streamlit.experimental_memo(ttl=60, persist="disk")
#def create_xlsx(snow_fruit):
#    buffer = io.BytesIO()
#    with pandas.ExcelWriter(buffer) as writer:
#        snow_fruit.to_excel(writer)
#    return buffer

#if streamlit.download_button(
#        label="Download",
#        data=create_xlsx(snow_fruit) ,
#        file_name='exp_fruit_data.xlsx',
#        mime="application/vnd.ms-excel"):
    
#    st.write("thank you for downloading!")

#if st.button("Clear All"):
#    st.experimental_memo.clear()

# -------------- ACTION: STOP  --------------
streamlit.stop()


# ---------------- DRAFT CODE -------------
#def get_fruityvice_data(this_fruit_choice):
#  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
#  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
#  return fruityvice_normalized
    
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

