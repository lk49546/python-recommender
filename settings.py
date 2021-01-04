#settings.py

from nltk.corpus import stopwords
import pandas as pd
import pymongo
import numpy as np
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

def get_director(crew):
    for member in crew:
        if member['job'] == 'Director':
            return member['name']
    return np.nan

def get_cast_name(cast):
    lista = []
    for member in cast:
        lista.append(member['name'])
    return lista

def filter_keywords(keywords, key):
    words = []
    for i in keywords:
        if i in key:
            words.append(i)
    return words

def init():
    myclient = pymongo.MongoClient("mongodb://drumreAdmin:ovojedugackasifra@sedam.eu:27017/")
    mydb = myclient["dm"]
    global mycol_recommendations
    mycol_recommendations = mydb["recommendations"]
    global mycol_movies
    mycol_movies = mydb["movies"]
    global mycol_ratings
    mycol_ratings = mydb["ratings"]
    mycol_credits = mydb["credits"]
    mycol_keywords = mydb["keywords"]
    films = pd.DataFrame(list(mycol_movies.find()))
    credits = pd.DataFrame(list(mycol_credits.find()))
    keywords = pd.DataFrame(list(mycol_keywords.find()))
    stop_words = set(stopwords.words('english'))

    global films_detail_info
    films_detail_info = films.merge(credits, on='id').merge(keywords, on='id')

    films_detail_info['director'] = films_detail_info['crew'].apply(get_director)
    films_detail_info['genres'] = films_detail_info['genres'].apply(lambda x: [w['name'].replace(" ", "").lower() for w in x])
    films_detail_info['castname'] = films_detail_info['cast'].apply(get_cast_name)
    films_detail_info['cast'] = films_detail_info['castname'].apply(lambda x: x[:3] if len(x) > 3 else x)
    films_detail_info['keywords'] = films_detail_info['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    #films_detail_info['keywords'] = list(filter(lambda x: x not in stop_words, films_detail_info['keywords']))
    films_detail_info.cast = films_detail_info.cast.apply(lambda x: [w.replace(" ", "").lower() for w in x])
    films_detail_info.director = films_detail_info.director.astype('str').apply(lambda x: x.replace(" ", "").lower())
    films_detail_info.director = films_detail_info.director.apply(lambda x: [x, x, x])
    key = films_detail_info.apply(lambda x: pd.Series(x.keywords), axis=1).stack().reset_index(level=1, drop=True)
    key.name = 'keyword'
    key = key.value_counts()
    key = key[key > 3]
    stemmer = SnowballStemmer('english')
    stemmer.stem('films')

    films_detail_info.keywords = films_detail_info.keywords.apply(lambda x: filter_keywords(x, key))
    films_detail_info.keywords = films_detail_info.keywords.apply(lambda x: [stemmer.stem(i) for i in x])
    films_detail_info.keywords = films_detail_info.keywords.apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
    films_detail_info['stack'] = films_detail_info.keywords + films_detail_info.cast + films_detail_info.genres + films_detail_info.director
    films_detail_info['stack'] = films_detail_info['stack'].apply(lambda x: ' '.join(x))
    count = CountVectorizer(analyzer='word',ngram_range=(1, 3),min_df=0)
    count_matrix = count.fit_transform(films_detail_info['stack'])
    
    global cosine_sim
    cosine_sim = linear_kernel(count_matrix, count_matrix)

    global titles
    titles = films_detail_info.title
    global indices
    indices = pd.Series([i for i in range(len(films_detail_info))], index=films_detail_info.title)