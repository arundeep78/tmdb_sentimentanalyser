
import os
import random
import time
from src import utils

import streamlit as st
import sqlalchemy as sa

# Set page confiuration. Must be the first execution in the app/page
st.set_page_config(
   page_title="TMDB review sentiment analyzer",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)



# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():

    # return psycopg2.connect(**st.secrets["postgres"])

    return sa.create_engine(f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}")

# Initialize Db connection
conn = init_connection()

#Read TMDB api key
tmdb_key = os.environ['TMDB_KEY'] #st.secrets['tmdb']['TMDB_KEY']

# Load CSS to hide dataframe index column
# utils.load_css()

def main():
    """
    Sentiment analysis app based on reviews of the daily popular movies list on The moview database
    """

    hc1, hc2 = st.columns([3,1])

    with hc1:    
        st.title("[TMDB](https://www.themoviedb.org/) movie sentiment analyzer - :smile: | :neutral_face: | :disappointed:")
        # st.write(f"https://www.themoviedb.org/")
        
    with hc2:
        st.write("Fetch new list of popular movies from TMDB")
        # To update movie list and sentiments from TMDB website
        update_movie_bt = st.button(
                        label="Update movies",
                        help= 'Fetches new popular movie list from TMDB and recalculates sentiments',
                        )
    st.markdown("---")

    st.write("Current list of popular movies with overall sentiment rating")
    
    # Layout for the overview page 
    c1, c2 = st.columns([3,1])
    
    with c1:
        # Show main overview table
        ovr_table = st.empty() 
    with c2:

        st.write("#####  Update sentiments with new settings")
        rm_hl = st.checkbox(
                    label="Remove hyperlinks",
                    value= True
                    )
        rm_sw = st.checkbox(
                    label= "Remove stop words",
                    value= True
                    )

        threshold = st.slider(
                label= "threshold for positive sentiment",
                min_value= .05,
                max_value= .85,
                value= .05,
                key="threshold",
             
            )
        st.write("---")
        st.write(""" Movie review sentiment analysis based on [VADER 
                    (Valence Aware Dictionary and sEntiment Reasoner)](https://github.com/cjhutto/vaderSentiment#python-demo-and-code-examples)
                    using [NLTK](https://www.nltk.org/) package """)
    # update table if button is clicked        
    if update_movie_bt:
        with st.spinner("Please wait while we fetch updated movies from TMDB..."):
            start = time.perf_counter()
            utils.update_tmdb_pop_movies_sentiments(
                        con = conn,
                        tmdb_key = tmdb_key,
                        thresh = threshold,
                        stwords = rm_sw,
                        hyperlinks = rm_hl
                    )

        st.success(f" Movies successfully updated in {int(time.perf_counter() - start)} seconds!")
    try:
        movie_overview, tot_movies = utils.get_movies_overview(con= conn)
    except:
        # update DB in case there is no initial data
        with st.spinner("Please wait while we initialize the DB with initial movies list. It won't take long ..."):
            start = time.perf_counter()
            utils.update_tmdb_pop_movies_sentiments(con=conn, 
                                            tmdb_key= tmdb_key, 
                                            stwords = rm_sw,
                                            hyperlinks = rm_hl
                                        )

        st.success(f" DB successfully initialized in {int(time.perf_counter() - start)} seconds!\n Enjoy the app!")
    # update sentiments based on new threshold
    utils.update_sentiments(
                    con = conn,
                    thresh = threshold,
                    stwords = rm_sw,
                    hyperlinks = rm_hl
                    )
    
    
    # get movie overview infrom from DB
    movie_overview, tot_movies = utils.get_movies_overview(con= conn)

    movie_overview.columns = [" ".join(c.split("_")).capitalize() for c in movie_overview.columns]

    # separate out genre info from the main table
    movie_genres = movie_overview[['Id','Genre']]

    movie_overview = movie_overview.drop(columns = 'Genre')
    
    ovr_table.dataframe(movie_overview)


   # -------Side bar information-----------#
    st.sidebar.write("### Total Movies : ",tot_movies)
    st.sidebar.write("### Movies with reviews : ",len(movie_overview))
    st.sidebar.write("---")
    # sidebar movie selection for full reviews
    movie_index = st.sidebar.selectbox("Select a movie for detailed reviews",
                     options= movie_overview.index,
                     index= 0,
                     format_func = lambda x: movie_overview.loc[x,'Title']
                     
                     )
    
    # Add genre information
    st.sidebar.markdown(f"**Genre** : {movie_genres.loc[movie_index,'Genre']}")
    
    # image of the selected movie
    st.sidebar.image(utils.get_movie_img_url(
                    m_id = movie_overview.loc[movie_index,'Id'] , 
                    con = conn
                    )
                )
    
    # Individual moview reviews table on the main page
    st.write("#### Review sentiments for : ",
                 f"*{movie_overview.loc[movie_index,'Title']}*"
            )
    m_reviews_df = utils.get_movie_reviews(
                        m_id = movie_overview.loc[movie_index,'Id'],
                        con = conn)

    m_reviews_df.columns = [" ".join(c.split("_")).capitalize() for c in m_reviews_df.columns]

    st.write(m_reviews_df)

if __name__ == "__main__":
    main()

