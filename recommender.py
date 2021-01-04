import pymongo
import pandas as pd
import numpy as np
from bson.objectid import ObjectId
from nltk.corpus import stopwords
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

def get_recommendations(userId):
    recommendations = []
    ratings = mycol_ratings.find({"userId" : ObjectId(userId)})
    for rating in ratings:
        recommendations.append(get_recommendation(rating["movieId"]))
    print()

def get_recommendation(film):
    
    my_film = mycol_movies.find_one({"id": film}, {"originalTitle" : 1})

    films_detail_info = pd.DataFrame(other_films)
    films_detail_info['director'] = films_detail_info['crew'].apply(get_director)
    films_detail_info['genres'] = films_detail_info['genres'].apply(lambda x: [w['name'].replace(" ", "").lower() for w in x])
    films_detail_info['castname'] = films_detail_info['cast'].apply(get_cast_name)
    films_detail_info['cast'] = films_detail_info['castname'].apply(lambda x: x[:3] if len(x) > 3 else x)
    films_detail_info['keywords'] = films_detail_info['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    #films_detail_info['keywords'] = filter(lambda x: x not in stop_words, films_detail_info['keywords'])
    films_detail_info.cast = films_detail_info.cast.apply(lambda x: [w.replace(" ", "").lower() for w in x])
    films_detail_info.director = films_detail_info.director.astype('str').apply(lambda x: x.replace(" ", "").lower())
    films_detail_info.director = films_detail_info.director.apply(lambda x: [x, x, x])
    key = films_detail_info.apply(lambda x: pd.Series(x.keywords), axis=1).stack().reset_index(level=1, drop=True)
    key.name = 'keyword'
    key = key.value_counts()
    key = key[key > 3]
    stemmer = SnowballStemmer('english')
    stemmer.stem('films')

    films_detail_info.keywords = filter_keywords(films_detail_info.keywords, key)
    films_detail_info.keywords = films_detail_info.keywords.apply(lambda x: [stemmer.stem(i) for i in x])
    films_detail_info.keywords = films_detail_info.keywords.apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
    films_detail_info['stack'] = films_detail_info.keywords + films_detail_info.cast + films_detail_info.genres + films_detail_info.director
    films_detail_info['stack'] = films_detail_info['stack'].apply(lambda x: ' '.join(x))
    count = CountVectorizer(analyzer='word',ngram_range=(1, 3),min_df=0)
    count_matrix = count.fit_transform(films_detail_info['stack'])
    cosine_sim = linear_kernel(count_matrix, count_matrix)

    titles = films_detail_info.title
    indices = pd.Series([i for i in range(len(films_detail_info))], index=films_detail_info.title)
    idx = indices[my_film]
    if type(idx) != np.dtype('int64') and len(idx) > 1:
        idx = sorted(idx, key=lambda x: avail.iloc[x].popularity, reverse=True)
        idx = idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:number+1]
    movie_indices = [i[0] for i in sim_scores]
    return titles.iloc[movie_indices]




if __name__ == '__main__':
    myclient = pymongo.MongoClient("mongodb://drumreAdmin:ovojedugackasifra@sedam.eu:27017/")
    mydb = myclient["dm"]
    mycol_movies = mydb["movies"]
    mycol_ratings = mydb["ratings"]
    pipeline2 = [
        {"$lookup": {"from": "credits", "localField": "id", "foreignField": "id", "as": "credits"}},
        {"$replaceRoot": { "newRoot": { "$mergeObjects": [ { "$arrayElemAt": [ "$credits", 0 ] }, "$$ROOT" ]}}},
        {"$project": { "credits": 0 }},
        {"$lookup": {"from": "keywords", "localField": "id", "foreignField": "id", "as": "keywords2"}},
        {"$replaceRoot": { "newRoot": { "$mergeObjects": [ { "$arrayElemAt": [ "$keywords2", 0 ] }, "$$ROOT" ]}}},
        {"$project": { "keywords2": 0 }},
        {"$match": {'voteAverage' : { "$gte": 7 }}}
    ]
    stop_words = set(stopwords.words('english'))
    other_films = list(mycol_movies.aggregate(pipeline2))
    get_recommendations("5ff1b89186276088b08e058b")