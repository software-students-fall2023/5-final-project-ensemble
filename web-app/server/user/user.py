from flask import Flask, request
from passlib.hash import pbkdf2_sha256
import uuid


class User:
    def get_user(self):
        user = {
            "_id": uuid.uuid4().hex,
            "username": request.form.get("username"),
            "name": request.form.get("name"),
            "password": request.form.get("password"),
        }

        user["password"] = pbkdf2_sha256.encrypt(user["password"])
        
        return user