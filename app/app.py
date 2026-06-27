from flask import Flask, request, redirect, render_template_string
import pymysql
import os
import time

app = Flask(__name__)

# ----------------------------
# Database Connection
# ----------------------------

def get_connection():
    while True:
        try:
            return pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB"),
    cursorclass=pymysql.cursors.DictCursor
)
        except Exception as e:
            print("Waiting for MySQL...")
            print(e)
            time.sleep(3)

# ----------------------------
# HTML Template
# ----------------------------

HTML = """
<!DOCTYPE html>
<html>

<head>

<title>Enterprise Migration Project</title>

<style>

body{
font-family:Arial;
background:#f5f5f5;
margin:40px;
}

.container{
max-width:900px;
margin:auto;
background:white;
padding:30px;
border-radius:10px;
box-shadow:0 0 15px rgba(0,0,0,.1);
}

h1{
color:#1d3557;
}

.card{
padding:15px;
background:#eef6ff;
border-left:5px solid #0077cc;
margin-bottom:20px;
}

table{
width:100%;
border-collapse:collapse;
margin-top:20px;
}

th,td{
padding:12px;
border:1px solid #ddd;
text-align:left;
}

th{
background:#0077cc;
color:white;
}

input{
padding:10px;
width:70%;
}

button{
padding:10px 20px;
background:#0077cc;
color:white;
border:none;
cursor:pointer;
}

button:hover{
background:#005fa3;
}

.footer{
margin-top:30px;
font-size:14px;
color:gray;
}

</style>

</head>

<body>

<div class="container">

<h1>Enterprise Migration Project</h1>

<div class="card">

<b>Application Status</b><br>

Application : Running ✅<br>
Database : Connected ✅<br>
Environment : Docker Compose

</div>

<form method="POST" action="/add">

<input
type="text"
name="name"
placeholder="Enter User Name"
required>

<button>Add User</button>

</form>

<h2>Registered Users</h2>

<table>

<tr>

<th>ID</th>
<th>Name</th>

</tr>

{% for user in users %}

<tr>

<td>{{ user.id }}</td>

<td>{{ user.name }}</td>

</tr>

{% endfor %}

</table>

<div class="footer">

Enterprise Migration Demo

WSL → Docker → AWS EC2 → Amazon RDS

</div>

</div>

</body>

</html>

"""

# ----------------------------
# Home
# ----------------------------

@app.route("/")
def home():

    try:

        conn=get_connection()

        cursor=conn.cursor()

        cursor.execute("SELECT * FROM users")

        users=cursor.fetchall()

        conn.close()

        return render_template_string(HTML,users=users)

    except Exception as e:

        return f"<h2>Database Error</h2><pre>{e}</pre>"

# ----------------------------
# Add User
# ----------------------------

@app.route("/add",methods=["POST"])
def add():

    try:

        name=request.form["name"]

        conn=get_connection()

        cursor=conn.cursor()

        cursor.execute(
            "INSERT INTO users(name) VALUES(%s)",
            (name,)
        )

        conn.commit()

        conn.close()

        return redirect("/")

    except Exception as e:

        return f"Error : {e}"

# ----------------------------
# Health Check
# ----------------------------

@app.route("/health")
def health():

    return {

        "status":"healthy",

        "application":"running"

    }

# ----------------------------
# Database Status
# ----------------------------

@app.route("/db-status")
def db_status():

    try:

        conn=get_connection()

        cursor=conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total FROM users")

        total=cursor.fetchone()

        conn.close()

        return {

            "database":"connected",

            "total_users":total["total"]

        }

    except Exception as e:

        return {

            "database":"failed",

            "error":str(e)

        }

# ----------------------------
# Main
# ----------------------------

if __name__=="__main__":

    app.run(

        host="0.0.0.0",

        port=5000

    )