from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    
    # Get all the drinks from db
    drinks = Drink.query.all()
    
    # Transform drink to short data representation
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    
    # Get all the drinks from db
    drinks = Drink.query.all()
    
    # Transform drink to long data representation
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200
    
    
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    # get the body
    body = request.get_json()
    
    try:
        # create new drink
        drink = Drink()
        drink.title = body['title']
        
        # Convert recipe to string
        drink.recipe = json.dumps(body['recipe'])
        
        # insert the new drink
        drink.insert()
    
    except Exception:
        abort(400)
        
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    # Get the body
    body = request.get_json()
    
    # Get the drink with requested id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    # if no drink with given id abort
    if not drink:
        abort(404)
        
    try:
        body_title = body.get('tittle')
        body_recipe = body.get('recipe')
        
        # check if the title is the one is updated
        if body_title:
            drink.title = body_title
            
        if body_recipe:
            drink.recipe = json.dumpd(body['recipe'])
            
        # update the drink
        drink.update()
        
    except Exception:
        abort(400)
        
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # Get the drink with requested id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    # if no drink with given id abort
    if not drink:
        abort(404)
        
    try:
        # delete the drink
        drink.delete()
    except Exception:
        abort(400)
    
    return jsonify({
        'success': True,
        'deleted': id
    }), 200

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def  not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
    
    
@app.errorhandler(401)
def  unathorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
    
    
@app.errorhandler(500)
def  internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server errror"
    }), 500
    
    
@app.errorhandler(400)
def  bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
    
    
@app.errorhandler(405)
def  method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405
    

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    }), 401

if __name__ == '__main__':
    app.debug = True
    app.run()