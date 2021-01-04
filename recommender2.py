import settings
from bson.objectid import ObjectId
import numpy as np
import pandas as pd


def get_recommendations(userId, number):
    i = 0
    recommendations = []
    reversed_recommendations = dict()
    ratings = pd.DataFrame(list(settings.mycol_ratings.find({"userId" : ObjectId(userId)}))).movieId
    for rating in ratings:
        mov_dict = get_recommendation(rating, number).to_dict()
        for key, value in mov_dict.items():
            if value not in list(ratings):
                if value not in reversed_recommendations:
                    reversed_recommendations[value] = [key]
                else:
                    reversed_recommendations[value] += [key]
    reversed_recommendations_list = list(sorted(reversed_recommendations, key=lambda k: (len(reversed_recommendations[k]), -int(reversed_recommendations[k][0])), reverse=True))
    while len(recommendations) < number:
        recommendations.append(reversed_recommendations_list[i])
        i += 1
    delete_query = { "userId": ObjectId(userId) }
    settings.mycol_recommendations.delete_many(delete_query)
    for i in recommendations[:number]:
        settings.mycol_recommendations.insert_one({"userId" : ObjectId(userId), "movieId": i})



def get_recommendation(film, number):

    idx = settings.indices[film]
    if type(idx) != np.dtype('int64') and len(idx) > 1:
        idx = sorted(idx, key=lambda x: settings.films_detail_info.iloc[x].popularity, reverse=True)
        idx = idx[0]
    sim_scores = list(enumerate(settings.cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:number+1]
    movie_indices = [i[0] for i in sim_scores]
    return settings.ids.iloc[movie_indices]