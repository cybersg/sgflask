#!/usr/bin/env python
#-*- coding: utf-8 -*-
__author__ = 'cybersg'

from hashlib import md5
from flask import Blueprint, current_app, request
from flask_restful import Api, Resource

user_api = Blueprint('user_api', __name__, url_prefix='/users')

class UserListApi(Resource):

    def __init__(self):
        self.db = current_app.config['DB']

    def get(self):
        return [
            {
                'login': r['login'],
                'role': 'Admin' if r['admin'] else 'User'
            } for r in self.db.User.find()
        ]

class UserApi(Resource):

    def __init__(self):
        self.db = current_app.config['DB']

    def get(self, login=None):
        if login:
            return self.db.User.find_one({'login': login})
        else:
            return [
                {
                    'login': r['login'],
                    'role': 'Admin' if r['admin'] else 'User'
                } for r in self.db.User.find()
            ]

    def post(self):
        if request.json is None:
            return ({'message': "Data required"}, 400)
        if self.db.User.find_one({'login': request.json['login']}):
            return {'message': 'User already exists'}
        user = self.db.User()
        user['login'] = request.json['login']
        user['password'] = md5(request.json['password']).hexdigest()
        user.save()
        return ({'message': 'User created successfully!'}, 201)

    def put(self, login):
        pass
        #self.db.User.sa

    def delete(self, login):
        self.db.User.remove({'login': login})