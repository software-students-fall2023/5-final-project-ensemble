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
from functools import wraps

load_dotenv()
user = os.environ["MONGO_INITDB_ROOT_USERNAME"]
password = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
uri = f"mongodb://{user}:{password}@mongo:27017/db?authSource=admin"

mongo = MongoClient(uri, server_api=ServerApi('1'))

try:
    mongo.admin.command("ping")
    print("successfully connected to mongo")
except pymongo.errors.ConnectionFailure as e:
    print("Failed:",e)

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

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        from user.authentication import UserAuthentication

        return UserAuthentication().login()
    return render_template("login.html")

@app.route('/home/')
@login_required
def home():
    """Render home page."""
    user_id = session["user"].get("_id")
    name = session["user"].get("name")
    inventory = list(mongo.db.inventory.find({"user_id": user_id}))
    inventory.sort(key=lambda x: int(x['sku']))
    return render_template('home.html', inventory=inventory, name=name)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        from user.authentication import UserAuthentication

        return UserAuthentication().sign_up()
    return render_template("register.html")

@app.route("/signout")
@login_required
def signout():
    from user.authentication import UserAuthentication

    UserAuthentication().sign_out()
    return redirect(url_for("login"))

@app.route('/search')
@login_required
def search():
    user_id = session["user"].get("_id")
    name = session["user"].get("name")
    search_query = request.args.get('query')

    sku_match = {"sku": str(search_query)}
    name_match = {"product_name": re.compile(search_query, re.IGNORECASE)}

    query = {"$and": [{"user_id": user_id}, {"$or": [sku_match, name_match]}]}

    if not sku_match:
        query = {"$and": [{"user_id": user_id}, name_match]}

    inventory = list(mongo.db.inventory.find(query))

    return render_template('home.html', inventory=inventory, name=name)

@app.route('/add_sku', methods=['GET', 'POST'])
@login_required
def add_sku():
    if request.method == 'POST':
        user_id = session["user"].get("_id")
        fsku = request.form.get("sku")
        fname = request.form.get("product_name")
        fstock = request.form.get("stock")

        if not fsku.isdigit() or len(fsku) > 10 or not fname:
            flash("Invalid input. Fix SKU and/or product name input.")
            return redirect(url_for('add_sku'))
        
        existing_sku = mongo.db.inventory.find_one({"sku": fsku, "user_id": user_id})
        if existing_sku:
            flash("SKU already exists. Please enter a unique SKU.")
            return redirect(url_for('add_sku'))
        
        if not fstock.isdigit() or not fstock:
            flash("Invalid input. Fix stock input.")
            return redirect(url_for('add_sku'))

        sku_data = {
            "sku": fsku,
            "product_name": fname,
            "stock": fstock,
            "user_id": user_id
        }
        mongo.db.inventory.insert_one(sku_data)
        return redirect(url_for('home'))
    return render_template('addsku.html')

@app.route('/sku/<sku>')
@login_required
def sku_details(sku):
    user_id = session["user"].get("_id")
    sku = mongo.db.inventory.find_one({"sku": sku, "user_id": user_id})
    return render_template('sku.html', sku=sku)

@app.route('/add_log', methods=['GET', 'POST'])
@login_required
def add_log():
    user_id = session["user"].get("_id")

    if request.method == 'POST':
        sku = request.form.get("sku")
        action = request.form.get("action")
        quantity = int(request.form.get("quantity"))

        current_item = mongo.db.inventory.find_one({"sku": sku, "user_id": user_id})
        if not current_item:
            flash("SKU not found.")
            return redirect(url_for('add_log'))

        new_stock = int(current_item['stock']) + quantity if action == 'increase' else int(current_item['stock']) - quantity
        if new_stock < 0:
            flash("Cannot decrease stock below 0.")
            return redirect(url_for('add_log'))

        mongo.db.inventory.update_one({"sku": sku, "user_id": user_id}, {"$set": {"stock": new_stock}})

        flash("Stock updated successfully.")
        return redirect(url_for('home'))

    return render_template('add_log.html')

@app.route('/sku/<sku>/edit_sku', methods=['GET', 'POST'])
@login_required
def edit_sku(sku):
    user_id = session["user"].get("_id")
    sku = mongo.db.inventory.find_one({"sku": sku, "user_id": user_id})
    
    if request.method == 'POST':
        fsku = request.form.get("sku")
        fname = request.form.get("product_name")
        fstock = request.form.get("stock")
        
        if fsku:
            if not fsku.isdigit() or len(fsku) > 10:
                flash("Invalid input. Please fix sku input.")
                return redirect(url_for('edit_sku', sku=sku))
            existing_sku = mongo.db.inventory.find_one({"sku": fsku, "user_id": user_id})
            if existing_sku and existing_sku != sku['sku']:
                flash("SKU already exists. Please enter a unique SKU.")
                return redirect(url_for('edit_sku', sku=sku))
        else:
            fsku = sku['sku']
        if fstock:
            if not fstock.isdigit():
                flash("Invalid input. Please fix stock input.")
                return redirect(url_for('edit_sku', sku=sku))
        else:
            fstock = sku['stock']
        
        if not fname:
            fname = sku['product_name']
        
        mongo.db.inventory.find_one_and_update(
            {"sku": sku['sku'], "user_id": user_id} , {'$set': {'product_name': fname, 'sku':fsku, 'stock': fstock}},
            )
        return redirect(url_for('home'))
    
    return render_template('editsku.html', sku=sku)

@app.route('/sku/<sku>/delete_sku', methods=['GET'])
@login_required
def delete_sku(sku):
    user_id = session["user"].get("_id")
    sku = mongo.db.inventory.find_one({"sku": sku, "user_id": user_id})
    if sku is None:
        flash("SKU not found.")
        return redirect(url_for('home'))
    return render_template('deletesku.html', sku=sku)

@app.route('/sku/<sku>/confirm_delete_sku', methods=['POST'])
@login_required
def confirm_delete_sku(sku):
    user_id = session["user"].get("_id")
    mongo.db.inventory.delete_one({"sku": sku, "user_id": user_id})
    flash("SKU deleted successfully.")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
