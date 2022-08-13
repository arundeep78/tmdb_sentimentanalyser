# TMDB movie review Sentiment Analyser

Sentiment Analyser for movie reviews provided on [The movie database](https://www.themoviedb.org/). 


This is a demo wep-app to download list of popular movies from TMDB, read user reviews and perform sentiment analysis on those reviews.

Sentiment analysis is used to mark each review as `positive`, `negative` or `neutral`. Overall sentiment for a given movie is provided %age of positive reviews to total reviews.

## Technologies

- [Docker](https://www.docker.com/)
- [NLTK](https://www.nltk.org/)
- [Streamlit](https://streamlit.io/)
- [PostgreSQL](https://hub.docker.com/_/postgres/)

## Usage

### Sidebar

App has a left sidebar that provides total movies in local DB and movies with reviews.

User can also select an individual movie to get details of all the reviews for the movie. On selection, it updates Genre information and download poster image from TMDB.

### Main content

Center of the page providers 2 data tables.

- Overview:

    List of movies with basic information and overall %age of postive sentiments.
- Indvidual movie reviews:

    On selection of the movie in left side bar, this table is updated to show all the reviews and its calculated sentiment.

### Right control panel

On the right side there is a control panel to recalculate sentiments by adjusting the parameters for sentiment analyzer

- **Stop words**:
        This check box allows user to select if english stop words to be removed from the review before performing sentiment analysis.
- **Hyperlinks**:
        This checkbox allows user to remove or keep hyperlinks before performing sentiment analysis
- **Threshold**:
        This slider allows user to set threshold for the calculated rating to mark it as positive, negative or neutral.

## Sentiment analysis

This application uses Python's [Natural Language ToolKit](https://www.nltk.org/) to perform sentiment analysis. Specifically for this app, [Vader Sentiment analysis](https://github.com/cjhutto/vaderSentiment).

This classifer providers a `compound score` in addition to scores for positive, negative and neutral category. For this app, `threshold` value is used to define the range for neutral zone between -1 and 1. Higher the threshold, larger the range of neutral zone and thus only extreme cases are rated as positive.

### Pre-processing movie review text

Before calculating Vader scores, we preprocess the review text to remove hastags, hyperlinks and stop words. hyperlinks and stopwords are offered as control options in the app to observe the difference in sentiment ratings.

## How to run

### 1. Github method

1. Clone github repo to local folder
2. Execute below steps 
   1. `docker compose build`
   2. `docker compose up -d`
3. Open https://localhost in local browser

### 2. VS Code

If you use VS code for development, then you can execute and change the application as needed. This setup is based on [VS Code Remote development](https://code.visualstudio.com/docs/remote/remote-overview) especially Remote Containers and [dev containers](https://code.visualstudio.com/docs/remote/containers-tutorial).

1. Clone github repo to local folder
2. Open the folder in VS Code.
3. Open VS Command `Remote Containers: Reopen in container`
4. Launch the application with `F5` or `Ctrl+F5`

