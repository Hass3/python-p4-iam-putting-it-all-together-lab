#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        data = request.get_json()
        username_form = data.get('username')
        password = data.get('password')
        image_url_form = data.get('image_url')
        bio_form = data.get('bio')
        if not username_form or not password:
            return {"Error": "Fields are required"}, 422
        if User.query.filter_by(username=username_form).first():
            return {"Error": "User already exsits"}, 422
    
        new_user = User(
            username = username_form,
            image_url = image_url_form,
            bio =bio_form
            )
        new_user.password_hash = password
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id

        new_user_to_json = {
            "id" : new_user.id,
            "username" : new_user.username,
            "img_url" : new_user.image_url,
            "bio" : new_user.bio
            }
        return new_user_to_json, 201
    
        
class CheckSession(Resource):
    def get(self):
        logged_in_user = User.query.filter(User.id == session['user_id']).first()
        if logged_in_user:
            logged_in_user_to_json = {
                "id" : logged_in_user.id,
                "username" : logged_in_user.username,
                "img_url" : logged_in_user.image_url,
                "bio" : logged_in_user.bio
            }
            return logged_in_user_to_json, 200
        
        return {"error": "user is logged in"}, 401
        
        
class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        password = request.get_json()['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            return  {'error' : 'invailid username or password'}, 401

        if not user.authenticate(password):
            return {'error' : 'invailid username or password'}, 401
        

        session['user_id'] = user.id

        user_to_json = {
            "id" : user.id,
            "username" : user.username,
            "img_url" : user.image_url,
            "bio" : user.bio
            }
        return user_to_json, 200
    
class Logout(Resource):
    def delete(self):
        user = User.query.filter(User.id == session['user_id']).first()
        if user:
            session['user_id'] = None
            return {}, 204
        return {'error':'user is not logged in'}, 401
    

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session['user_id']).first()
        if not user:
            return {'error':'user is not logged in'}, 401
        recipes = []
        for recipe in user.recipes:
            recipe_json = {
                "title" : recipe.title,
                "instructions":recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "img_url": recipe.user.image_url,
                    "bio": recipe.user.bio
                }
            }
            recipes.append(recipe_json)
        return recipes, 200
    

    def post(self):
        user = User.query.filter(User.id == session['user_id']).first()
        title_form = request.get_json()['title']
        min_to_complete = request.get_json()['minutes_to_complete']
        instr = request.get_json()['instructions']

        if not user:
            return {'error':'user is not logged in'}, 401
        
        
        try:
            new_recipe = Recipe(
            title = title_form,
            instructions = instr,
            minutes_to_complete = min_to_complete,
            user_id = session['user_id']
          )
            db.session.add(new_recipe)
            db.session.commit()
           
        except ValueError as e:
            return {'error' : f'{str(e)}'}, 422
        new_recipe_json = {
                "title" : new_recipe.title,
                "instructions" : new_recipe.instructions,
                "minutes_to_complete" : new_recipe.minutes_to_complete,
            }
        return new_recipe_json, 201
        
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)