import requests
import os
import simplejson as json
import sqlite3

# Replace 'YOUR_API_KEY' with your actual Yelp Fusion API key
my_api_key = os.getenv('YELP_API_KEY')

# Define the endpoint

# Define the headers, including the authorization header with your API key

# ask for user location, insert that location into url
# format the user string to satisfy the url (can make it into a function)
url = "https://api.yelp.com/v3/businesses/search?location=new%20york%20city&sort_by=best_match&limit=2"

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


"""restaurantsDB = []
#data["businesses"]
for key, value in data.items():
    #print(f"Key is: {key}")
    if key == "businesses":
        newDict = {}
        for items in value:
            for item in items:
                if item == "name":
                    newDict[item] = items[item]
                    #print(items[item])
                    #print(newDict)
                if item == "price":
                    print(items[item])
                if item == "categories":
                    print(items[item][0]["title"])
                if item == "rating":
                    print(items[item])
                if item == "location":
                    newDict[item] = items[item]["city"]
                    newDict["address"] = items[item]['display_address'][0] + ", " + items[item]['display_address'][1]
                    #print(f"{items[item]['display_address'][0]}, {items[item]['display_address'][1]}")
        print(newDict)
        restaurantsDB.append(newDict)      
            

print(restaurantsDB)"""
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

#print(restaurantsDB)

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

#print(response.text)
