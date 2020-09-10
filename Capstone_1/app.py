from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Drink, Recommendation, Ingredients, Favorite, Rating, Drinks_Ingredients
from functions import login, logout, get_fav_drink_dict, get_fav_drink_ingredients, get_drink_ingredients, get_count_dict, get_fav_ingredient
from forms import RegisterForm, LoginForm, RecommendForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
import random
KEY = "user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cocktails'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "secret"
# toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global."""

    if KEY in session:
        g.user = User.query.get(session[KEY])

    else:
        g.user = None

@app.route('/')
def home():
    """Shows top rated drinks up to 6 and fills remainder if there aren't 6 ratings in DB"""

    ratings = Rating.query.filter(Rating.rating > 0).order_by(Rating.rating.desc()).limit(6).all()
    all_drinks = Drink.query.all()

    drinks = []
    
    for rating in ratings:
        drink = Drink.query.get(rating.drink_id)
        drinks.append(drink)

    distinct_drinks = list(set(drinks))
    
    while len(distinct_drinks) < 6:
        rand_drink = random.choice(all_drinks)
        distinct_drinks.append(rand_drink)
        distinct_drinks = list(set(distinct_drinks))
    
    return render_template('home.html', distinct_drinks=distinct_drinks)

@app.route('/user/signup', methods=['GET','POST'])
def sign_up_page():
    """Registers user"""

    form = RegisterForm()

    if form.validate_on_submit():

        try:
            user = User.signup(
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form = form)

        db.session.add(user)
        db.session.commit()

        login(user)

        return redirect("/drinks/page1")

    else:

        return render_template('signup.html', form=form)

@app.route('/user/login', methods=['GET',"POST"])
def login_page():
    """Handle user login."""
    form = LoginForm()

    if form.validate_on_submit():
        print(form)
        print(form.data)
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/user/favorites")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)

@app.route('/user/logout')
def logout_user():
    """Handle user logout."""

    user_id = session[KEY]
    user = User.query.get(user_id)
    if user:
        logout()
        flash("Logout successful", "success")
        return redirect('/')

@app.route('/user', methods=['GET'])
def user():
    """Show user profile,shows random drinks if there are no favs or ratings
    shows top rated drinks in DB if no favs, and shows recommendations based on
    ingredient that appears most often in favs of user"""

    if 'user' not in session:
        flash('Please log in to access this page', 'danger')
        return redirect('/')
    else:
        user_id = session['user']
        favs = Favorite.query.filter(Favorite.user_id == user_id).all()
        ratings = Rating.query.all()

        if favs == [] and ratings == []:
            all_drinks = Drink.query.all()
            i=0
            rand_drinks = []
            while i < 6:
                rand_drink = random.choice(all_drinks)
                if rand_drink in rand_drinks:
                    continue
                else:
                    rand_drinks.append(rand_drink)
                    i += 1
            return render_template('user.html', drinks=rand_drinks, recommends=None, favs=None)
        
        if favs == []:
            ratings = Rating.query.filter(Rating.rating > 0).order_by(Rating.rating.desc()).limit(6).all()
            high_rated_drinks = []
            for rating in ratings:
                drink = Drink.query.filter(Drink.id == rating.drink_id).first()
                high_rated_drinks.append(drink)
                high_rated_drinks=list(set(high_rated_drinks))
            return render_template('user.html', ratings=high_rated_drinks, favs=None)


        else:

            drinks = get_fav_drink_dict(favs)
  
            drink_ingreds = get_fav_drink_ingredients(drinks)
            
            count_dict = get_count_dict(drink_ingreds)
            
            fav_ingredient_dict = get_fav_ingredient(count_dict)
            
            for key in fav_ingredient_dict:
                fav_ingredient = Ingredients.query.filter(Ingredients.name == key).first()

            if fav_ingredient is None:
                pass 
            else:  
                possible_recommends = Drinks_Ingredients.query.filter(Drinks_Ingredients.ingredient_id==fav_ingredient.id).all()
                drink_count = len(Drink.query.all())
                recommends_list = []
                j=0
                k=0
                while j < 6:
                    recommend = random.choice(possible_recommends)
                    possible_drink = Drink.query.get(recommend.drink_id)
                    if k > drink_count:
                        break
                    
                    for fav in favs:
                        if possible_drink.id == fav.drink_id or possible_drink in recommends_list:
                            k += 1
                            
                        else:
                            recommends_list.append(possible_drink)
                            j += 1
                
                return render_template('user.html', recommends=recommends_list, ratings=1, favs=1)

@app.route('/search')
def search():
    """Handles searches"""
    try:
        search = request.args['search']
        if search == "":
            flash("Please enter a drink in the search bar", 'danger')
            return redirect('/')
        else:
            drinks = Drink.query.filter(Drink.name.ilike(str(f'%{search}%'))).all()
            drink_ingreds = get_drink_ingredients(drinks)
                
            return render_template('search.html', drinks=drinks, drink_ingreds=drink_ingreds)

    except KeyError:
        flash("Please enter a drink in the search bar", 'danger')

    return render_template('search.html')

@app.route('/drinks/page<int:page_num>')
def show_drinks(page_num):
    """Shows all drinks in DB at 25 per page"""
    next_page = page_num+1
    previous_page = page_num-1

    if page_num == 1:
        drinks = Drink.query.filter(Drink.id>0).order_by(Drink.id).limit(25).all()
    else:
        drinks = Drink.query.filter(Drink.id>0).order_by(Drink.id).limit(25).offset(((page_num-1)*25)).all()
        if not drinks:
            flash("We're out of drinks!", 'danger')
            return redirect(f'/drinks/page{previous_page}')
    
    drink_ingreds = get_drink_ingredients(drinks)
    
    avg_ratings_dict = {}
    total = 0
    length = 0
    average = 0
    for drink in drinks:
        ratings = Rating.query.filter(Rating.drink_id==drink.id).all()
        if ratings ==[]:
            avg_ratings_dict[drink.id]= []
        else:
            for rating in ratings:
                total += rating.rating
                length += 1
            average = total/length
            avg_ratings_dict[drink.id]= average
            total = 0
            length = 0
    
    return render_template('drinks.html', page_num=page_num, drinks=drinks, drink_ingreds=drink_ingreds, next_page=next_page, previous_page=previous_page, avg_ratings_dict=avg_ratings_dict)

@app.route('/drinks/<int:drink_id>', methods=['GET', 'POST'])
def get_drink(drink_id):
    """Shows drink info page, handles creating/deleting ratings"""
    try:
        user_id = session['user']
    except KeyError:
        flash('Log in to rate/favorite drinks', 'warning')
        pass
    
    drink = Drink.query.get(drink_id)    

    if request.method == 'POST':
        rating = request.json['rating']
        if float(rating) < 0 or float(rating) > 5:
            flash('Please enter a rating between 0 and 5', 'danger')
            return redirect(f'/drinks/{drink_id}')

        rating_check = Rating.query.filter(Rating.user_id==user_id).filter(Rating.drink_id == drink_id).first()
        
        if rating_check is None:
            new_rating = Rating(rating=rating, user_id=user_id, drink_id=drink_id)
            db.session.add(new_rating)
            db.session.commit()
        else:
            update_rating = Rating.query.get(rating_check.id)
            update_rating.rating = rating
            db.session.commit()

        return redirect(f'/drinks/{drink_id}')
    else:
        
        drink = Drink.query.get(drink_id)
        if 'user' not in session:
            rating = None
            fav_check = None
        else:
            rating = Rating.query.filter(Rating.user_id==user_id).filter(Rating.drink_id == drink_id).first()
            fav_check = Favorite.query.filter(Favorite.drink_id == drink_id).filter(Favorite.user_id == user_id).first()
        
        ingredients = Drinks_Ingredients.query.filter(Drinks_Ingredients.drink_id == drink.id).all()
        names = []
        for ingredient in ingredients:
            ingredient_name = Ingredients.query.get(ingredient.ingredient_id)
            names.append(ingredient_name)

        return render_template('drink.html', drink=drink, ingredients=ingredients, fav_check=fav_check, rating=rating, names=names)

@app.route('/user/favorites', methods=['GET', 'POST'])
def get_favs():
    """Shows favorites page, handles creating/deleting of favorites"""
    try:
        user_id = session['user']
    except KeyError:
        flash('Log in to rate/favorite drinks', 'warning')
        return redirect('/')
    
    if request.method == 'POST':
        drink_id = request.json['drinkId']
        
        fav_check = Favorite.query.filter(Favorite.drink_id==drink_id).filter(Favorite.user_id == user_id).first()
        if fav_check is None:
            new_fav = Favorite(user_id=user_id, drink_id=drink_id)
            db.session.add(new_fav)
            db.session.commit()

            favs = Favorite.query.filter(Favorite.user_id==user_id).all()
            drinks = get_fav_drink_dict(favs)
            drink_ingreds = get_fav_drink_ingredients(drinks)
        
        else:
            delete_fav = Favorite.query.get(fav_check.id)
            db.session.delete(delete_fav)
            db.session.commit()

            favs = Favorite.query.filter(Favorite.user_id==user_id).all()
            drinks = get_fav_drink_dict(favs)
            drink_ingreds = get_fav_drink_ingredients(drinks)
        
        return render_template('favorite.html', drinks=drinks, drink_ingreds=drink_ingreds)
            
    else:
        
        favs = Favorite.query.filter(Favorite.user_id==user_id).all()
        drinks = get_fav_drink_dict(favs)
        drink_ingreds = get_fav_drink_ingredients(drinks)
        
        return render_template('favorite.html', drinks=drinks, drink_ingreds=drink_ingreds)

@app.route('/user/recommend/form<int:drink_id>', methods=['GET', 'POST'])
def recommend_form(drink_id):
    """Show form for posting recommendations, creates new recommendations from POST"""

    if 'user' not in session:
        flash('Please log in or sign up to send recommendations', 'danger')
        return redirect('/')

    form = RecommendForm()

    user_id = session['user']
    user = User.query.get(user_id)
    drink = Drink.query.get(drink_id)

    form = RecommendForm()
    form.recommend_to_name.choices = [(user.id,user.username) for user in User.query.filter(User.id !=user_id).all()]
    form.username.data = user.username
    form.drink.data = drink.name

    if request.method == 'POST':

        username = form.username.data
        recommend_to_id = form.recommend_to_name.data
        drink = form.drink.data

        user = User.query.filter(User.username==username).first()
        drink = Drink.query.filter(Drink.name==drink).first()

        new_recommend = Recommendation(recommender_id=user.id, recommend_to_user_id=recommend_to_id,drink_id=drink.id)
        db.session.add(new_recommend)
        db.session.commit()

        return redirect('/user/favorites')

    else:
    
        return render_template('form.html', form=form, drink_id=drink_id)

@app.route('/user/recommendations', methods=["GET", 'POST'])
def show_recommendations():
    """Show recommendations handles deleting recommendations"""

    if 'user' not in session:
        flash('Please log in or sign up to get recommendations', 'danger')
        return redirect('/')
    
    user_id = session['user']

    if request.method == 'POST':
        rec_id = request.json['recId']
        
        rec_to_delete = Recommendation.query.get(rec_id)

        db.session.delete(rec_to_delete)
        db.session.commit()

        return redirect('/user/recommendations')

    drinks = {}
    recommenders = {}

    recommends = Recommendation.query.filter(Recommendation.recommend_to_user_id==user_id).all()
    for recommend in recommends:
        drink = Drink.query.filter(Drink.id==recommend.drink_id).first()
        drinks[recommend.recommender_id]=drink

        recommender = User.query.filter(User.id==recommend.recommender_id).first()
        recommenders[recommender.id]=recommender.username

    return render_template('recommend.html', drinks=drinks, recommenders=recommenders, recommends=recommends)