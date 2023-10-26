from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
import re
import string

app = Flask(__name__, template_folder='templates')


# Load your data and perform data preprocessing here
# Load your data
df = pd.read_csv('data1.csv')  # Load your food data
ratings = pd.read_csv('ratings.csv')  # Load user ratings data
# ...
# No of dishes in my dataset
len(list(df['Name'].unique()))

df['C_Type'].unique()  # Categorical Data

df['Veg_Non'].unique()  # Categorical Data

len(df)

df.shape

df.info()

# function to remove all the punctuation from the "Describe" column


def text_cleaning(text):
    text = "".join([char for char in text if char not in string.punctuation])
    return text


# clean the text
df['Describe'] = df['Describe'].apply(text_cleaning)

# see if that worked...
df.head()

# Are there any duplicate data ?
df.duplicated().sum()
# None :)

# Are there any null values?
df.isnull().sum()
# None :))

# General Description
df.describe()
csr_rating_matrix = None

# Content-Based Filtering
# Update the 'content' column to include the 'Diabetic_Friendly' feature


def create_soup(x):
    diabetic_friendly = x['Diabetic_Friendly']
    if isinstance(diabetic_friendly, str):
        return x['C_Type'] + " " + x['Veg_Non'] + " " + x['Describe'] + " " + diabetic_friendly
    else:
        return x['C_Type'] + " " + x['Veg_Non'] + " " + x['Describe']


# Using the soup(), create the column for the dataframe df
df['soup'] = df.apply(create_soup, axis=1)

# Initialize Count Vectorizer
count = CountVectorizer(stop_words='english')

# Fit and transform the Count Vectorizer on the 'soup' column
count_matrix = count.fit_transform(df['soup'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

# Reset the index and pull out the names of the food alone from the df dataframe
df = df.reset_index()
indices = pd.Series(df.index, index=df['Name'])

# The main recommender code!


def get_recommendations_advanced(title, cosine_sim=cosine_sim2):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 5 most similar food
    sim_scores = sim_scores[1:6]

    food_indices = [i[0] for i in sim_scores]
    # Filter recommendations for diabetic-friendly items
    recommended_foods = df.iloc[food_indices]
    recommended_foods = recommended_foods[recommended_foods['Diabetic_Friendly'] == 1]

    return recommended_foods[['Name', 'Diabetic_Friendly']]


# Collaborative Filtering
# Checking the shape
ratings.shape

# Checking for null values
ratings.isnull().sum()

ratings.tail()

# Removing the last row
ratings = ratings[:511]
ratings.tail()

# So, now there should not be any null value
ratings.isnull().sum()

# Making a dataframe that has food ID and the number of ratings
food_rating = ratings.groupby(by='Food_ID').count()
food_rating = food_rating['Rating'].reset_index().rename(
    columns={'Rating': 'Rating_count'})

# ...

# Create the rating_matrix from the 'rating' DataFrame
rating_matrix = ratings.pivot_table(
    index='Food_ID', columns='User_ID', values='Rating').fillna(0)

# Now you can use 'rating_matrix' in your recommender model
csr_rating_matrix = csr_matrix(rating_matrix.values)
recommender = NearestNeighbors(metric='cosine')
recommender.fit(csr_rating_matrix)


def simple_search(query, food_list):
    matching_foods = [
        food for food in food_list if query.lower() in food.lower()]
    return matching_foods


# Example usage:
all_foods = ["Chicken Curry", "Spaghetti Carbonara",
             "Vegetable Stir-Fry", "Chocolate Cake", "Salmon Sushi"]
user_query = "chicken"

matching_foods = simple_search(user_query, all_foods)
print(matching_foods)


# The main recommender code!
def Get_Recommendations(title):
    print('DF:', df['Food_ID'])
    user = df[df['Name'] == title]
    print('INT:', user['Food_ID'])
    user_index = np.where(ratings.index == int(user['Food_ID']))[0][0]
    user_ratings = csr_rating_matrix[user_index]

    reshaped = user_ratings.toarray().reshape(1, -1)
    distances, indices = recommender.kneighbors(reshaped, n_neighbors=16)

    nearest_neighbors_indices = ratings.iloc[indices[0]].index[1:]
    nearest_neighbors = pd.DataFrame({'Food_ID': nearest_neighbors_indices})

    result = pd.merge(nearest_neighbors, df, on='Food_ID', how='left')

    # Filter recommendations for diabetic-friendly items
    # Assuming 1 indicates diabetic-friendly items
    result = result[result['Diabetic_Friendly'] == 1]

    return result.head()


@app.get('/food-suggestions')
def food_suggestions():
    query = request.args.get('query', '').strip()
    page = request.args.get('page', default=1, type=int)
    items_per_page = 10  # Set the number of items to display per page

    # Query your database or food list to find matching food items using the simple_search function
    # Replace all_foods with your list of food items
    matching_foods = simple_search(query, all_foods)

    # Calculate the start and end indices for the current page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    # Get the food items for the current page
    current_page_foods = matching_foods[start_index:end_index]

    # Calculate the total number of pages
    total_pages = (len(matching_foods) + items_per_page - 1) // items_per_page

    # Create a dictionary to hold the pagination information and results
    result = {
        "page": page,
        "total_pages": total_pages,
        "current_page_foods": current_page_foods
    }

    return jsonify(result)

# Define your API endpoints


@app.post('/content-based-recommendation')
def content_based_recommendation_api():
    data = request.get_json()
    food_name = data.get('food_name')

    recommendations = get_recommendations_advanced(food_name, cosine_sim2)

    return jsonify(recommendations.to_dict(orient='records'))


@app.post('/collaborative-filtering-recommendation')
def collaborative_filtering_recommendation_api():
    data = request.get_json()
    food_name = data.get('food_name')

    recommendations = Get_Recommendations(food_name)

    return jsonify(recommendations.to_dict(orient='records'))


@app.route('/meal_plan_display')
def display_meal_plan():
    # You can pass any necessary data to your template here
    return render_template('meal_plan_display.html')


@app.get('/food-names')
def get_food_names():
    food_names = df['Name']
    return {
        'names': food_names.tolist(),
        'status': 'Food Names'
    }


# app routes
@app.route('/')
def home():
    return render_template('home.html')


# @app.route('/plan-meal')
# def plan_meal():
#     return render_template('meal_plan_display.html')

@app.route('/food')
def food():
    return render_template('food.html')


@app.route('/additional')
def additional():
    return render_template('addition.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
