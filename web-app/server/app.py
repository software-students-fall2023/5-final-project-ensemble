"""Module providing routing."""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, jsonify
import requests
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
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

@app.route('/')
def home():
    """Render home page."""
    inventory = list(mongo.inventory_db.inventory.find())
    inventory.sort(key=lambda x: int(x['sku']))
    return render_template('home.html', inventory=inventory)

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

app.run(debug=True)