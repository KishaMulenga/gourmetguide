import requests
import os
import simplejson as json
import sqlite3

# Replace 'YOUR_API_KEY' with your actual Yelp Fusion API key


# Define the endpoint

# Define the headers, including the authorization header with your API key

# ask for user location, insert that location into url
# format the user string to satisfy the url (can make it into a function)

def get_yelp(user_input):
    
    my_api_key = os.getenv('YELP_API_KEY')

    # for cities with more than one word like new york city
    if " " in user_input:
        split_input = (user_input.lower()).split() #["new", "york", "city"]
        formatted_location = "%20".join(split_input)
        print(formatted_location)
        
    # otherwise, one word cities are good


    url = f"https://api.yelp.com/v3/businesses/search?location={formatted_location}&sort_by=best_match&limit=2"

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
    conn = sqlite3.connect('restaurants.db')
    cursor = conn.cursor()

    # Delete all rows from the table
    cursor.execute('DELETE FROM Restaurants')

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()
