from flask import *
from flask_mysqldb import *
from datetime import datetime

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '#LearnDBMS55'
app.config['MYSQL_DB'] = 'mydb2'
mysql = MySQL(app)

# For user session management
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route("/home")
def home():
    return render_template("index2.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/createsession", methods = ['post'])
def createsession():
    email = request.form['email']
    password = request.form['password']

    dbconn = mysql.connection
    cursor1 = dbconn.cursor()
    cursor2 = dbconn.cursor()

    # Cursor to check if user is admin
    cursor1.execute("select * from admin where email = %s and password = %s", (email, password,))
    user1 = cursor1.fetchone()
    
    # Cursor to check if user is registered_user
    cursor2.execute("select * from registered_users where email = %s", (email,))
    user2 = cursor2.fetchone()

    if user1:                  # Admin can access the admin_dashboard
        session['is_admin'] = True
        session['email'] = user1[0]
        return redirect("/admin_dashboard")
    elif user2:                # Registered_user can add to cart
        session['is_user'] = True
        session['email'] = user2[3]
        session['user_id']=user2[0]
        print("THis is the email that is logged in: ", session['email'])
        print(session['is_user'])
        return redirect('/home')
    else:
        return redirect("/login")

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
    status = 'Pending'
    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO customer_query VALUES (%s,%s,%s,%s)", (name, email, message, status))
    dbconn.commit()
    cursor.close()
    return ("Your query has been submitted successfully. You will hear from us soon!")


@app.route("/main_registration")
def main_registration():
    session['is_admin'] = False
    session['is_user'] = False
    return render_template("main_registration.html")

@app.route("/reg_confirm", methods=['POST'])
def reg_confirm():
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['email']
    password=request.form['password']
    cpassword=request.form['cpassword']
    pno=request.form['pno']
    address=request.form['address']

    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO registered_users(fname, lname, email, password, c_password, phone, address) VALUES (%s,%s,%s,%s,%s,%s,%s)", (fname,lname,email,password,cpassword,pno,address))
    dbconn.commit()
    cursor.close()
    
    return render_template("reg_confirm.html")


@app.route("/event_registration")
def event_registration():
    dbconn=mysql.connection
    cursor1=dbconn.cursor()
    cursor1.execute("SELECT event_name FROM events WHERE event_date BETWEEN CURRENT_DATE() AND '2025-01-30'")
    results1=cursor1.fetchall()
    cursor1.close()
    return render_template("event_registration.html", results1=results1)


@app.route("/event_confirm", methods=['POST'])
def event_confirm():
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['email']
    pno=request.form['pno']
    event=request.form['event']

    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO event_users(fname, lname, email, phone, event) VALUES (%s,%s,%s,%s,%s)", (fname,lname,email,pno,event,))
    dbconn.commit()
    cursor.close()
    
    return render_template("event_confirm.html", event=event)

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
    cursor1.execute("SELECT * FROM events WHERE event_date BETWEEN CURRENT_DATE() AND '2025-01-30' LIMIT 3")
    results1=cursor1.fetchall()
    cursor1.close()
    cursor2=dbconn.cursor()
    cursor2.execute("SELECT * FROM events WHERE event_date>'2025-01-30' LIMIT 3")
    results2=cursor2.fetchall()
    cursor2.close()
    return render_template("events.html", results1=results1, results2=results2)

@app.route("/artists")
def artists():
    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("SELECT * FROM artists")
    results=cursor.fetchall()
    cursor.close()
    return render_template("artists.html", results=results)


@app.route('/filter_artwork', methods=['GET'])
def filter_artwork():
    try:
        cursor = mysql.connection.cursor()
        filter_category = request.args.get('category')
        cursor.execute("SELECT * FROM mydb2.artwork WHERE category = %s", (filter_category,))
        res = cursor.fetchall()
        print(res)
        cursor.close()
        return render_template('filter_artwork.html', res=res)
    except Exception as e:
        return render_template("artwork.html")

@app.route('/products/<int:product_id>', methods=['GET'])
def products(product_id):  
    print(product_id)
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("Select * from artwork where id = %s", (product_id,))
    res = cursor.fetchone()
    print(res)
    return render_template('products.html',res = res)

@app.route("/cart", methods=['POST','GET'])
def cart():
    if 'is_user' in session and session['is_user']:
        product_id = request.form.get('product_id')
        print(product_id)
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("Select * from artwork where id = %s", (product_id,))
        res = cursor.fetchone()
        print(res)
        return render_template("cart.html", res = res)
    else:
        return redirect("/login")
    
@app.route("/checkout", methods = ['post'])
def checkout():
    if 'is_user' in session and session['is_user']:
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        order_date = datetime.now().strftime('%Y-%m-%d')
        status = 'processing'
        user_email = session['email']

        # Insert the order details into the 'orders' table
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        # cursor.execute("insert into orders (order_date, product_name, price, user_email, status) values (%s, %s, %s, %s, %s,)", (order_date, product_name, price, user_email, status,) )
        cursor.execute("Insert into orders (order_date, product_name, price , status, user_email) values (%s, %s, %s, %s, %s)", (order_date, product_name, price, status, user_email,))
        dbconn.commit()
        cursor.close()
        return render_template("checkout.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if session['is_admin']:
        return render_template("admin_dashboard.html")
    else:
        return redirect("/login")

# @app.route("/view_orders")
# def view_orders():
#     cursor = mysql.connection.cursor()
#     cursor.execute("SELECT * FROM orders")
#     res = cursor.fetchall()
#     return render_template("view_orders.html", res = res)

@app.route("/view_orders", methods=['GET'])
def view_orders():
    # Get the filter parameter from the URL (if any)
    status_filter = request.args.get('status', '')

    # Build the query depending on whether a filter is applied
    query = "SELECT * FROM orders"
    params = ()

    if status_filter:
        query += " WHERE status = %s"
        params = (status_filter,)

    # Execute the query with or without filter
    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    res = cursor.fetchall()

    return render_template("view_orders.html", res=res)

@app.route("/confirm_orders", methods=["POST"])
def confirm_orders():
    selected_orders = request.form.getlist("selected_orders")  # Get list of selected order IDs

    if selected_orders:
        cursor = mysql.connection.cursor()
        
        # Update status of selected orders to 'Confirmed'
        cursor.execute("""
            UPDATE orders
            SET status = 'Confirmed'
            WHERE id IN (%s)
        """ % ",".join(["%s"] * len(selected_orders)), tuple(selected_orders))
        
        mysql.connection.commit()
        cursor.close()
        
        flash("Selected orders have been confirmed!", "success")
        return redirect("/view_orders")
    
    flash("No orders selected.", "warning")
    return redirect("/view_orders")


@app.route("/add_event")
def add_event():
    if session['is_admin']:
        return render_template("add_event.html")
    else:
        return redirect("/login")

@app.route("/adding_events", methods = ['post'])
def adding_events():
    event_name = request.form['name']
    event_date = request.form['date']
    description = request.form['description']
    event_img = request.files['event_img']

    event_filename = event_img.filename
    event_poster_path = "static/images/"+event_filename
    event_img.save(event_poster_path)
    
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("Insert into events (event_name, event_date, description, event_img) values (%s, %s, %s, %s)", (event_name, event_date, description, event_poster_path,))
    dbconn.commit()
    cursor.close()
    return render_template("admin_dashboard.html",message = "Successfully Added the Event")


@app.route("/modify_event", methods=["GET", "POST"])
def modify_event():
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    
    # Fetch all events
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    # Handle form submission for updating events
    if request.method == "POST":
        # Assuming the form contains data to modify event
        event_id = request.form["event_id"]
        new_name = request.form["event_name"]
        new_date = request.form["event_date"]
        # Update event in database
        cursor.execute(
            "UPDATE events SET event_name = %s, event_date = %s WHERE event_id = %s",
            (new_name, new_date, event_id)
        )
        dbconn.commit()

        # After updating, fetch the updated events
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()

    return render_template("modify_event.html", events=events)


@app.route("/logout")
def logout():
    if 'is_admin' in session and session['is_admin']:
        session.pop('email',None)
        session.pop('is_admin',None)
    elif 'is_user' in session and session['is_user']:
        session.pop('email',None)
        session.pop('is_user',None)
    else:
        return redirect("/home")
    return redirect("/home")

@app.route("/order_confirmation")
def order_confirmation():
    user_id=session['user_id']
    dbconn=mysql.connection
    cursor1=dbconn.cursor()
    cursor1.execute("SELECT user_id, user_name FROM cart WHERE user_id=%s",(user_id,))
    results1=cursor1.fetchone()
    cursor1.close()
    cursor2=dbconn.cursor()
    cursor2.execute("SELECT product_id, product_name, price FROM cart WHERE user_id=%s",(user_id,))
    results2=cursor2.fetchall()
    cursor2.close()
    cursor3=dbconn.cursor()
    cursor3.execute("SELECT phone, email, address FROM registered_users WHERE user_id=%s",(user_id,))
    results3=cursor3.fetchone()
    cursor3.close()
    cursor4=dbconn.cursor()
    cursor4.execute("SELECT SUM(price) AS total_price FROM cart WHERE user_id=%s",(user_id,))
    results4=cursor4.fetchone()
    cursor4.close()
    return render_template("order_confirmation.html", results1=results1, results2=results2, results3=results3, results4=results4)

@app.route('/update_address', methods=['POST'])
def update_address():
    customer_id = request.form['customer_id']
    new_address = request.form['new_address']
    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("UPDATE orders SET user_address = %s WHERE user_id = %s",(new_address, customer_id))
    cursor.close()
    dbconn.commit()
    flash("Address updated successfully!", "success")
    return redirect(url_for('order_confirmation'))



app.run(debug=True, port=5003)
