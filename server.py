from flask import *
from flask_mysqldb import *
app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '#LearnDBMS55'
app.config['MYSQL_DB'] = 'mydb2'
mysql = MySQL(app)

@app.route("/home")
def home():
    return render_template("index2.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/customer_query", methods=['POST'])
def customer_query():
    name=request.form['name']
    email=request.form['email']
    message=request.form['message']

    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO customer_query VALUES (%s,%s,%s)", (name, email, message))
    dbconn.commit()
    cursor.close()

    return ("Your query has been submitted successfully. You will hear from us soon!")

@app.route('/products/<int:product_id>', methods=['GET'])
def products(product_id):  
    print(product_id)
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("Select * from artwork where id = %s", (product_id,))
    res = cursor.fetchone()
    print(res)
    return render_template('products.html',res = res)

@app.route("/cart", methods=['POST'])
def cart():
    product_id = request.form.get('product_id')
    print(product_id)
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("Select * from artwork where id = %s", (product_id,))
    res = cursor.fetchone()
    print(res)
    return render_template("cart.html", res =res)

@app.route("/registration")
def registration():
    dbconn=mysql.connection
    cursor1=dbconn.cursor()
    cursor1.execute("SELECT event_name FROM mydb2.events WHERE event_date BETWEEN CURRENT_DATE() AND '2025-01-30'")
    results1=cursor1.fetchall()
    cursor1.close()
    return render_template("registration.html", results1=results1)

@app.route("/reg_confirm", methods=['POST'])
def reg_confirm():
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['email']
    password=request.form['password']
    cpassword=request.form['cpassword']
    pno=request.form['pno']
    event=request.form['event']

    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO mydb2.registered_users(fname, lname, email, password, c_password, phone, event) VALUES (%s,%s,%s,%s,%s,%s,%s)", (fname,lname,email,password,cpassword,pno,event,))
    dbconn.commit()
    cursor.close()
    
    return render_template("reg_confirm.html", event=event)

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/artwork")
def artwork():
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("Select * from artwork")
    res = cursor.fetchall()
    
    return render_template("artwork.html", res = res)

@app.route("/events")
def events():
    dbconn=mysql.connection
    cursor1=dbconn.cursor()
    cursor1.execute("SELECT * FROM mydb2.events WHERE event_date BETWEEN CURRENT_DATE() AND '2025-01-30'")
    results1=cursor1.fetchall()
    cursor1.close()
    cursor2=dbconn.cursor()
    cursor2.execute("SELECT * FROM mydb2.events WHERE event_date>'2025-01-30'")
    results2=cursor2.fetchall()
    cursor2.close()
    return render_template("events.html", results1=results1, results2=results2)

@app.route("/artists")
def artists():
    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("SELECT * FROM mydb2.artists")
    results=cursor.fetchall()
    cursor.close()
    return render_template("artists.html", results=results)


@app.route('/filter_artwork', methods=['GET'])
def filter_artwork():
    try:
        cursor = mysql.connection.cursor()
        filter_category = request.args.get('category')
        #print(filter_category)
        cursor.execute("SELECT * FROM mydb2.artwork WHERE category = %s", (filter_category,))
        res = cursor.fetchall()
        print(res)
        cursor.close()
        return render_template('filter_artwork.html', res=res)
    except Exception as e:
        return render_template("artwork.html")


@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

app.run(debug=True, port=5002)
