#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')
        image_url = json_data.get('image_url')
        bio = json_data.get('bio')

        if username and password:
            new_user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )
            new_user.password_hash = password
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        else:
            return {'error': 'Unprocessable Entity'}, 422


class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return user.to_dict(), 200
        else:
            return {'error:': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        password = request.get_json()['password']

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'error': 'Unauthorized'}, 401
    
class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        else:
            return {'error': 'Unauthorized'}, 401
        

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            recipes = Recipe.query.all()
            recipe_list = [recipe.to_dict() for recipe in recipes]
            return recipe_list, 200
        else:
            return {'error': 'Unauthorized'}, 401
        
    def post(self):
        json_data = request.get_json()
        title = json_data.get('title')
        instructions = json_data.get('instructions')
        minutes_to_complete = json_data.get('minutes_to_make')

        if session.get('user_id'):
            new_recipe = Recipe(
                title = title,
                instructions = instructions,
                minutes_to_complete = minutes_to_complete,
                user_id=session.get('user_id') 
            )
            db.session.add(new_recipe)
            try:
                db.session.commit()
            except Exception:
                return {'error': 'Unprocessable Entity'}, 422
            return new_recipe.to_dict(), 201
        else:
            return {'error': 'Unauthorized'}, 401


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
