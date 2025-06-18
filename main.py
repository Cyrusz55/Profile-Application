from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = "your secret key"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "geekprofile"

mysql = MySQL(app)


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = % s \ and password = % s",
            (
                username,
                password,
            ),
        )
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            msg = "Logged in successfully !"
            return render_template("index.html", msg=msg)
        else:
            msg = "Incorrect username / password !"
    return render_template("login.html", msg=msg)


@app.route("/display")
def display():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (session["id"],))
        account = cursor.fetchone()
        return render_template("display.html", account=account)
    return redirect(url_for("login"))


@app.route("/update", methods=["GET", "POST"])
def update():
    msg = ""
    if "loggedin" in session:
        if (
            request.method == "POST"
            and "username" in request.form
            and "password" in request.form
            and "email" in request.form
            and "country" in request.form
            and "postalcode" in request.form
            and "organisation" in request.form
        ):
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]
            organisation = request.form["organisation"]
            address = request.form["address"]
            city = request.form["city"]
            state = request.form["state"]
            country = request.form["country"]
            postalcode = request.form["postalcode"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM account WHERE username = % s", (username,))
            account = cursor.fetchone()
            if account:
                msg = "Account already exists !"
            elif not re.match(r"[^@] + @[^@] + \.[^@] +", email):
                msg = "invalid email address !"
            elif not re.match(r"[A-Za-z0-9] + ", username):
                msg = "name must contain only characters and numbers!"
            else:
                cursor.execute(
                    "UPDATE accounts SET username =% s, \ country =% s, postalcode = % s WHERE id =% s",
                    (
                        username,
                        password,
                        email,
                        organisation,
                        address,
                        city,
                        state,
                        country,
                        postalcode,
                        (session["id"],),
                    ),
                )
