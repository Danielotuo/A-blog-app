import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud


conn = sqlite3.connect('data.db')
cur = conn.cursor()


# Functions
def create_table():
    cur.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,article TEXT,postdate DATE)')


def add_data(author, title, article, postdate):
    cur.execute('INSERT INTO blogtable(author,title,article,postdate) VALUES (?,?,?,?)',
              (author, title, article, postdate))
    conn.commit()


def view_all():
    cur.execute('SELECT * FROM blogtable')
    data = cur.fetchall()
    return data


def view_all_titles():
    cur.execute('SELECT DISTINCT title FROM blogtable')
    data = cur.fetchall()
    return data


def get_blog_by_title(title):
    cur.execute('SELECT * FROM blogtable WHERE title="{}"'.format(title))
    data = cur.fetchall()
    return data


def get_blog_by_author(author):
    cur.execute('SELECT * FROM blogtable WHERE author="{}"'.format(author))
    data = cur.fetchall()
    return data


def delete_data(title):
    cur.execute('DELETE FROM blogtable WHERE title="{}"'.format(title))
    conn.commit()


title_page = """
<div style="background-color:#383838;padding:10px;border-radius:10px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="http://fanaru.com/naruto/image/21647-naruto-naruto.jpg" 
alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
<h6>Author: {}</h6>
<br/>
<br/>
<p style="text-align:justify">{}</p>
</div>
"""
article_page = """
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<h6>Author: {}</h6>
<h6>Post Date: {}</h6>
<img src="http://fanaru.com/naruto/image/21647-naruto-naruto.jpg" alt="Avatar" style="vertical-align:
middle;width: 50px;height: 50px;border-radius: 50%;" >
<br/>
<br/>
<p style="text-align:justify">{}</p>
</div>
"""
head_message_page = """
<div style="background-color:#383838;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="http://fanaru.com/naruto/image/21647-naruto-naruto.jpg" 
alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author: {}</h6>
<h6>Post Date: {}</h6>
</div>
"""
full_message_page = """
<div style="background-color:powderblue;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""


def main():
    """A Simple CRUD  Blog"""

    menu = ["Home", "View Posts", "Add Posts", "Search", "Manage Posts"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.image("post.jpg", use_column_width=True)
        st.subheader('Choose Article from Menu')
        result = view_all()
        
        # Show some details about the articles
        for post in result:
            blog_author = post[0]
            blog_title = post[1]
            blog_article = str(post[2])[0:50]
            blog_post_date = post[3]

            st.markdown(title_page.format(blog_title, blog_author, blog_article, blog_post_date), unsafe_allow_html=True)
    
    # Option to view posts and also select an article to read
    elif choice == "View Posts":
        st.subheader("Articles")

        all_titles = [post[0] for post in view_all_titles()]
        postlist = st.sidebar.selectbox("Select Posts", all_titles)
        post_result = get_blog_by_title(postlist)

        for post in post_result:
            blog_author = post[0]
            blog_title = post[1]
            blog_article = post[2]
            blog_post_date = post[3]
            st.markdown(head_message_page.format(blog_title, blog_author, blog_post_date), unsafe_allow_html=True)
            st.markdown(full_message_page.format(blog_article), unsafe_allow_html=True)

    # Option to add new posts or articles
    elif choice == "Add Posts":
        st.subheader("Add Articles")
        create_table()
        blog_author = st.text_input("Enter Author Name", max_chars=50)
        blog_title = st.text_input("Enter Post Title")
        blog_article = st.text_area("Post", height=500)
        blog_post_date = st.date_input("Date")
        if st.button("Add"):
            add_data(blog_author, blog_title, blog_article, blog_post_date)
            st.success(f"{blog_title} added")
    
    # Option to search for articles
    elif choice == "Search":
        st.subheader("Search Articles")
        search_term = st.text_input('Enter Search Term')
        search_choice = st.radio("Field to Search By", ("title", "author"))
        if st.button("Search"):
            if search_choice == "title":
                article_result = get_blog_by_title(search_term)
            elif search_choice == "author":
                article_result = get_blog_by_author(search_term)

            for post in article_result:
                blog_author = post[0]
                blog_title = post[1]
                blog_article = post[2]
                blog_post_date = post[3]
                st.markdown(head_message_page.format(blog_title, blog_author, blog_post_date), unsafe_allow_html=True)
                st.markdown(full_message_page.format(blog_article), unsafe_allow_html=True)

    # Option to manage the particle like delete, get a word loud and also length of articles
    elif choice == "Manage Posts":
        st.subheader("Manage Articles")

        result = view_all()
        clean_db = pd.DataFrame(result, columns=["Author", "Title", "Articles", "Post Date"])
        st.dataframe(clean_db)

        post_titles = [post[0] for post in view_all_titles()]
        delete_blog_by_title = st.selectbox("Post Title", post_titles)
        new_df = clean_db

        # Delete an article
        if st.button("Delete"):
            delete_data(delete_blog_by_title)
            st.warning(f"{delete_blog_by_title} deleted")

        # GEt length of articles
        if st.checkbox("Metrics"):
            new_df['Length'] = new_df['Articles'].str.len()
            st.dataframe(new_df)
            
            # Generate a pie chart to represent the authors' posts statistics
            st.subheader("Author Stats")
            new_df['Author'].value_counts().plot.pie(autopct="%1.1f%%")
            st.pyplot()

        # Generate a word cloud for all the articles
        if st.checkbox("Word Cloud"):
            st.subheader("Get Word Cloud")
            text = ','.join(new_df['Articles'])
            wordcloud = WordCloud().generate(text)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            st.pyplot()


if __name__ == '__main__':
    main()
