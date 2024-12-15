from flask import *
from flask_mysqldb import *
from datetime import datetime

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'

app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'mydb2'

mysql = MySQL(app)

# For user session management
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route("/home")
def home():
    dbconn = mysql.connection
    cursor1 = dbconn.cursor()
    
    id = request.args.get('id', default=1, type=int)
    cursor1.execute("Select * from artwork limit 4")
    artworks = cursor1.fetchall()

    cursor2 = dbconn.cursor()
    
    id = request.args.get('id', default=1, type=int)
    cursor2.execute("Select * from artists limit 5")
    artists = cursor2.fetchall()

    cursor3 = dbconn.cursor()
    
    id = request.args.get('id', default=1, type=int)
    cursor3.execute("Select * from events limit 3")
    events= cursor3.fetchall()

    return render_template('index3.html', artists=artists, artworks=artworks, events=events)

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

    dbconn=mysql.connection
    cursor=dbconn.cursor()
    cursor.execute("INSERT INTO customer_query VALUES (%s,%s,%s)", (name, email, message))
    dbconn.commit()
    cursor.close()

    return ("Your query has been submitted successfully. You will hear from us soon!")


@app.route("/registration")
def registration():
    session['is_admin'] = False
    session['is_user'] = False
    dbconn=mysql.connection
    cursor1=dbconn.cursor()
    cursor1.execute("SELECT event_name FROM events WHERE event_date BETWEEN CURRENT_DATE() AND '2025-01-30'")
    results1=cursor1.fetchall()
    cursor1.close()
    return render_template("registration.html", results1=results1)

    
    #return render_template("registration.html")


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
        cursor.execute("SELECT * FROM artwork WHERE category = %s", (filter_category,))
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


@app.route("/add_artist")
def add_artist():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor1 = dbconn.cursor()
        cursor1.execute("SELECT * from artists")
        res = cursor1.fetchall()
        return render_template("add_artist.html",res = res)
    else:
        return redirect("/login")


@app.route("/adding_artist", methods=['POST'])
def adding_artist():
    artist_name = request.form['name']
    hails_from = request.form['hails_from']
    description = request.form['description']
    artist_img = request.files['artist_img']

    # Save the artist image to a static folder
    artist_filename = artist_img.filename
    artist_image_path = "static/images/" + artist_filename
    artist_img.save(artist_image_path)

    # Database operation
    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("INSERT INTO artists (artist_name, hails_from, description, artist_img) VALUES (%s, %s, %s, %s)",
                   (artist_name, hails_from, description, artist_image_path))
    dbconn.commit()
    cursor.close()

    return render_template("admin_dashboard.html", message="Artist successfully added!")

@app.route("/add_artwork")
def add_artwork():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor1 = dbconn.cursor()
        cursor1.execute("SELECT * from artwork")
        res = cursor1.fetchall()
        return render_template("add_artwork.html",res = res)
    else:
        return redirect("/login")

@app.route("/adding_artwork", methods=['POST'])
def adding_artwork():
    category = request.form['category']
    name = request.form['name']
    artist_name = request.form['artist_name']
    year = request.form['year']
    size = request.form['size']
    price = request.form['price']
    description = request.form['description']
    product_path = request.files['product_path']

    product_filename = product_path.filename
    product_img_path = "static/images/" + product_filename
    product_path.save(product_img_path)

    dbconn = mysql.connection
    cursor = dbconn.cursor()
    cursor.execute("INSERT INTO artwork (category, name, product_path, artist_name, year, size, price, description) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                   (category, name, product_img_path, artist_name, year, size, price, description))
    dbconn.commit()
    cursor.close()

    return render_template("admin_dashboard.html", message="Successfully Added the Artwork")

    
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


    
@app.route("/modify_artist")
def modify_artist():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT * FROM artists")
        res = cursor.fetchall()
        return render_template("modify_artist.html", res=res)
    else:
        return redirect("/login")
 

@app.route("/modifying_artist", methods=["POST"])
def modifying_artist():
    try:
        artist_id = request.form['artist_id']
        artist_name = request.form.get('artist_name', None)
        hails_from = request.form.get('hails_from', None)
        description = request.form.get('description', None)
        artist_img = request.files.get('artist_img', None)

        # Update database
        dbconn = mysql.connection
        cursor = dbconn.cursor()

        # Dynamically update only provided fields
        update_fields = []
        values = []

        if artist_name:
            update_fields.append("artist_name = %s")
            values.append(artist_name)

        if hails_from:
            update_fields.append("hails_from = %s")
            values.append(hails_from)

        if description:
            update_fields.append("description = %s")
            values.append(description)

        if artist_img:
            img_path = f"static/uploads/{artist_img.filename}"
            artist_img.save(img_path)
            update_fields.append("artist_img = %s")
            values.append(img_path)

        if update_fields:
            query = f"UPDATE artists SET {', '.join(update_fields)} WHERE artist_id = %s"
            values.append(artist_id)
            cursor.execute(query, values)
            dbconn.commit()

        return render_template("success.html", message="Artist modified successfully!")
    except Exception as e:
        return render_template("error.html", message=f"An error occurred: {e}")

    
@app.route("/modify_event")
def modify_event():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT * FROM events")
        res = cursor.fetchall()
        return render_template("modify_event.html", res=res)
    else:
        return redirect("/login")

@app.route("/modifying_event", methods=["POST"])
def modifying_event():
    try:
        event_id = request.form['event_id']
        event_name = request.form.get('name', None)
        event_date = request.form.get('date', None)
        description = request.form.get('description', None)
        event_img = request.files.get('event_img', None)

        # Update database
        dbconn = mysql.connection
        cursor = dbconn.cursor()

        # Dynamically update only provided fields
        update_fields = []
        values = []

        if event_name:
            update_fields.append("event_name = %s")
            values.append(event_name)

        if event_date:
            update_fields.append("event_date = %s")
            values.append(event_date)

        if description:
            update_fields.append("description = %s")
            values.append(description)

        if event_img:
            img_path = f"static/uploads/{event_img.filename}"
            event_img.save(img_path)
            update_fields.append("event_img = %s")
            values.append(img_path)

        if update_fields:
            query = f"UPDATE events SET {', '.join(update_fields)} WHERE event_id = %s"
            values.append(event_id)
            cursor.execute(query, values)
            dbconn.commit()
    

        return render_template("success.html", message="Event modified successfully!")
    except Exception as e:
        return render_template("error.html", message=f"An error occurred: {e}")


@app.route("/modify_artwork")
def modify_artwork():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT * FROM artwork")
        res = cursor.fetchall()
        return render_template("modify_artwork.html", res=res)
    else:
        return redirect("/login")

@app.route("/modifying_artwork", methods=["POST"])
def modifying_artwork():
    try:
        artwork_id = request.form['artwork_id']
        category = request.form.get('category', None)
        name = request.form.get('name', None)
        product_path = request.form.get('product_path', None)
        artist_name = request.form.get('artist_name', None)
        year = request.form.get('year', None)
        size = request.form.get('size', None)
        price = request.form.get('price', None)
        description = request.form.get('description', None)
        artwork_img = request.files.get('artwork_img', None)

        # Update database
        dbconn = mysql.connection
        cursor = dbconn.cursor()

        # Dynamically update only provided fields
        update_fields = []
        values = []

        if category:
            update_fields.append("category = %s")
            values.append(category)

        if name:
            update_fields.append("name = %s")
            values.append(name)

        if product_path:
            update_fields.append("product_path = %s")
            values.append(product_path)

        if artist_name:
            update_fields.append("artist_name = %s")
            values.append(artist_name)

        if year:
            update_fields.append("year = %s")
            values.append(year)

        if size:
            update_fields.append("size = %s")
            values.append(size)

        if price:
            update_fields.append("price = %s")
            values.append(price)

        if description:
            update_fields.append("description = %s")
            values.append(description)

        if artwork_img:
            img_path = f"static/uploads/{artwork_img.filename}"
            artwork_img.save(img_path)
            update_fields.append("product_path = %s")
            values.append(img_path)

        if update_fields:
            query = f"UPDATE artwork SET {', '.join(update_fields)} WHERE id = %s"
            values.append(artwork_id)
            cursor.execute(query, values)
            dbconn.commit()

        return render_template("success.html", message="Artwork modified successfully!")
    except Exception as e:
        return render_template("error.html", message=f"An error occurred: {e}")


    
@app.route("/delete_artist")
def delete_artist():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT artist_id, artist_name FROM artists")
        res = cursor.fetchall()
        return render_template("delete_artist.html", res=res)
    else:
        return redirect("/login")
    
@app.route("/deleting_artist", methods=["GET", "POST"])
def deleting_artist():
    try:
        # Connect to the database
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        
        # Fetch all artists
        cursor.execute("SELECT * FROM artists")
        artists = cursor.fetchall()

        if request.method == "POST":
            artist_id = request.form['artist_id']
            cursor.execute("DELETE FROM artists WHERE artist_id = %s", (artist_id,))
            dbconn.commit()
            return render_template("success.html", message="Artist deleted successfully!")

        # Render the page with artists data
        return render_template("delete_artist.html", artists=artists)
        
    except Exception as e:
        return render_template("error.html", message=f"An error occurred: {e}")

    
@app.route("/delete_artwork")
def delete_artwork():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT id, name, artist_name FROM artwork")
        res = cursor.fetchall()
        return render_template("delete_artwork.html", res=res)
    else:
        return redirect("/login")

@app.route("/deleting_artwork", methods=["GET", "POST"])
def deleting_artwork():
    try:
        # Connect to the database
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        
        # Fetch all artists
        cursor.execute("SELECT * FROM artwork")
        artwork = cursor.fetchall()

        if request.method == "POST":
            id = request.form['id']
            cursor.execute("DELETE FROM artwork WHERE id = %s", (id,))
            dbconn.commit()
            return render_template("success.html", message="Artwork deleted successfully!")

        # Render the page with artists data
        return render_template("delete_artwork.html", artwork=artwork)
        
    except Exception as e:
        return render_template("error.html", message=f"An error occurred: {e}")
    
@app.route("/delete_event")
def delete_event():
    if session['is_admin']:
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT event_id, event_name, event_date FROM events")
        res = cursor.fetchall()
        return render_template("delete_event.html", res=res)
    else:
        return redirect("/login")

@app.route("/deleting_event", methods=["POST"])
def deleting_event():
    try:
        event_id = request.form['event_id']
        dbconn = mysql.connection
        cursor = dbconn.cursor()
        cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
        dbconn.commit()
        return render_template("success.html", message="Event deleted successfully!")
    except Exception as e:
        return render_template("error.html", message=f"An error occurred: {e}")


app.run(debug=True, port=5003)

