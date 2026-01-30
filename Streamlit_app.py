import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()

name_on_order = st.text_input("Name on Smoothie:")
st.write("The Name on your Smoothie will be:", name_on_order)

fruit_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

fruit_data = fruit_df.collect()

fruit_names = [row["FRUIT_NAME"] for row in fruit_data]
search_lookup = {
    row["FRUIT_NAME"]: row["SEARCH_ON"] for row in fruit_data
}

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        search_term = search_lookup.get(fruit_chosen)

        st.subheader(f"{fruit_chosen} Nutrition Information")

        if search_term:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_term}"
            )

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning(f"No nutrition data found for {fruit_chosen}")
        else:
            st.warning(f"No SEARCH_ON value for {fruit_chosen}")

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
