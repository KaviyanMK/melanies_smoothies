import streamlit as st
from snowflake.snowpark.functions import col
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your Smoothie will be:", name_on_order)

session = get_active_session()

fruit_df = session.table("smoothies.public.fruit_options").select("FRUIT_NAME")
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

cnx=st.connection("snowflake")
session=cnx.session()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""
    for Fruit_chosen in ingredients_list:
        ingredients_string += Fruit_chosen + " "

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
