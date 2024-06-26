# import libraries
import sqlite3
import requests
import os
import openai
from openai import OpenAI
import simplejson as json

def get_yelp(user_input):
    
    my_api_key = os.getenv('YELP_API_KEY')
    
    # for cities with more than one word like new york city
    if " " in user_input:
        split_input = (user_input.lower()).split() #["new", "york", "city"]
        formatted_location = "%20".join(split_input)
        print(formatted_location)
    else:
        # otherwise, one word cities are good
        formatted_location = user_input
        
    


    url = f"https://api.yelp.com/v3/businesses/search?location={formatted_location}&sort_by=best_match&limit=5"

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

            restaurantsDB.append(newDict)

    # Step 2: Connect to the SQLite3 database
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Step 3: Iterate over the JSON data and insert into the database
    for item in restaurantsDB:
        cursor.execute(
        """INSERT INTO Restaurants (Name, Location, Address) VALUES (?, ?, ?)
        """, (item['name'], item['location'], item['address']))
    conn.commit()
    # Step 4: Commit the transaction and close the connection

    # Query the database to check the stored data
    cursor.execute('SELECT * FROM Restaurants')
    rows = cursor.fetchall()

    # Print the stored data
    for row in rows:
        print(row)
    
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

    cursor.execute('SELECT Name, Location, Address FROM Restaurants')
    restaurants = cursor.fetchall()

    conn.close()
    return restaurants

# make the prompt to give to chatgpt
def make_prompt(user_name, user_location, restaurants):
    prompt = f"{user_name}is asking for restaurant recommendations around {user_location}. Here is a list of restaurants:\n"
    for name, location, address in restaurants:
        prompt += f"Name: {name}, Location: {location}, Address: {address}\n"
    prompt += "\nBased on this information, which 3 restaurants do you recommend for a great dining experience?"
    return prompt

def get_gpt_response(name, location):

    # Set environment variables
    my_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=my_api_key))

    # Fetch restaurant data from the database
    restaurants = get_restaurants()

    # Create a prompt using the fetched data
    prompt = make_prompt(name, location, restaurants)


    # Make a request to the OpenAI API
    gpt_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
        api_key=my_api_key
    )

    # Get the response text
    return gpt_response.choices[0].text.strip()




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
    

if __name__ == "__main__":
    
    is_valid_inputs = False

    # ask for user input
    user_name = input("Howdy! This is a restaurant recommender app for USA. Please enter your name or if you want to quit, enter quit: ")
    is_valid_name, user_name = validate_input(user_name)
    if is_valid_name and user_name.lower() != "quit":
        print(f"This is the chosen name: {user_name}")     
        user_city = input("Please enter a US city (e.g. New York City or NYC) or if you want to quit, enter quit: ")
        is_valid_city, user_city = validate_input(user_city)
        if is_valid_city and user_city.lower() != "quit":
            print(f"This is the chosen city: {user_city}")
            is_valid_inputs = True

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
            Address TEXT NOT NULL)""");

        con.commit()
        con.close()

        get_yelp(user_city)
        result = get_gpt_response(user_name, user_city)
        print(result)


    # validate input somewhere here
    
