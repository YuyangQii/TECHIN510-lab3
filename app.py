import os
import datetime
from dataclasses import dataclass

import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Prompt:
    title: str
    prompt: str
    is_favorite: bool
    id: int = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None

def setup_database():
    con = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prompts (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            is_favorite BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    con.commit()
    return con, cur

def prompt_form(prompt=None):
    unique_key = f"prompt_form_{prompt.id if prompt and prompt.id else 'new'}"
    with st.form(key=unique_key, clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title if prompt else "")
        prompt_content = st.text_area("Prompt Content", height=200, value=prompt.prompt if prompt else "")
        is_favorite = st.checkbox("Favorite", value=prompt.is_favorite if prompt else False)
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not title or not prompt_content:
                st.error('Please fill in both the title and prompt content.')
                return None
            return Prompt(title, prompt_content, is_favorite, prompt.id if prompt else None)

def display_prompts(cur, con):
    search_query = st.text_input("Search Prompts")
    sort_order = st.selectbox("Sort by", ["Newest", "Oldest", "Favorites First"])
    order_query = "created_at DESC"
    if sort_order == "Oldest":
        order_query = "created_at ASC"
    elif sort_order == "Favorites First":
        order_query = "is_favorite DESC, created_at DESC"

    cur.execute(f"SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY {order_query}", ('%' + search_query + '%', '%' + search_query + '%',))
    prompts = cur.fetchall()
    for p in prompts:
        with st.expander(f"{p[1]} (Created: {p[5].strftime('%Y-%m-%d %H:%M:%S')})"):
            st.code(p[2])
            if st.button("Edit", key=f"edit_{p[0]}"):
                prompt = Prompt(p[1], p[2], p[3], p[0])
                prompt_details = prompt_form(prompt)
                if prompt_details:
                    edit_prompt(prompt_details, cur, con)
            if st.button("Delete", key=f"delete_{p[0]}"):
                cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
                con.commit()
            st.checkbox("Favorite", value=p[3], key=f"fav_{p[0]}", on_change=toggle_favorite, args=(p[0], cur, con))
            if st.button("Render as Template", key=f"template_{p[0]}"):
                render_prompt_as_template(p[0], cur)

def toggle_favorite(prompt_id, cur, con):
    cur.execute("UPDATE prompts SET is_favorite = NOT is_favorite WHERE id = %s", (prompt_id,))
    con.commit()

def edit_prompt(prompt, cur, con):
    cur.execute("UPDATE prompts SET title = %s, prompt = %s, is_favorite = %s WHERE id = %s",
                (prompt.title, prompt.prompt, prompt.is_favorite, prompt.id))
    con.commit()
    st.success('Prompt updated successfully!')

def render_prompt_as_template(prompt_id, cur):
    cur.execute("SELECT * FROM prompts WHERE id = %s", (prompt_id,))
    prompt_data = cur.fetchone()
    if prompt_data:
        formatted_template = f"Title: {prompt_data[1]}\n---\nContent: {prompt_data[2]}"
        st.text_area("Copy and paste this template into ChatGPT:", value=formatted_template, height=250, key=f"template_area_{prompt_id}")

con, cur = setup_database()
st.title('PromptBase')
prompt_details = prompt_form()
if prompt_details:
    if prompt_details.id is None:
        cur.execute("INSERT INTO prompts (title, prompt, is_favorite) VALUES (%s, %s, %s) RETURNING id",
                    (prompt_details.title, prompt_details.prompt, prompt_details.is_favorite))
        con.commit()
        st.success('Prompt added successfully!')
    else:
        edit_prompt(prompt_details, cur, con)
display_prompts(cur, con)
