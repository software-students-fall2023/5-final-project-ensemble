from flask import Flask, jsonify, request, session
from passlib.hash import pbkdf2_sha256
from app import mongo
from user.user import User


class UserAuthentication:
    def sign_up(self):
        user = User().get_user()

        if mongo.db.users.find_one({"username": user["username"]}):
            return jsonify({"error": "Username already in use"}), 400

        if mongo.db.users.insert_one(user):
            return self.start_session(user)

        return jsonify({"error": "Something went wrong"}), 400


    def login(self):
        user = mongo.db.users.find_one({"username": request.form.get("username")})

        if user and pbkdf2_sha256.verify(
            request.form.get("password"), user["password"]
        ):
            return self.start_session(user)

        return jsonify({"error": "Invalid login credentials "}), 401


    def start_session(self, user):
        del user["password"]
        session["logged_in"] = True
        session["user"] = user

        return jsonify(user), 200


    def sign_out(self):
        session.clear()
