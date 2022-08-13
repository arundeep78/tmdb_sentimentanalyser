"""
Helper functions for natural language processing tasks

"""

import nltk
import string
import re
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from src import tmdbutils
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords

# download lexicon for vader sentiment analyzer
nltk.download("vader_lexicon")

stopwords_english = stopwords.words('english')


def get_vsa_value(review_text:str, thresh:int = .05, keep_raw: bool = False, stwords:bool = True, hyperlinks:bool=True) -> int:
    """
    Performs Vader sentiment analysis on a review statement and returns -1,0 or 1 as negative, neutral or positive sentiment 
    Note: Currently works only for English language

    Args:
        review_text (str): text string to perform sentiment analysis on
        thresh (int, optional) : threshold for vader sentiment analysis compound value. Defaults to .05
        keep_raw (bool, optional): to keep the raw string with all chracters to perform a basic cleanup for non-english characters. Defaults to False
        stwords (bool, optional): True to remove stop words before performing sentiment analysis. Default True
        hyperlinks(bool, optional): True to remove hyperlinks before performing sentiment analysis. Default: True
    Returns:
        rating: int: sentiment rating fore the review text
    """

    
    sa = SentimentIntensityAnalyzer()

    tfsa = review_text
    # cleans the sentence of extra unicode chracters e.g. a different language chracters
    if not keep_raw:
        tfsa = clean_text(tfsa, stwords, hyperlinks)

    # Get polarity score dictionary
    p_scores = sa.polarity_scores(tfsa)

    # return overall sentiment rating
    return vader_sa_rating(p_scores, thresh)

def vader_sa_rating(ps:dict, thresh:float=.05):
    """
    Takes polarity score dictionary from vader sentiment Intesity analyser and converts into a rating
    -1 : negative
    0 : neutral
    1: positve 

    Args:
        ps (dict): polarity score dictionary from vader sentiment analysis
        thresh (float, optional): threshold value to be used against compound score. Defaults to .05
    Output:
        rating (int) : rating as integer value based on the threshold 
    """

    cmp_value = ps['compound'] 
    return int((abs(cmp_value) > thresh) * np.sign(cmp_value ))

def clean_text(in_text:str, stwords:bool= True, hyperlinks:bool=True) -> str:
    """
    Cleans up text from special chracters, hyperlinks, etc

    Args:
        in_text (str): Input review text
        stwords (bool, optional): True if to remove stopwords from text. Default: True
        hyperlinks (bool, optional): True if urls to be removed from text. Default: True

    Output:
        str : cleaned up text
    """

    regex = re.compile(f'[^a-zA-Z{string.punctuation}{string.digits}{string.whitespace}]')
    out_text = regex.sub("",in_text)

    # remove hyperlinks

    if hyperlinks:
        out_text = re.sub(r'https?:\/\/.*[\r\n]*', '', out_text)

    # remove hashtags
    out_text = re.sub(r'#', '', out_text)
    
    # remove stop words
    if stwords:
        text_tokens = word_tokenize(out_text)

        out_text = [ token  for token in text_tokens if token not in stopwords_english]

        out_text = " ".join(out_text)

    return out_text
