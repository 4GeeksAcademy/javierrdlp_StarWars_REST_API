from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class UserS(db.Model):
    __tablename__= 'userS'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique = True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250))
    subscription_date = db.Column(db.String(50))

    character_favorite = db.relationship('FavoriteCharacters', back_populates='users')
    planet_favorite = db.relationship('FavoritePlanets', back_populates='users')

    def __repr__(self):
        return f'UserS  Id:{self.id}  {self.first_name}'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "fisrtName": self.first_name
        }

class FavoriteCharacters(db.Model):
    __tablename__= 'favorite_characters'
    id = db.Column(db.Integer, primary_key=True)   

    user_id = db.Column(db.Integer, db.ForeignKey('userS.id'), nullable=False)
    users = db.relationship('UserS', back_populates='character_favorite')

    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)  
    favorite_characters = db.relationship('Characters', back_populates='favorite_by')

    def __repr__(self):
        return f'User {self.user_id} likes character {self.character_id}'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }

class FavoritePlanets(db.Model):
    __tablename__= 'favorite_planets'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('userS.id'), nullable=False)
    users = db.relationship('UserS', back_populates='planet_favorite')

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    favorite_planets = db.relationship('Planets', back_populates='favorite_by')

    def __repr__(self):
        return f'User {self.user_id} likes planet {self.planet_id}'
    
    def serialize(self):
        return{
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.planet_id
        }

class Characters(db.Model):
    __tablename__= 'characters'
    id =db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(250), unique = True, nullable=False)
    gender =db.Column(db.String(250), nullable=False)
    species =db.Column(db.String(250), nullable=False)

    planet_id =db.Column(db.Integer, db.ForeignKey('planets.id'))
    starship_id =db.Column(db.Integer, db.ForeignKey('starships.id'))

    planet = db.relationship('Planets', back_populates='characters')
    starship = db.relationship('Starships', back_populates='characters')

    favorite_by = db.relationship('FavoriteCharacters', back_populates='favorite_characters')

    def __repr__(self):
        return f'Ch. {self.id} {self.name}'
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "species": self.species
        }

class Planets(db.Model):
    __tablename__= 'planets'
    id =db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(250), unique = True, nullable=False)
    climate =db.Column(db.String(250))    
    population =db.Column(db.Integer)

    characters = db.relationship('Characters', back_populates='planet')
    
    favorite_by = db.relationship('FavoritePlanets', back_populates='favorite_planets')

    def __repr__(self):
        return f'Planet {self.id} {self.name}'
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population
        }    
    
class Starships(db.Model):
    __tablename__= 'starships'
    id =db.Column(db.Integer, primary_key=True)
    name =db.Column(db.String(250), unique = True, nullable=False)
    passengers =db.Column(db.Integer)    
    lenght =db.Column(db.Float)

    characters = db.relationship('Characters', back_populates='starship')

    def __repr__(self):
        return f'Starship {self.id} {self.name}'

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "passengers": self.passengers,
            "lenght": self.lenght
        }     