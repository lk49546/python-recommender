import settings
from bson.objectid import ObjectId
import numpy as np
import pandas as pd


def get_recommendations(userId, number):
    recommendations = []
    ratings = settings.mycol_ratings.find({"userId" : ObjectId(userId)})
    for rating in ratings:
        for elem in get_recommendation(rating["movieId"], number).array:
            d = {"userId": userId, "name": elem, "reason": rating["movieId"]}
            settings.mycol_recommendations.insert_one(d)


def get_recommendation(film, number):
    my_film = settings.mycol_movies.find_one({"id": film})

    idx = settings.indices[my_film['originalTitle']]
    if type(idx) != np.dtype('int64') and len(idx) > 1:
        idx = sorted(idx, key=lambda x: settings.films_detail_info.iloc[x].popularity, reverse=True)
        idx = idx[0]
    sim_scores = list(enumerate(settings.cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:number+1]
    movie_indices = [i[0] for i in sim_scores]
    return settings.titles.iloc[movie_indices]