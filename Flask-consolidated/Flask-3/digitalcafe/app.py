from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response 
import database as db
import authentication
import logging
import ordermanagement as om

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

@app.route('/changepassword')
def changepassword():
    password = request.form.get('old_password')
    correct_password = db.get_password(password)
    new_password = request.form.get('new_password')
    error = None
    error2 = None
    
    #code for password change
    if(password == correct_password):
        correct_password = new_password
        return redirect('/')
    elif(correct_password == new_password):
        error2 = "The Password you put is the same as your current password. Please enter a new one."
        return render_template('changepassword.html', error2=error2)
    elif(correct_password != password):
        error = "Incorrect Password. Please Try Again"
        return render_template('changepassword.html', error = error)   

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list = branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))
    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    item["code"] = code
    item["qty"] = 0
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*1

    if(session.get("cart") is None):
        session["cart"]={}
    if product['name'] == item['name']:
        item['qty'] += 1

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart', methods=['POST'])
def updatecart():
    code = request.form.get('code', '')
    product = db.get_product(int(code))
    qty = int(request.form.get('qty'))

    cart = session["cart"]

    for item in cart.values():
        if item["code"] == code:
            item["qty"] = qty
            item["subtotal"] = product["price"] * item["qty"]
            cart = session["cart"]
            cart[code] = item
            session["cart"] = cart
    return render_template('cart.html', qty=qty, code=code, product=product)

@app.route('/deleteitem', methods=['POST'])    
def removeproduct():
    code = request.form.get('code', '')
    cart = session["cart"]
    del cart[code]
    session["cart"] = cart
    return redirect('cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/pastorder')
def pastorders():
    past_orders = db.show_orders()
    return render_template('pastorder.html', page="Previous Orders")

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')