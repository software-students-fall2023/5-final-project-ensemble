"""Module providing routing."""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, jsonify, url_for, session
import requests
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import re

load_dotenv()
user = os.environ["MONGO_INITDB_ROOT_USERNAME"]
password = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
uri = f"mongodb://{user}:{password}@localhost:27017"

mongo = MongoClient(uri, server_api=ServerApi('1'))

try:
    mongo.admin.command("ping")
    print("successfully connected to mongo")
except pymongo.errors.ConnectionFailure as e:
    print(e)

app=Flask(__name__, template_folder='../client/templates', static_folder='../client/static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')



def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrap

@app.route('/')
def home():
    """Render home page."""
    inventory = list(mongo.inventory_db.inventory.find())
    inventory.sort(key=lambda x: int(x['sku']))
    return render_template('home.html', inventory=inventory)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        from user.authentication import UserAuthentication

        return UserAuthentication().login()
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        from user.authentication import UserAuthentication

        return UserAuthentication().sign_up()
    return render_template("register.html")

@app.route("/signout")
def signout():
    from models.authentication import UserAuthentication

    UserAuthentication().sign_out()

    return redirect(url_for("login"))

@app.route('/search')
def search():
    """Implement search bar functionality"""
    search_query = request.args.get('query')
    try:
        sku_query = int(search_query)
        sku_match = {"sku": sku_query}
    except ValueError:
        sku_match = {}

    name_match = {"product_name": re.compile(search_query, re.IGNORECASE)}
    query = {"$or": [sku_match, name_match]} if sku_match else name_match
    inventory = mongo.inventory_db.inventory.find(query)

    return render_template('home.html', inventory=inventory)

@app.route('/add_sku', methods=['GET', 'POST'])
def add_sku():
    if request.method == 'POST':
        fsku = request.form.get("sku")
        fname = request.form.get("product_name")
        if not fsku.isdigit() or len(fsku) > 10 or not fname:
            flash("Invalid input. Please ensure all fields are correctly filled.")
            return redirect(url_for('add_sku'))
        
        existing_sku = mongo.inventory_db.inventory.find_one({"sku": fsku})
        if existing_sku:
            flash("SKU already exists. Please enter a unique SKU.")
            return redirect(url_for('add_sku'))
        
        fstock = 0
        sku_data = {
            "sku": fsku,
            "product_name": fname,
            "stock": fstock
        }
        mongo.inventory_db.inventory.insert_one(sku_data)
        return redirect(url_for('home'))
    return render_template('addsku.html')

@app.route('/sku/<sku>')
def sku_details(sku):
    sku = mongo.inventory_db.inventory.find_one({"sku": sku})
    return render_template('sku.html', sku=sku)

app.run(debug=True)