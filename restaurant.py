# import libraries
import sqlite3
import requests
import os
import openai
from openai import OpenAI
import simplejson as json
import re

def get_yelp(user_input, category, price):
    
    my_api_key = os.getenv('YELP_API_KEY')
    
    # for cities with more than one word like new york city
    if " " in user_input:
        split_input = (user_input.lower()).split() #["new", "york", "city"]
        formatted_location = "%20".join(split_input)
    else:
        # otherwise, one word cities are good
        formatted_location = user_input
        
    # give user choice to pick a cuisine and price level
    # 10. United States · 9. Mexico · 8. Thailand · 7. Greece · 6. India · 5. Japan · 4. Spain · 3. France. 2. China, 1. Italy
    # price level - 1, 2, 3, 4
    category = category.lower()
    url = f"https://api.yelp.com/v3/businesses/search?location={formatted_location}&categories={category}&price={price}&sort_by=best_match&limit=20"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {my_api_key}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    # pretty print json file, then parse json file
    # name, categories, rating, pricing, location[display address]
    #pretty_response = json.dumps(data["businesses"], indent=4)
    #print("Pretty-printed JSON response:\n", pretty_response)

    restaurantsDB = []
    if "businesses" in data:
        for business in data["businesses"]:
            newDict = {}
            if "name" in business:
                newDict["name"] = business["name"]
            if "location" in business:
                newDict["location"] = business["location"]["city"]
                newDict["address"] = business["location"]['display_address'][0] + ", " + business["location"]['display_address'][1]
            if "categories" in business:
                newDict["categories"] = business["categories"][0]["title"]
            if "price" in business:
                newDict["price"] = business["price"]
            restaurantsDB.append(newDict)

    # Step 2: Connect to the SQLite3 database
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Step 3: Iterate over the JSON data and insert into the database
    for item in restaurantsDB:
        cursor.execute(
        """INSERT INTO Restaurants (Name, Location, Address, Category, Price) VALUES (?, ?, ?, ?, ?)
        """, (item['name'], item['location'], item['address'], item['categories'], item['price']))
    conn.commit()
    # Step 4: Commit the transaction and close the connection

    # Query the database to check the stored data
    cursor.execute('SELECT * FROM Restaurants')
    rows = cursor.fetchall()
    
    conn.close()


def deleteRows():
    # DELETING ROWS

    # Connect to SQLite database
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Delete all rows from the table
    cursor.execute('DELETE FROM Restaurants')

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

# fetch all data from restaurants database
def get_restaurants():

    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()

    cursor.execute('SELECT Name, Location, Address, Category, Price FROM Restaurants')
    restaurants = cursor.fetchall()

    conn.close()
    return restaurants

# make the prompt to give to chatgpt
def make_prompt(user_name, user_location, restaurants):
    user_prompt = f"I, {user_name}, am asking for restaurant recommendations around {user_location}. "
    user_prompt += "Which 3 restaurants do you recommend for a great dining experience? For each recommended, give me a short pitch (1-2 sentences) on why I should go there. "
    user_prompt += "Please list the restaurant name, location, address, category, and price level."
    user_prompt += "If there is none there, please say so."
    gpt_prompt = "You are a restaurant finder system. Here is a list of restaurants:\n"
    for name, location, address, category, price in restaurants:
        gpt_prompt += f"Name: {name}, Location: {location}, Address: {address}, Category: {category}, Price level: {price}\n"
    
    return user_prompt, gpt_prompt

def get_gpt_response(name, location, email):

    # Set environment variables
    my_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=my_api_key)

    # Fetch restaurant data from the database
    restaurants = get_restaurants()

    # Create a prompt using the fetched data
    user_prompt, gpt_prompt = make_prompt(name, location, restaurants)

    print("\nPlease wait a moment for our response...\n")
    # ask chatgpt for a response
    gpt_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": gpt_prompt},
        {"role": "user", "content": user_prompt},
    ],
    temperature=0,)


    # Get the response text
    response_text = gpt_response.choices[0].message.content
    print(response_text)

    # parse chatgpt code and ask user what they want, validate it, and return choice
    restaurant_names = re.findall(r'\d+\.\s+([^\n]+)', response_text)

    user_favorite = input("\nOut of these restaurants, pick one to save as your favorite (enter a number 1-3): ")
    is_valid_fav, user_favorite = validate_user(user_favorite)
    
    if is_valid_fav:
        # access db
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute('''UPDATE Users SET Favorite = ? WHERE Email = ?''', (restaurant_names[int(user_favorite)-1],user_email,))
        con.commit()
        con.close()




def validate_input(user_input):
    invalid_input = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "@", "$", "&", "#", "*", ",", "/", "\\", "!"]
    is_valid = False  # Start with the assumption that the username might be invalid
    #valid_input = user_input
    while not is_valid:
        is_valid = True  # Assume the username is valid, will be disproved if condition fails
        for char in user_input:
            if char in invalid_input:
                is_valid = False
                user_input = input("Invalid input, please enter again: ")
                break  # Exit the for loop to re-check the new input

    return is_valid, user_input

def validate_price(price):
    is_valid = False
    while not is_valid:
        if price.isdigit() and int(price) in range(1, 5):
            is_valid = True
        else:
            price = input("Invalid input, please enter a number 1-4: ")
    
    return is_valid, price

def validate_category(category):
    is_valid = False
    while not is_valid:
        if category.lower() == "none" or (category.isdigit() and int(category) in range(1, 17)):
            is_valid = True
        else:
            category = input("Invalid input, please enter a number 1-16 or 'none': ")
    
    return is_valid, category
        
def validate_email(email):
    
    # Regular expression for validating an email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = False
    while not is_valid:
        # Use the re module to match the email against the regex
        if re.match(email_regex, email):
            is_valid = True
        else:
            email = input("Invalid email, please enter again: ")

    return is_valid, email

def validate_user(choice):
    is_valid = False
    while not is_valid:
        if choice.isdigit() and int(choice) in range(1,4):
            is_valid = True
        else:
            choice = input("Invalid choice, please enter a number 1-3: ")
    
    return is_valid, choice

def check_user_by_email(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Execute the query to find the user by email
    cursor.execute('''
    SELECT * FROM Users WHERE Email = ?
    ''', (email,))
    
    # Fetch the first result (if any)
    user = cursor.fetchone()
    if user is not None:
        cursor.execute('''SELECT Name FROM Users WHERE Email = ?''', (email,))
        name = cursor.fetchone()
        conn.close()

        return True, name[0]
    else:
        conn.close()
        return False, " "
    # Return True if user found, False otherwise
    
if __name__ == "__main__":
    
    is_valid_inputs = False
    categories = ["Italian", "Chinese", "Greek", "French", "Indian", 
                "Japanese", "Thai", "American", "Nigerian", "Carribean", "Spanish",
                "Mexican", "Korean", "African", "Middle Eastern", "British"]
    
    # ask for user input
    starting_prompt = input("Howdy! This is a restaurant recommender app. \n1. New User \n2. Returning User \n3. Quit\nEnter a number (1-3):")
    is_valid_choice, user_choice = validate_user(starting_prompt)

    if is_valid_choice and user_choice == "1":

        user_name = input("\nPlease enter your name: ")
        is_valid_name, user_name = validate_input(user_name)

        if is_valid_name:

            user_email = input("Please enter your email: ")
            is_valid_email, user_email = validate_email(user_email)

            if is_valid_email:
                print(f"\n{user_name}, let's start the search!")
                user_city = input("Please enter a city (e.g. Tokyo or NYC): ")
                is_valid_city, user_city = validate_input(user_city)
                if is_valid_city:

                    print("Choose from the categories below (enter the number i.e., 1 for Italian). Or enter none for no specific cuisine\n")

                    for i in range(len(categories)):
                        print(f"{i+1}. {categories[i]}")
                    
                    user_category = input("Chosen cuisine: ")
                    is_valid_category, user_category = validate_category(user_category)
                    
                    if is_valid_category and user_category.isdigit():
                        user_category = categories[int(user_category)-1]
                        user_price = input("\nChoose a Price level from below \n1. $ (budget)\n2. $$ (moderate)\n3. $$$ (expensive)\n4. $$$$ (luxury) \nEnter a number 1-4: ")
                        
                        is_valid_price, user_price = validate_price(user_price)
                        if is_valid_price:
                            is_valid_inputs = True

                    elif is_valid_category and user_category.lower() == "none":
                        user_price = input("\nChoose a Price level from below \n1. $ (budget)\n2. $$ (moderate)\n3. $$$ (expensive)\n4. $$$$ (luxury) \nEnter a number 1-4: ")
                        
                        is_valid_price, user_price = validate_price(user_price)
                        if is_valid_price:
                            is_valid_inputs = True
        
    elif is_valid_choice and user_choice == "2":
        user_email = input("Please enter your email: ")
        is_valid_email, user_email = validate_email(user_email)

        # check if user exists in db
        user_exists, user_name = check_user_by_email(user_email)

        if user_exists:
            print(f"\nWelcome back {user_name}! Let's start the search!")
            user_city = input("Please enter a city (e.g. Tokyo or NYC): ")
            is_valid_city, user_city = validate_input(user_city)
                
            if is_valid_city:

                print("Choose from the categories below (enter the number i.e., 1 for Italian). Or enter none for no specific cuisine\n")

                for i in range(len(categories)):
                    print(f"{i+1}. {categories[i]}")
                    
                user_category = input("Chosen cuisine: ")
                is_valid_category, user_category = validate_category(user_category)
                    
                if is_valid_category and user_category.isdigit():
                    user_category = categories[int(user_category)-1]
                    user_price = input("\nChoose a Price level from below \n1. $ (budget)\n2. $$ (moderate)\n3. $$$ (expensive)\n4. $$$$ (luxury) \nEnter a number 1-4: ")
                        
                    is_valid_price, user_price = validate_price(user_price)
                    if is_valid_price:
                        is_valid_inputs = True

                    elif is_valid_category and user_category.lower() == "none":
                        user_price = input("\nChoose a Price level from below \n1. $ (budget)\n2. $$ (moderate)\n3. $$$ (expensive)\n4. $$$$ (luxury) \nEnter a number 1-4: ")
                        
                        is_valid_price, user_price = validate_price(user_price)
                        if is_valid_price:
                            is_valid_inputs = True
    
    elif is_valid_choice and user_choice == "3":
        # otherwise quit if user choice is not 1 or 2
        print("Thank you for using our app!")


    if is_valid_inputs == True:
        # now begin starting yelp and chat gpt

        # setting up database
        db_name = "restaurant.db"
        con = sqlite3.connect(db_name)
        cur = con.cursor()

        # location is technically city
        cur.execute("""CREATE TABLE IF NOT EXISTS Restaurants
            (restaurantID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
            Name TEXT NOT NULL, 
            Location TEXT NOT NULL, 
            Address TEXT NOT NULL,
            Category TEXT NOT NULL,
            Price TEXT NOT NULL)""");
        con.commit()
        con.close()

        db_name = "users.db"
        con = sqlite3.connect(db_name)
        cur = con.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS Users 
            (userID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Favorite TEXT NOT NULL)""");

        cur.execute('''SELECT * FROM Users WHERE Email = ?''', (user_email,))
        existing_user = cur.fetchone()

        if not existing_user:
            cur.execute("""INSERT INTO Users (Name, Email, Favorite) VALUES (?, ?, ?)
            """, (user_name, user_email, "None"))
        else:
            cur.execute('''SELECT Name FROM Users WHERE Email = ?''', (user_email,))
            user_name = cur.fetchone()

        con.commit()
        con.close()

        get_yelp(user_city, user_category, user_price)
        get_gpt_response(user_name, user_city, user_email)
        
        ask_again = input("Would you like to search again? (enter yes or no) ") # should respond yes or no
        restart_loop = False
        is_valid_answer, ask_again = validate_input(ask_again)

        if is_valid_answer and ask_again.lower() == "yes":   
            restart_loop = True

        while restart_loop == True:
            deleteRows()  
            user_city = input("Please enter a city (e.g. Tokyo or NYC): ")
            is_valid_city, user_city = validate_input(user_city)
                
            if is_valid_city and user_city.lower():

                print("Choose from the categories below (enter the number i.e., 1 for Italian). Or enter 'none' for no specific cuisine")

                for i in range(len(categories)):
                    print(f"{i+1}. {categories[i]}")
                    
                user_category = input("Chosen cuisine: ")
                is_valid_category, user_category = validate_category(user_category)
                    
                if is_valid_category and user_category.isdigit():
                    user_category = categories[int(user_category)-1]
                    user_price = input("\nChoose a Price level from below \n1. $ (budget)\n2. $$ (moderate)\n3. $$$ (expensive)\n4. $$$$ (luxury) \nEnter a number 1-4: ")
                        
                    is_valid_price, user_price = validate_price(user_price)
                    if is_valid_price:
                        is_valid_inputs = True

                elif is_valid_category and user_category.lower() == "none":
                    user_price = input("\nChoose a Price level from below \n1. $ (budget)\n2. $$ (moderate)\n3. $$$ (expensive)\n4. $$$$ (luxury) \nEnter a number 1-4: ")
                        
                    is_valid_price, user_price = validate_price(user_price)
                    if is_valid_price:
                        is_valid_inputs = True

                
                get_yelp(user_city, user_category, user_price)
                get_gpt_response(user_name, user_city, user_email)

                ask_again = input("Would you like to search again? (enter yes or no) ") # should respond yes or no
                is_valid_answer, ask_again = validate_input(ask_again)
                
                # if yes clear favorite
                cursor.execute('''UPDATE Users SET Favorite = 'None' WHERE Email = ?''', (user_email,))

                if is_valid_answer and ask_again.lower() == "no":
                    restart_loop = False

    # validate input somewhere here
    
