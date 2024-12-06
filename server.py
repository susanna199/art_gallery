from flask import *
from flask_mysqldb import *

app=Flask(__name__)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/index2")
def index2():
    return render_template("index2.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/paintings")
def paintings():
    return render_template("paintings.html")

@app.route("/illustrations")
def illustrations():
    return render_template("illustrations.html")

@app.route("/abstract")
def abstract():
    return render_template("abstract.html")

@app.route("/sketches")
def sketches():
    return render_template("sketches.html")

@app.route("/portraits")
def portraits():
    return render_template("portraits.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/artwork")
def artwork():
    return render_template("artwork.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/artists")
def artists():
    return render_template("artists.html")

# @app.route('/filter_artwork', methods=['GET'])
# def filter_artwork():
#     try:
#         cursor = mysql.connection.cursor()
#         filter_category = request.args.get('category')
#         cursor.execute("SELECT * FROM artwork WHERE category = %s", (filter_category,))
#         res = cursor.fetchall()
#         print(res)
#         cursor.close()
#         return render_template('filter_artwork.html', res=res)
#     except Exception as e:
#         return render_template("artwork.html")

# @app.route("/display", methods = ['post'])
# def paintings():
#     paintings = request.form['painting']
#     print(paintings)
#     dbconn = mysql.connection
#     cursor = dbconn.cursor()
#     cursor.execute("Select * from artwork where category = %s", (paintings,))
#     res = cursor.fetchall()
#     print(res)
#     return render_template("display.html",filter_category=res)

@app.route("/sitelayout")
def sitelayout():
    return render_template("sitelayout.html")

app.run(debug=True)