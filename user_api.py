#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'cybersg'

from flask import abort, Blueprint, current_app, request
from flask_restful import Resource
from flaskext.bcrypt import Bcrypt

user_api = Blueprint('user_api', __name__, url_prefix='/users')


class UserApi(Resource):

    def __init__(self):
        self.db = current_app.config['DB']
        self.bcrypt = Bcrypt(current_app)

    def abort(self, response=None):
        if response is None:
            abort(400)
        return (response, 400)

    def prettify(self, user):
        return {
            'login': user['login'],
            'role': 'Admin' if user['admin'] else 'User'
        }

    def find_user(self, login=None):
        if login is None:
            login = request.json['login']
        return self.db.User.find_one({'login': login})

    def get(self, login=None):
        if login:
            user = self.find_user(login)
            if user:
                return self.prettify(user)
        else:
            return [
                self.prettify(r) for r in self.db.User.find()
            ]

    def post(self):
        if request.json is None:
            return self.abort({'message': "Data required"})
        if self.find_user():
            return {'message': "User already exists"}
        user = self.db.User()
        user['login'] = request.json['login']
        user['password'] = self.bcrypt.generate_password_hash(
            request.json['password']
        )
        user.save()
        return ({'message': 'User created successfully!'}, 201)

    def put(self, login):
        user = self.find_user(login)
        if user is None:
            return self.abort({'message': "User not found"})
        curr_pass = request.json.get('current_password', '')
        if not self.bcrypt.check_password_hash(
                user['password'], curr_pass):
            return self.abort({'message': "Invalid password"})
        new_pass = request.json.get('new_password', '')
        if new_pass ==  curr_pass:
            return self.abort({'message': "New password should be different than the old one"})
        confirm_pass = request.json.get('confirm_password')
        if not new_pass:
            return self.abort({'message': "Please provide new password"})
        if new_pass != confirm_pass:
            return self.abort({'message': "New password confirmed incorrectly"})
        user = self.db.User(user)
        user['password'] = self.bcrypt.generate_password_hash(
            request.json['new_password']
        )
        user.save()
        return {'message': "Password changed"}

    def delete(self, login):
        user = self.find_user(login)
        if user:
            self.db.User(user).delete()
        else:
            return self.abort({'message': "User was not found"})
        if self.find_user(login) is not None:
            return self.abort({'message': "User still exists"})
        return {'message': "User deleted successfully"}
