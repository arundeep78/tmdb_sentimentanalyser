"""
Helper functions to get information from TMDB API
  
"""
import os
import requests
import json
import pandas as pd
import numpy as np


tmdb_url = "https://api.themoviedb.org/3"

api_key = "f78ae83838fa87074abc367e0e58fdc0"


def get_daily_pop_movies(api_key:str, page_limit:int=5):
  """
  get popular movies from the TMDB using standard API

  Inputs:
    api_key (str): api key for TMDB api
    page_limit (page_limit, optional): number of pages to download. Default: 20
  output:
    dataframe: pandas dataframe with basic information returned by the api
  """
  pop_movie_path = "/movie/popular"

  url = tmdb_url + pop_movie_path

  params = {
    "api_key" : api_key,
    "language": "en-US",
    "page" : 1
    }

  res= requests.get(url,params= params)

  movies = json.loads(res.text)
  
  # find total number of pages
  total_pages = movies['total_pages']
  
  total_pages = np.minimum(page_limit, total_pages)

  movie_df = pd.DataFrame(movies['results'])

  # get all additional  pages if any exists and append to the DataFrame
  for page in range(2,total_pages):
    
    params['page'] = page
    res = requests.get(url, params=params)
    movies = json.loads(res.text)
 
    cur_page_movies_df = pd.DataFrame(movies['results'])
  
    movie_df = pd.concat([movie_df , cur_page_movies_df ], ignore_index= True)
    # movie_df.append(cur_page_movies_df,ignore_index= True)


  genre_dict = get_movie_genres(api_key)

  movie_df['genre_names'] = movie_df['genre_ids']\
                            .apply(lambda ids : ", ".join([genre_dict.get(id,"") for id in ids]))

  return movie_df


# genre

def get_movie_genres(api_key:str):
  """
  get a dictionary of movie genres id:name mapping from TMDB

  Inputs:
    api_key (str) : API key for TMDB api
  Returns:
      dict: Dictionary of id:name for genre id and genre name for movies
  """
  genre_path = "/genre/movie/list"

  url = tmdb_url + genre_path

  params = {
    "api_key" : api_key,
    "language": "en-US"
    }

  res = requests.get(url,params=params)

  genres = json.loads(res.text)

  genres_df = pd.json_normalize(genres['genres'])

  # return dictionary of genres with id:name
  return genres_df.set_index("id").to_dict()["name"]


# actor

def get_movie_credits(m_id:int, api_key:str):
  """
  Get casting and crew details of a movie from TMDB and returns the informaton as separate dataframes

  Args:
      m_id (int): TMDB movie ID
      api_key (str) : API key for TMDB api

  Returns:
      (DataFrame, DataFrame): returns a tuple of cast and cre information
  """
  crew_url = "/movie/{}/credits"

  url = tmdb_url + crew_url

  params = {
    "api_key" : api_key,
    "language": "en-US"
    }

  url = url.format(m_id)

  res = requests.get(url, params= params)

  if not res.ok:
    return None, None
    
  m_credits = json.loads(res.text)

  # separate the json into two separate Dataframes
  cast_df = pd.DataFrame(m_credits['cast'])

  crew_df = pd.DataFrame(m_credits['crew'])

  return cast_df, crew_df


# reviews

def get_movie_reviews(m_id:int, api_key:str):
  """
  Get reviews of the movies from TMDB and return s dataframe

  Input:
    m_id(int) : TMDB Movie id
    api_key (str) : TMDB api key

  Output:
    Dataframe: Dataframe with all the reviews of the movie
  """

  review_path = "/movie/{}/reviews"

  url = tmdb_url + review_path

  url = url.format(m_id)

  params = {
    "api_key" : api_key,
    "language": "en-US",
    "page" : 1
    }


  res = requests.get(url, params=params)
  
  if not res.ok:
    return None

  reviews = json.loads(res.text)

  # find total number of pages
  total_pages = reviews['total_pages']
  # return reviews['total_pages'],reviews['total_results']
  
  reviews_df = pd.json_normalize(reviews['results'])

  # print(f'total pages : {total_pages}')

  # get all additional  pages if any exists and append to the DataFrame
  for page in range(2,total_pages):
    
    params['page'] = page
    res = requests.get(url, params=params)
    reviews = json.loads(res.text)
 
    cur_page_reviews_df = pd.json_normalize(reviews['results'])
  
    reviews_df.append(cur_page_reviews_df,ignore_index= True)

  # update column names to convert to snake case
  reviews_df.columns = [c.replace('.','_') for c in reviews_df.columns]
  
  return reviews_df


