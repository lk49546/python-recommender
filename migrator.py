import pymongo
import requests
from bson.objectid import ObjectId
from bson.dbref import DBRef


myclient = pymongo.MongoClient("mongodb://drumreAdmin:ovojedugackasifra@sedam.eu:27017/")
mydb = myclient["dm"]
mycol = mydb["movies"]
mycol2 = mydb["credits"]
mycol3 = mydb["users"]
mycol4 = mydb["keywords"]
mycol5 = mydb["ratings"]
mycol6 = mydb["recommendations"]

# for y in mycol.find():
#     endpoint = "https://api.themoviedb.org/3/movie/" + str(y["id"]) + "/credits?api_key=" + "2b3dbc328df6c9999aa6a6a1214dcbd0" + "&language=en-US"

#     test_dict = requests.get(endpoint).json()
#     res = {key: test_dict[key] for key in test_dict.keys() 
#                                 & {'cast', 'crew', 'id'}}


#     crews = []
#     casts = []
#     for x in res["crew"]:
#         crews.append({key: x[key] for key in x.keys() 
#                                     & {'name', 'job'}})
#     for x in res["cast"]:
#         casts.append({key: x[key] for key in x.keys() 
#                                 & {'name'}})

#     res["crew"]= crews
#     res["cast"] = casts
#     mycol2.insert_one(res)

# for y in mycol.find():
#     endpoint = "https://api.themoviedb.org/3/movie/" + str(y["id"]) + "/keywords?api_key=" + "2b3dbc328df6c9999aa6a6a1214dcbd0"
#     test_dict = requests.get(endpoint).json()
#     mycol4.insert_one(test_dict)


# mycol5.insert_one({
#     "movieId": 19404,
#     "score": 9
# })

# user = {
#     "name": "Luka Kelava",
#     "email": "luka.kelava2009@gmail.com",
#     "ratings": []
# }

# for i in mycol5.find():
#     user["ratings"].append(DBRef("ratings", i["_id"]))

# mycol3.insert_one(user)
