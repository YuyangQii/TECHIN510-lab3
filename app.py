import sqlite3
import psycopg2
import os

import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp

# Connect to our database
DB_CONFIG = os.getenv("DB_TYPE")
if DB_CONFIG == 'PG':
    PG_USER = os.getenv("PG_USER")
    con = psycopg2.connect(f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/todoapp?connect_timeout=10&application_name=todoapp")
else:
    con = sqlite3.connect("todoapp.sqlite", isolation_level=None)
cur = con.cursor()

# Create the table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        is_done BOOLEAN
    )
    """
)

# Define our Form
class Task(BaseModel):
    name: str
    description: str
    is_done: bool

# This function will be called when the check mark is toggled, this is called a callback function
def toggle_is_done(is_done, row):
    cur.execute(
        """
        UPDATE tasks SET is_done = ? WHERE id = ?
        """,
        (is_done, row[0]),
    )

def main():
    st.title("Todo App")

    # Create a Form using the streamlit-pydantic package, just pass it the Task Class
    data = sp.pydantic_form(key="task_form", model=Task)
    if data:
        cur.execute(
            """
            INSERT INTO tasks (name, description, is_done) VALUES (?, ?, ?)
            """,
            (data.name, data.description, data.is_done),
        )

    data = cur.execute(
        """
        SELECT * FROM tasks
        """
    ).fetchall()

    # HINT: how to implement a Edit button?
    # if st.query_params.get('id') == "123":
    #     st.write("Hello 123")
    #     st.markdown(
    #         f'<a target="_self" href="/" style="display: inline-block; padding: 6px 10px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 12px; border-radius: 4px;">Back</a>',
    #         unsafe_allow_html=True,
    #     )
    #     return

    cols = st.columns(3)
    cols[0].write("Done?")
    cols[1].write("Name")
    cols[2].write("Description")
    for row in data:
        cols = st.columns(3)
        cols[0].checkbox('is_done', row[3], label_visibility='hidden', key=row[0], on_change=toggle_is_done, args=(not row[3], row))
        cols[1].write(row[1])
        cols[2].write(row[2])
        # cols[2].markdown(
        #     f'<a target="_self" href="/?id=123" style="display: inline-block; padding: 6px 10px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 12px; border-radius: 4px;">Action Text on Button</a>',
        #     unsafe_allow_html=True,
        # )

main()