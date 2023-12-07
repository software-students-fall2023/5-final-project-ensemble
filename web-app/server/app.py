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
passw = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
uri = f"mongodb://{user}:{passw}@mongo:27017/db?authSource=admin"

mongo = MongoClient(uri, server_api=ServerApi('1'))

try:
    mongo.admin.command("ping")
    print("successfully connected to mongo")
except pymongo.errors.ConnectionFailure as e:
    print(e)

app=Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/')
def home():
    inventory = list(mongo.db.inventory.find())
    inventory.sort(key=lambda x: int(x['SKU']))
    return render_template('home.html', inventory=inventory)

@app.route('/search')
def search():
    search_query = request.args.get('query')
    inventory = mongo.db.inventory.find({"SKU": re.compile(search_query, re.IGNORECASE)})
    return render_template('home.html', inventory=inventory)