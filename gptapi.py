import os 
import openai
from openai import OpenAI
import sqlite3


# fetch all data from restaurants database
def get_restaurants():

    conn = sqlite3.connect("restaurants.db")
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
    prompt += "\nBased on this information, which 5 restaurants do you recommend for a great dining experience?"
    return prompt

# Connect to chatgpt api

def get_gpt_response():

    # Set environment variables
    my_api_key = os.getenv('OPENAI_API_KEY')

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


# Create an OpenAPI client using the key from our environment variable
client = OpenAI(
    api_key=my_api_key,
)

# Specify the model to use and the messages to send
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a university instructor and can explain programming concepts clearly in a few words."},
        {"role": "user", "content": "What are the advantages of pair programming?"}
    ]
)
print(completion.choices[0].message.content) 