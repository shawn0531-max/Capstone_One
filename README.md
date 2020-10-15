# Cocktail Connection
Link to site - https://cocktail-connection.herokuapp.com/  

API link - https://www.thecocktaildb.com/api.php  

Search for different cocktails and learn how to make them. Users can add to  
a personal favorites list, rate drinks, send recommendations to other users, and  
receive recommendations based on ingredients in their favorite drinks.  

## Setup  

To run locally:  
- Clone the github repository  
- pip install -r requirements.txt  
- create a database for the seed file to place the data  
- python seed.py


##Features  
- **Search** - A search input available to all users to make finding a specific drink easier.  
- **Site Recommended Drinks** - Implemented in multiple ways dependent on user status, ratings and favorites.  
	- _User not logged in_: Homepage shows 6 random drinks  
	- _Logged in without favorites_: Profile page shows top 6 rated drinks, if no ratings fills remaining spots with random drinks.  
	- _Logged in with favorites_: Profile page shows 6 drinks with the most common ingredient among that user's favorites.  
- **Favorites** - Logged in users can add/remove any drinks to their own favorites list for easy viewing  
- **Ratings** - Logged in users can rate any drink (0 to 5 in 0.5 increments)  
- **User Recommendations** - Logged in users can send drink recommendations to other users in the database  

##User Flow  
The home page consists of 6 drinks from the database which the user can click on to receive information about ingredients and their measurements to make the drink. There is also a search bar for if the user already has a specific drink in mind as well as a drinks link in the navigation bar to view all the drinks available. Users will need to login/register in order to set favorites, rate drinks, and send drink recommendations to other users. Once logged in users will have access to their favorites page, profile page, and recommendations page. From the user's favorites page they will have access to a list of favorites as well as a carousel display flipping through all the favorites. They can also send recommendations from here. The profile page will show site recommended drinks based on criteria listed in features section. The recommendations page will show all drinks recommended by other users to the current user. 

##Technologies  
- HTML
- Jinja
- CSS
- Bootstrap
- JavaScript
- jQuery
- Python
- Flask
- sqlalchemy
- WTForms
- Postgres