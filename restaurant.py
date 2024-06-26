# import libraries
import sqlite3
"""
pseudocode

Program should continue running until user enters quit or exit, let them continually respond with a location

first, make database

create database name
create table users (primary email address TEXT, first and last names TEXT, location text, extra - preferences JSONB)
create table restaurants (primary id int, secondary location TEXT, name text, address text)
test if database exists/was actually made

second, load up yelp api data into restaurants table

since yelp api returns a json file, use for loop or other methods to put data into restaurants table
test to see if restaurants table was properly populated

third, ask user input and store it in database, check if the data went in the database

In python - ask user input, validate user input, once validated we store in database
can test if stuff actually went in there

fourth, retrieve the data from user table and restaurant table to give to chatGPT

chatGPT says "here's the top five restuarants in that {location}: name, address name, price level, attributes (hot & new stuff, deals)"
check if chatGPT actually got the information from the tables, was it able to access it

check if the while loop for user input continues to run well without breaking the other parts of program

"""

# setting up database
db_name = "restaurant.db"
con = sqlite3.connect(db_name)
cur = con.cursor()

# location is technically city
cur.execute("""CREATE TABLE IF NOT EXISTS Restaurants
    (restaurantID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
    Name TEXT NOT NULL, 
    Location TEXT NOT NULL, 
    Address TEXT NOT NULL,)""");

# Create an index on the Location column (this technically creates a secondary key)
cur.execute("CREATE INDEX IF NOT EXISTS idx_location ON Restaurants(Location)")

con.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS Users
    (email TEXT NOT NULL PRIMARY KEY, 
    fName TEXT NOT NULL,
    lName TEXT NOT NULL, 
    Location TEXT NOT NULL)""");
    
con.commit()

# check if tables are in database -- yes!
for row in con.execute("""SELECT name FROM sqlite_master"""):
    print(row)



    


# ask user input (ONLY ASK FOR CITIES)
#user_location = input("Howdy! This is a restaurant finder. Please enter your city (e.g. New York City or NYC): ")
# validate input later

# give input to openAI chatgpt