"""Models for Cocktail Connection app."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.model):
    """Users"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True, unique = True)
    username = db.Column(db.String(25), nullable = False, unique = True)
    f_name = db.Column(db.String(20), nullable = False)
    l_name = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Drink(db.model):
    """Drinks"""

    __tablename__ = 'drinks'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True, unique = True)
    name = db.Column(db.String(25), nullable = False, unique = True)
    content = db.Column(db.String, nullable = False) #alcoholic vs non-alcoholic
    instructions = db.Column(db.Text, nullable = False)
    image = db.Column(db.String)
    ingredients = db.Column(db.Text, nullable = False)
    in_amount = db.Column(db.String, nullable = False)
    glass = db.Column(db.String)
    drink_type = db.Column(db.String)

class Recommendation(db.model):
    """Recommendations"""

    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True, unique = True)
    info = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'cascade'))
    drink_id = db.Column(db.Integer, db.ForeignKey('drinks.id', ondelete = 'cascade'), unique = True)
    # ? recommend_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'cascade'))
    # ? timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utc.now())

class Favorite(db.model):
    """Favorites"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True, unique = True)
    rating = db.Column(db.Decimal, precision = 1, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'cascade'))
    drink_id = db.Column(db.Integer, db.ForeignKey('drinks.id', ondelete = 'cascade'), unique = True)