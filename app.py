from flask import Flask, request, jsonify
import logging
import src.util.logger
from config import cfg
from src.app_users import Users

app = Flask(__name__)

# Users
@app.route("/users", methods=['GET'])
def get_users():
  return jsonify({"tasks": "Get all Users"})

@app.route("/users/signup", methods=['POST'])
def post_users_sign_up():
  raw_data = raw_data = request.get_json()
  Users.sign_up(user_data=raw_data)
  return jsonify({"tasks": "Sign Up"})

@app.route("/users/login", methods=['POST'])
def post_users_login():
  return jsonify({"tasks": "Login"})


if(__name__ == "__main__"):
  app.run(host="0.0.0.0", port=80, debug=True)
  pass