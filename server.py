from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask, render_template, request, redirect, Markup, session
from wiki_linkify import wiki_linkify
import pg, datetime, markdown
import os
tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask("wiki", template_folder=tmp_dir)

db = pg.DB(
    dbname=os.environ.get('PG_DBNAME'),
    host=os.environ.get('PG_HOST'),
    user=os.environ.get('PG_USERNAME'),
    passwd=os.environ.get('PG_PASSWORD')
)
db.debug = True

app.secret_key = "whatever"

@app.route("/")
def home_page():
    return render_template(
    "homepage.html"
    )

@app.route("/<page_name>")
def place_holder(page_name):
    query = db.query("select * from page where title = $1", page_name).namedresult()
    if len(query) == 0:
        return render_template(
            "placeholderpage.html",
            page_name = page_name,
            query=query
        )
    else:
        page_content = query[0].page_content
        wiki_linkified_content = wiki_linkify(page_content)
        print page_content
        return render_template(
            "placeholderpage.html",
            page_name = page_name,
            query=query[0],
            page_content = Markup(markdown.markdown(wiki_linkified_content))
        )

@app.route("/<page_name>/edit")
def edit_page(page_name):
    query = db.query("select * from page where title = $1", page_name).namedresult()
    if len(query) == 0:
        return render_template(
            "edit.html",
            page_name=page_name,
            query=query
        )
    else:
        return render_template(
            "edit.html",
            page_name=page_name,
            query=query[0]
        )

@app.route("/<page_name>/save", methods=["POST"])
def save_content(page_name):
    id = request.form.get("id")
    page_content = request.form.get("page_content")
    author_name = request.form.get("author_name")
    last_mod_date = request.form.get("last_mod_date")
    action = request.form.get("submit_button")
    if action == "update":
        db.update(
            "page", {
                "id": id,
                "page_content": page_content,
                "author_name": author_name,
                "last_mod_date": last_mod_date,
            }
        )
    elif action == "create":
        db.insert (
            "page",
            title=page_name,
            page_content=page_content,
            author_name=author_name
        )
    else:
        pass
    return redirect("/%s" % page_name)

@app.route("/AllPages")
def all_pages():
    query = db.query("select title from page order by title;").namedresult()
    return render_template(
        "allpages.html",
        query=query
    )

@app.route("/search")
def search_pages():
    search = request.args.get("search")
    page = db.query("select title from page where title = $1", search).namedresult()
    if len(page) == 0:
        return redirect("/%s" % search)
    else:
        return render_template(
            "search.html",
            search=search,
            page=page
        )

@app.route("/login")
def login_user():
    user_name = request.args.get("user_name")
    password = request.args.get("password")
    query = db.query("select * from users where user_name = $1 and password = $2", user_name, password).namedresult()
    if len(query) == 0:
        return render_template(
            "login.html"
        )
    else:
        user = query[0]
        if user.password == password:
            session['username'] = user.user_name
            return redirect("/")
        else:
            return render_template(
                "login.html"
            )

@app.route("/signup")
def signup_user():
    user_name = request.args.get("user_name")
    password = request.args.get("password")
    query = db.query("select * from users where user_name = $1 and password = $2", user_name, password).namedresult()
    if len(query) == 0:
        print user_name
        print password
        return render_template(
            "login.html"
        )
    else:
        user = query[0]
        if user.name == user_name and user.password == password:
            session['username'] = user.user_name
            return redirect("/")
        else:
            print "sorry, that wasn't there"
            return render_template(
                "login.html"
            )


@app.route("/logout")
def logout_user():
    del session['username']
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
