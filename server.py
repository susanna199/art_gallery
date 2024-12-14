from flask import *
from flask_mysqldb import *
from datetime import datetime

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '3043'
app.config['MYSQL_DB'] = 'mydb'
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
        session['user_name'] = user2[1]
        session['user_id'] = user2[0]

        # return redirect('/home')  # Default page after login (e.g., homepage)
        redirect_url = session.get('redirect_url', '/home')  # Default to home if no redirect_url is found
        session.pop('redirect_url', None)  # Remove the redirect URL after using it
        return redirect(redirect_url)
    else:
        return redirect("/login")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():

    return render_template("contact.html")

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
    cursor.execute("SELECT * FROM mydb.artists")
    results=cursor.fetchall()
    cursor.close()
    return render_template("artists.html", results=results)

@app.route("/registration")
def registration():
    session['is_admin'] = False
    session['is_user'] = False
    return render_template("registration.html")

@app.route("/reg_confirm", methods=['POST'])
def reg_confirm():
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['email']
    password=request.form['password']
    cpassword=request.form['cpassword']
    pno=request.form['pno']
    event=request.form['event']

    # Simple validation for password and confirm password match
    if password != cpassword:
        return "Passwords do not match. Please try again."

    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO registered_users(fname, lname, email, password, c_password, phone, event) VALUES (%s,%s,%s,%s,%s,%s,%s)", (fname,lname,email,password,cpassword,pno,event,))
    dbconn.commit()
    cursor.close()
    
    return render_template("reg_confirm.html", event=event)

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


@app.route("/add_to_cart", methods = ['post'])
def add_to_cart():
    if 'is_user' in session and session['is_user']:
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        user_name = session['user_name']
        user_id = session['user_id']

        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("insert into cart (user_id, user_name, product_id, product_name, price)values (%s, %s, %s, %s, %s)",(user_id, user_name, product_id, product_name, product_price,))
        dbconn.commit()
        cursor.close()
        flash('Product Added to Cart Successfully!', 'success')
        return redirect("/artwork")
    else:
        session['redirect_url'] = request.referrer
        return redirect("/login")


@app.route("/cart")
def cart():
    if 'is_user' in session and session['is_user']:
        user_id = session['user_id']
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute('''select artwork.product_path , artwork.name, cart.price, artwork.id, cart.cart_id
                       from cart 
                       join artwork on cart.product_id = artwork.id
                       where cart.user_id = %s''', (user_id,))
        res = cursor.fetchall()
        cursor2 = dbconn.cursor()
        cursor2.execute('''select sum(price) as total
                            FROM cart
                            WHERE user_id = %s''', (user_id,))
        total = cursor2.fetchone()[0]
        
        if total:
            total = "{:,.2f}".format(total) 

        cursor3 = dbconn.cursor()
        cursor3.execute("select user_id, product_id from cart")
        res2 = cursor3.fetchone()

        return render_template("cart.html", res = res, res2 = res2, total = total)
    else:
        return redirect("/login")

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    
    product_id = int(request.form['product_id'])
    cart_id = int(request.form['cart_id'])
    print(product_id)

    # Connect to the database
    dbconn = mysql.connection
    cursor = dbconn.cursor()

    # Execute SQL query to remove the product from the cart for the logged-in user
    cursor.execute("DELETE FROM cart WHERE cart_id = %s AND user_id = %s", (cart_id, session['user_id']))
    dbconn.commit()

    cursor.close()

    # Respond with a success message
    return redirect("/cart")



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
        dbconn = mysql.connection
        cursor1 = dbconn.cursor()
        cursor1.execute("SELECT * from events")
        res = cursor1.fetchall()
        return render_template("add_event.html",res = res)
    else:
        return redirect("/login")

@app.route("/adding_events", methods = ['post'])
def adding_events():
    event_name = request.form['name']
    event_date = request.form['date']
    description = request.form['description']
    event_img = request.files['event_img']

    


    event_filename = event_img.filename
    event_poster_path = "art_gallery/static/images/"+event_filename
    event_img.save(event_poster_path)
    
    dbconn = mysql.connection
    cursor2 = dbconn.cursor()
    cursor2.execute("Insert into events (event_name, event_date, description, event_img) values (%s, %s, %s, %s)", (event_name, event_date, description, event_poster_path,))
    dbconn.commit()
    cursor2.close()
    
    return render_template("admin_dashboard.html", message = "Successfully Added the Event")


@app.route("/customer_query", methods=['POST'])
def customer_query():
    name=request.form['name']
    email=request.form['email']
    message=request.form['message']
    status = 'Pending'
    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO customer_query (name, email, message, status) VALUES (%s,%s,%s,%s)", (name, email, message, status))
    dbconn.commit()
    cursor.close()
    flash("Your query has been submitted successfully. You will hear from us soon!","success")
    return redirect("/contact")


# -- Admin Operation: to view user queries
@app.route("/queries")
def queries():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customer_query")
    res = cursor.fetchall()
    return render_template("queries.html",res = res)

@app.route("/resolve_query", methods=["POST"])
def resolve_query():
    selected_orders = request.form.getlist("selected_orders")  # Get list of selected order IDs

    if selected_orders:
        cursor = mysql.connection.cursor()
        
        # Update status of selected orders to 'Resolved', but only for those that are currently 'Pending'
        cursor.execute("""
            UPDATE customer_query
            SET status = 'Resolved'
            WHERE query_id IN (%s)
        """ % ",".join(["%s"] * len(selected_orders)), tuple(selected_orders))
        
        mysql.connection.commit()
        cursor.close()
        
        flash("Selected queries have been resolved!", "success")
        return redirect("/queries")
    
    flash("No orders selected.", "warning")
    return redirect("/queries")



@app.route("/logout")
def logout():
    session.clear()
    if 'is_admin' in session and session['is_admin']:
        session.pop('email',None)
        session.pop('is_admin',None)
    elif 'is_user' in session and session['is_user']:
        session.pop('email',None)
        session.pop('user_name',None)
        session.pop('is_user',None)
    else:
        return redirect("/home")
    return redirect("/home")
app.run(debug=True, port=5003)
