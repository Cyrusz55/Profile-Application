from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY") or "your-dev-secret-key"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Cyrus0792641275"
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

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM accounts WHERE username = %s AND password = %s",
                (username, password),
            )
            account = cursor.fetchone()
            cursor.close()

            if account:
                session["loggedin"] = True
                session["id"] = account["id"]
                session["username"] = account["username"]
                msg = "Logged in successfully!"
                return render_template("index.html", msg=msg)
            else:
                msg = "Incorrect username / password!"

        except Exception as e:
            msg = f"Database error: {str(e)}"
            print(f"Login error: {e}")

    return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""

    # Debug: Print all form data
    if request.method == "POST":
        print(f"Form data received: {dict(request.form)}")

    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
        and "address" in request.form
        and "city" in request.form
        and "country" in request.form
        and "postalcode" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        organisation = request.form.get("organisation", "")
        address = request.form["address"]
        city = request.form["city"]
        state = request.form.get("state", "")
        country = request.form["country"]
        postalcode = request.form["postalcode"]

        print(f"Processing registration for user: {username}")

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Check if user already exists
            cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
            account = cursor.fetchone()
            print(f"Existing account check: {account}")

            if account:
                msg = "Account already exists!"
                print("Registration failed: Account already exists")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                msg = "Invalid email address!"
                print(f"Registration failed: Invalid email: {email}")
            elif not re.match(r"[A-Za-z0-9]+", username):
                msg = "Username must contain only characters and numbers!"
                print(f"Registration failed: Invalid username: {username}")
            else:
                print("All validations passed, attempting to insert...")

                # Insert new account
                cursor.execute(
                    "INSERT INTO accounts (username, password, email, organisation, address, city, state, country, postalcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
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
                    ),
                )

                print(f"Insert executed, affected rows: {cursor.rowcount}")
                mysql.connection.commit()
                print("Transaction committed successfully")

                msg = "You have successfully registered!"
                cursor.close()
                return redirect(url_for("login"))

            cursor.close()

        except Exception as e:
            mysql.connection.rollback()
            msg = f"Registration failed: {str(e)}"
            print(f"Database error during registration: {e}")
            import traceback

            traceback.print_exc()

    elif request.method == "POST":
        msg = "Please fill out the form!"
        print("Registration failed: Missing form fields")
        print(
            f"Required fields check - username: {'username' in request.form}, password: {'password' in request.form}, email: {'email' in request.form}, address: {'address' in request.form}, city: {'city' in request.form}, country: {'country' in request.form}, postalcode: {'postalcode' in request.form}"
        )

    return render_template("register.html", msg=msg)


@app.route("/index")
def index():
    if "loggedin" in session:
        return render_template("index.html")
    return redirect(url_for("login"))


@app.route("/display")
def display():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE id = %s", (session["id"],))
        account = cursor.fetchone()
        cursor.close()
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
            state = request.form.get("state", "")
            country = request.form["country"]
            postalcode = request.form["postalcode"]

            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                # Fixed: Use 'accounts' consistently and proper spacing
                cursor.execute(
                    "SELECT * FROM accounts WHERE username = %s AND id != %s",
                    (username, session["id"]),
                )
                account = cursor.fetchone()

                if account:
                    msg = "Account already exists!"
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    msg = "Invalid email address!"
                elif not re.match(r"[A-Za-z0-9]+", username):
                    msg = "Username must contain only characters and numbers!"
                else:
                    # Fixed: Use 'accounts' and proper spacing
                    cursor.execute(
                        "UPDATE accounts SET username=%s, password=%s, email=%s, organisation=%s, address=%s, city=%s, state=%s, country=%s, postalcode=%s WHERE id=%s",
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
                            session["id"],
                        ),
                    )
                    mysql.connection.commit()
                    msg = "You have successfully updated!"

                cursor.close()

            except Exception as e:
                mysql.connection.rollback()
                msg = f"Update failed: {str(e)}"
                print(f"Update error: {e}")

        elif request.method == "POST":
            msg = "Please fill out the form!"

        return render_template("update.html", msg=msg)
    return redirect(url_for("login"))


# Test routes for debugging
@app.route("/test-db")
def test_db():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts LIMIT 5")
        accounts = cursor.fetchall()
        cursor.close()
        return f"Accounts found: {len(accounts)}<br>Data: {accounts}"
    except Exception as e:
        return f"Database error: {str(e)}"


@app.route("/check-tables")
def check_tables():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.execute("DESCRIBE accounts")
        structure = cursor.fetchall()
        cursor.close()
        return f"Tables: {tables}<br><br>Accounts structure: {structure}"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/manual-insert")
def manual_insert():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO accounts (username, password, email, organisation, address, city, state, country, postalcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                "testuser",
                "testpass",
                "test@email.com",
                "testorg",
                "123 Main St",
                "TestCity",
                "TestState",
                "TestCountry",
                "12345",
            ),
        )
        mysql.connection.commit()
        cursor.close()
        return "Manual insert successful! Check /test-db"
    except Exception as e:
        mysql.connection.rollback()
        return f"Manual insert failed: {str(e)}"


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"), debug=True)
