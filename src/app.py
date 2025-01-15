"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Starships, UserS, FavoriteCharacters, FavoritePlanets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users')
def get_users():
    all_users = UserS.query.all()
    all_users_serialized = []

    for us in all_users:
        all_users_serialized.append(us.serialize())

    return jsonify({'msg' : 'get users ok', 'data' : all_users_serialized})  

@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet_in_user(user_id, planet_id):     
    favorite_planet = FavoritePlanets.query.filter_by(
        user_id=user_id,
        planet_id=planet_id
    ).first()

    if favorite_planet:
        return jsonify({'msg' : 'The planet is already added as a favorite.'},
                       {'planet' : favorite_planet.favorite_planets.serialize()}), 400

    favorite_planet = FavoritePlanets()
    favorite_planet.planet_id = planet_id
    favorite_planet.user_id = user_id
    db.session.add(favorite_planet)
    db.session.commit()

    return jsonify({'msg' : 'Planet added to favorites.'})

@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_planet_in_user(user_id, planet_id):
    # Buscar el registro específico de favorito
    favorite_planet = FavoritePlanets.query.filter_by(
        user_id=user_id,
        planet_id=planet_id
    ).first()

    # Verificar si el registro existe
    if favorite_planet:
        db.session.delete(favorite_planet)
        db.session.commit()
        return jsonify({'msg': 'The planet has been removed from favorites.'})

    # Si no se encuentra el favorito
    return jsonify({'msg': "Planet isn't in favorites or invalid user"}), 400

@app.route('/favorite/<int:user_id>/character/<int:character_id>', methods=['POST'])
def add_fav_character_in_user(user_id, character_id):
    favorite_character = FavoriteCharacters.query.filter_by(
        user_id = user_id,
        character_id = character_id).first()
    
    if favorite_character:
        return jsonify({'msg' : 'The character is already added as a favorite.'},
                       {'character' : favorite_character.favorite_characters.serialize()}), 400
    
    favorite_character = FavoriteCharacters()
    favorite_character.user_id = user_id
    favorite_character.character_id = character_id
    db.session.add(favorite_character)
    db.session.commit()

    return jsonify({'msg' : 'Character added to favorites.'})

@app.route('/favorite/<int:user_id>/character/<int:character_id>', methods=['DELETE'])
def delete_fav_character_in_user(user_id, character_id):
    favorite_character = FavoriteCharacters.query.filter_by(user_id = user_id, character_id = character_id).first()

    if favorite_character:
        db.session.delete(favorite_character)
        db.session.commit()
        return jsonify({'msg' : 'The character has been removed from favorites'})

    return jsonify({'msg' : "Character isn't in favorites or invalid user"}), 400

@app.route('/users/<int:user_id>/favorites')
def get_favorites_by_user(user_id):
    favorite_characters = FavoriteCharacters.query.filter_by(user_id = user_id).all()
    favorite_planets = FavoritePlanets.query.filter_by(user_id = user_id).all()
    user = UserS.query.get(user_id).serialize()

    if not favorite_characters and not favorite_planets:
        return jsonify({'msg' : f"The user with id {user_id} doesn't have any favorite."},
                       {'user' : user},), 400  

    favorite_characters_serialized = []

    for fav in favorite_characters:
        favorite_characters_serialized.append(fav.favorite_characters.serialize())

    favorite_planets_serialized = []

    for fav in favorite_planets:        
        favorite_planets_serialized.append(fav.favorite_planets.serialize())    

    print(f'++++++ {favorite_planets_serialized}')    
    return jsonify(
        {'msg' : 'ok get favorites'}, 
        {'user' : user},
        {'characters': favorite_characters_serialized},
        {'planets' : favorite_planets_serialized}        
        )

    
@app.route('/characters')
def get_characters():
    all_characters = Characters.query.all()
    all_ch_serialized = []

    for ch in all_characters:
        all_ch_serialized.append(ch.serialize())
    
    print(all_ch_serialized)
    return jsonify({'msg': 'get characters ok', 'data': all_ch_serialized})

@app.route('/characters/<int:character_id>')
def get_one_character(character_id):
    char_query = Characters.query.get(character_id)
    if char_query is None:
        return jsonify({'msg' : f"The character with id {character_id} doesn't exist."}), 400

    return jsonify({'msg' : f'get character with id {character_id} ok', 'data' : char_query.serialize()})

@app.route('/characters', methods=['POST'])
def add_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg' : 'Query needs body: name, gender, species'}), 400
    if 'name' not in body:
        return jsonify({'msg' : 'Query needs name'}), 400
    if 'gender' not in body:
        return jsonify({'msg' : 'Query needs gender'}), 400
    if 'species' not in body:
        return jsonify({'msg' : 'Query needs species'}), 400    
    
    char = Characters()
    char.name = body['name']
    char.gender = body['gender']
    char.species = body['species']
    db.session.add(char)
    db.session.commit()
    
    return jsonify({'msg' : 'Character added', 'data': char.serialize()})

@app.route('/planets')
def get_planets():
    all_planets = Planets.query.all()
    all_pl_serialized = []

    for pl in all_planets:
        all_pl_serialized.append(pl.serialize())    
    print(all_pl_serialized)
    return jsonify({'msg': 'get planets ok', 'data': all_pl_serialized})

@app.route('/planets/<int:planet_id>')
def get_one_planet(planet_id):
    planet_query = Planets.query.get(planet_id)

    if planet_query is None:
        return jsonify({'msg' : f"The planet with id {planet_id} doesn't exist."}), 400
    
    planet_serialize = planet_query.serialize()
    planet_serialize['characters'] = []
    
    for ch in planet_query.characters:
        planet_serialize['characters'].append(ch.serialize())
    
    return jsonify({'msg' : f'get planet with id {planet_id} ok', 'data' : planet_serialize})

@app.route('/starships')
def get_starships():
    all_starships = Starships.query.all()
    all_ss_serialized = []

    for ss in all_starships:
        all_ss_serialized.append(ss.serialize())
    
    print(all_ss_serialized)
    return jsonify({'msg': 'get starship ok', 'data': all_ss_serialized})

@app.route('/starships/<int:starship_id>')
def get_one_starship(starship_id):
    ss_query = Starships.query.get(starship_id)

    if ss_query is None:
        return jsonify({'msg' : f"The starship with id {starship_id} doesn't exist."}), 400

    ss_serialize = ss_query.serialize()
    ss_serialize['characters'] = []
    for character in ss_query.characters:
        ss_serialize['characters'].append(character.serialize())

    return jsonify({'msg' : f'get starship with id {starship_id} ok', 'data' : ss_serialize})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
