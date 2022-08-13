"""
General purpose utilities package to help simplify common operations
"""

import io

from sqlalchemy import engine
from typing import List
from src import tmdbutils, nlp

import pandas as pd
import streamlit as st


M_CREW_TABLE = "t_tmdb_movie_crew"
M_CAST_TABLE = "t_tmdb_movie_cast"
MOVIE_TABLE = "t_tmdb_pop_movies"
M_REVIEW_TABLE = "t_tmdb_movie_review"

CSS_FILE = "./app/src/css/styles.css"

def update_tmdb_pop_movies_sentiments(con: engine, tmdb_key:str, thresh:float = .05, stwords:bool = True, hyperlinks:bool=True):
    """
    Updates daily list of popular movies from TMDB. 
    get additional information about the moview e.g. crew and cast.
    Get reviews of the movies. 
    perform sentiment analysis on the reviews.


    update Database with new information

    Inputs:
        con (sqlalchemy engine) : SQLAlchemy engine to the postgresql DB
        tmdb_key (str) : TMDB api key
        thresh (float, optional) : threshold value to classify for positive/negative sentiment. Defaults .05
          stwords (bool, optional): True to remove stop words before performing sentiment analysis. Default True
        hyperlinks(bool, optional): True to remove hyperlinks before performing sentiment analysis. Default: True
    Output:
        Dataframe: dataframe with movie id, name, director name, genre and overall ratio of positive sentiments 

    """

    # update daily popular movie DB with new list
    pop_movies_df = tmdbutils.get_daily_pop_movies(api_key=tmdb_key)


    # df_toPG(df=pop_movies_df, table_name=MOVIE_TABLE, con =con )
    pop_movies_df.to_sql(MOVIE_TABLE,con=con, index = False, if_exists= "replace")

    # Get additional details about movies i.e crew and cast details

    update_crew_cast(pop_movies_df['id'], con=con, tmdb_key=tmdb_key)

    #Get reviews for each movie and perform sentiment analysis of reviews before updating DB
    update_review_sentiments(m_ids = pop_movies_df['id'], 
                                con = con, 
                                tmdb_key = tmdb_key, 
                                thresh = thresh,
                                stwords= stwords,
                                hyperlinks= hyperlinks
                            )

def update_crew_cast(m_ids:List[int], con: engine, tmdb_key:str):
    """
    Update crew cast for list of movie ids in DB

    Args:
        m_ids (List(int)): List of movie Ids in TMDB 
        con (engine): SQLAlchemy engine
    """
    crew_list = []
    cast_list = []

    for m_id in m_ids:
        cast_df, crew_df = tmdbutils.get_movie_credits(m_id= m_id, api_key=tmdb_key)

        if (not crew_df is None) and len(crew_df) > 0:
        
            crew_df.insert(0, "m_id", m_id)
            crew_list.append(crew_df)
            
        if (not cast_df is None) and len(cast_df) > 0: 
            cast_df.insert(0, "m_id", m_id)
            cast_list.append(cast_df)

    # stack all crew and cast information in respective DF
    crews_df = pd.concat(crew_list,ignore_index= True)
    casts_df = pd.concat(cast_list, ignore_index= True)

    # update DB table with crew and cast info for popular movies
    # NOTE: current implementation is simplified to replace the whole table rather than to update the delta
    # as it is supposed to keep data only about the current popular movie list
    df_toPG(df=crews_df, table_name=M_CREW_TABLE, con =con )
    df_toPG(df=casts_df, table_name=M_CAST_TABLE, con =con )
 

def update_review_sentiments(m_ids:List(int), con: engine, tmdb_key:str, thresh: float = .05, stwords:bool = True, hyperlinks:bool=True):
    """
    update movie reviews and its sentiments for list of TMDB movie IDs.
    Store in DB

    NOTE: Current implentation updates complete table rather than adding delta

    Args:
        m_ids (List(int)): List of TMDB movie ids
        con (engine): SQl Alchemy engine to DB
        tmdb_key (str): TMDB api key
        thresh (float, optional): threshold to classify positive of negative sentiment. Defaults .05
          stwords (bool, optional): True to remove stop words before performing sentiment analysis. Default True
        hyperlinks(bool, optional): True to remove hyperlinks before performing sentiment analysis. Default: True

    """
    m_reviews_list = []
    # get reviews and perform sentiment analysis for each reivew
    for m_id in m_ids:

        m_reviews_df = tmdbutils.get_movie_reviews(m_id= m_id, api_key = tmdb_key)
        
        if (m_reviews_df is None) or len(m_reviews_df) == 0:
            continue

        # add movie id to Dataframe
        m_reviews_df.insert(0,"m_id",m_id)
        
        # perform sentiment analysis and add it to the Dataframe
        m_reviews_df['sentiment'] = m_reviews_df['content'].apply(nlp.get_vsa_value, 
                                                thresh = thresh,
                                                stwords= stwords,
                                                hyperlinks= hyperlinks
                                            )

        m_reviews_list.append(m_reviews_df)

    # stack all reviews in single DF
    movies_reviews_df = pd.concat(m_reviews_list, ignore_index=True)

    # movies_reviews_df['content'] = movies_reviews_df['content'].replace("\n","")
    
    # update DB table with crew and cast info for popular movies

    # NOTE: current implementation is simplified to replace the whole table rather than to update the delta
    # as it is supposed to keep data only about the current popular movie list
    movies_reviews_df.to_sql(name=M_REVIEW_TABLE, con =con, if_exists= 'replace', index =False )
    

    return movies_reviews_df


def update_sentiments(con: engine, thresh: float = .05, stwords:bool = True, hyperlinks:bool=True):
    """
    update sentiments of movie reviews for all movies in DB.
   
    NOTE: Current implentation updates complete table rather than adding delta

    Args:
        con (engine): SQl Alchemy engine to DB
        thresh (float, optional): threshold to classify positive of negative sentiment. Defaults .05
        stwords (bool, optional): True to remove stop words before performing sentiment analysis. Default True
        hyperlinks(bool, optional): True to remove hyperlinks before performing sentiment analysis. Default: True
    """
    # read existing data
    m_reviews_df = pd.read_sql(M_REVIEW_TABLE, con = con)
    
        
    # perform sentiment analysis and add it to the Dataframe
    m_reviews_df['sentiment'] = m_reviews_df['content'].apply(nlp.get_vsa_value, 
                                                            thresh = thresh, 
                                                            stwords =stwords,
                                                            hyperlinks = hyperlinks
                                                        )
    
    # update DB table with crew and cast info for popular movies

    # NOTE: current implementation is simplified to replace the whole table rather than to update the delta
    # as it is supposed to keep data only about the current popular movie list
    m_reviews_df.to_sql(name=M_REVIEW_TABLE, con =con, if_exists= 'replace', index =False )
    

    # return m_reviews_df

def get_movies_overview(con: engine):
    """
    Get overview information about daily popular movies and return as DataFrame

    Args:
        con (engine):SQLAlchemy engine
    
    Returns:
        Dataframe: Dataframe with movie basic information and overal positive sentiment %age based on review sentiment analysis,
        int: Total number of movies
    """

    ovr_stmt = f"""select ttpm.id, 
                        ttpm.title, 
                        ttpm.release_date,
                        ttmc."name" as "director",
                        ttmc2."name" as "lead_Actor",
                        ttpm.genre_names as genre
            from {MOVIE_TABLE} ttpm 
            join {M_CREW_TABLE} ttmc   on 
                ttpm .id = ttmc.m_id 
            join  {M_CAST_TABLE} ttmc2 on
                ttmc2.m_id = ttpm.id
            where 
                ttmc.job = 'Director' and 
                ttmc2."order" = '1'
            """

    m_overview_df = pd.read_sql(ovr_stmt, con=con)

    
    m_overview_df = m_overview_df.drop_duplicates(subset="id")

    
    # Get overall review of listed movies    
    review_stmt = f"""select ttmr.m_id, ttmr.sentiment  from {M_REVIEW_TABLE} ttmr
                    where ttmr.m_id in {tuple(m_overview_df['id'].tolist())} 
                """

    m_reviews_df = pd.read_sql(review_stmt, con= con)

    
    m_reviews_df = m_reviews_df.replace(
                            to_replace={"sentiment":{
                                                    1:"pos",
                                                    0: "neu", 
                                                    -1: "neg"}
                                            }
                                        )

    m_reviews_df = m_reviews_df.value_counts().unstack(fill_value=0)
    
    m_reviews_df['sentiment'] = m_reviews_df.apply(lambda row: f"{row['pos']/row.sum()*100:.2f} % +", axis=1)

    # Merge overview movies with overall movie sentiment rating
    m_reviews_df = m_overview_df.merge(
                        m_reviews_df['sentiment'],
                        left_on= "id",
                        right_index= True
                        )

    m_reviews_df = m_reviews_df.reset_index(drop= True)

    return m_reviews_df, len(m_overview_df)


def get_movie_reviews(m_id: int, con: engine):
    """
    Fetches reviews from the database and returns a DataFrame with movie reviews and respective sentiment.

    Args:
        m_id (int): TMDB movie ID
        con (engine): SQLAlchemy engine with DB details
    """

    review_stmt = f"""select ttmr.created_at,
                            ttmr.author_details_username as user, 
                            ttmr."content" as review, 
                            ttmr.sentiment  
                    from {M_REVIEW_TABLE} ttmr
                where m_id = '{m_id}'
                """
    
    m_reviews_df = pd.read_sql(review_stmt, con= con)

    m_reviews_df['created_at'] = pd.to_datetime(m_reviews_df['created_at']).dt.date

    m_reviews_df = m_reviews_df.replace(
                            to_replace={"sentiment":{
                                                    1:"positive",
                                                    0: "neutral", 
                                                    -1: "negative"}
                                            }
                                        )

    return m_reviews_df


def get_movie_img_url(m_id:int, con: engine, orig:bool = False):
    """
    Returns URL for poster image for the TMDB movie given it's ID

    Args:
        m_id (int): TMDB movie ID
        con (engine): SQLAlchemy engine
        orig (bool, optional): To return original resolution or scaled version. Default : False
    """

    stmt = f"""select ttpm.poster_path  from {MOVIE_TABLE} ttpm 
            where ttpm.id = {m_id} 
        """

    tmdb_img_host = "https://image.tmdb.org/t/p/"
    
    try:
        image_name= con.execute(stmt).fetchone()[0]

    # else returns TMDB logo
    except:
        url = "https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.svg"
        return url

    location = "original"
    if not orig:
        location = "w600_and_h900_bestv2"

    url = f"{tmdb_img_host}{location}{image_name}"

    return url





def df_toPG(df, table_name, con,if_exists='replace', sep='\t', index= False,dtypes= None , encoding='utf-8'):
    """
    Faster way to pushing large pandas dataframe ( million+ rows) to database. This one is specifically tested for Postgres.
    In comparison to df.to_sql this function took only 16s, while to_sql took about 3min for 6 million rows with no indexes.
    Orig source : https://github.com/blaze/odo/issues/614
    Args:
        df (DatFrame): Single index and column Dataframe to be pushed to Database 
        table_name (String): name of the table in the Database
        con (SQlAlchemy.Engine.Connection): SQLAlchemy database connection
        if_exists (str, optional): if table already exists then to replace it on append to it. Defaults to 'replace'.
        sep (str, optional): CSV file separator. Defaults to '\t'.
        index(bool, optional) : to use index as values for Db table or not. Defaults to False. 
        encoding (str, optional): Encoding for Db connection. Defaults to 'utf-8'.
        dtypes (Dict, optional): Dictionary of column names and database to be set in Databasse. Defaults to None.
    """
    # Create Table
    if not dtypes is None:
        df[:0].to_sql(table_name, con, if_exists=if_exists, index=index,dtype=dtypes)
    elif if_exists == "replace":
        df[:0].to_sql(table_name, con, if_exists=if_exists, index=False)

    #Prepare data
    output = io.StringIO()
    df.to_csv(output, sep=sep, header=False, index=index,encoding=encoding)
    #output.getvalue()
    output.seek(0)
    
    #Insert data
    raw = con.engine.raw_connection()
    curs = raw.cursor()
    # null values become ''
    # columns = df.columns
    curs.copy_from(output, table_name, null="")
    curs.connection.commit()
    curs.close()
    del output

def load_css():
    with open(CSS_FILE) as f:
        css_text = f.read()
        st.markdown('<style>{}</style>'.format(css_text), unsafe_allow_html=True)