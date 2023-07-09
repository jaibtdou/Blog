from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.keep_trailing_newline = False
blog_data = sqlite3.connect("storage/blogs.db", check_same_thread=False)
blog_cursor = blog_data.cursor()

@app.route('/')
def home():
    return redirect(url_for('index'))

@app.route('/page', defaults={'page': 1}, methods=["GET"])
@app.route('/page/<int:page>', methods=["GET"])
def index(page):
    blogs_per_page = 10

    offset = (page - 1) * blogs_per_page

    blog_cursor.execute(f"SELECT rowid, * FROM blogs ORDER BY time DESC LIMIT {blogs_per_page} OFFSET {offset} ")

    blogs = blog_cursor.fetchall()
    blogs = [{
        'rowid': blog[0],
        'title': blog[1],
        'time': datetime.fromtimestamp(blog[3]).strftime("%d/%m/%Y, %H:%M:%S"),
        'viewcount': blog[4]}
        for blog in blogs]
    return render_template("index.html", blogs=blogs, current_page=page)


@app.route('/read/<int:id>')
def blog(id):
    blog_cursor.execute(f"SELECT * from blogs WHERE rowid = {id}")
    blogs = blog_cursor.fetchall()
    blog_cursor.execute(f"UPDATE blogs SET viewcount = ? WHERE rowid = {id}", (blogs[0][3] + 1, ))
    blog_data.commit()
    if len(blogs) == 0:
        return "404 Not Found"
    
    return render_template("blog.html", blog=blogs[0][1].split('\n'))


if __name__ == '__main__':
    app.run(port=80, debug=1)
