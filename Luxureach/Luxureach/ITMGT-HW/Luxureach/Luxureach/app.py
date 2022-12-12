from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
import database as db
import authentication
import logging


app = Flask(__name__)

# Set the secret key to some random bytes. 
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

navbar = """
         <a href='/'>Home</a> | <a href='/products'>Products</a> |
         <a href='/branches'>Branches</a> | <a href='/aboutus'>About Us</a>
         <p/>
         """

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    correct_username = db.get_username(username)
    correct_password = db.get_password(password)
    error = None

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    elif(correct_password != password or correct_username != username):
        error = "Invalid Username or Password. Please try again"
        return render_template('login.html', error=error)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    correct_username = db.get_username(username)
    correct_password = db.get_password(password)
    error = None

    

    if(correct_password == password or correct_username == username):
        error = "Email or Username Already Exists."
        return render_template('signup.html', error=error)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/categories')
def categories():
    return render_template('dropdown.html')

@app.route('/products')
def products():
    return render_template('products.html', page="Products")

@app.route('/branches')
def branches():
    return render_template('branches.html', page="Community")

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a 
    # quantity of 1 for now
    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')