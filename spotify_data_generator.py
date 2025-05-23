from dotenv import load_dotenv
import os 
import base64
from requests import post, get
import json
import pandas as pd

load_dotenv()

client_id = os.getenv("CLIENT_ID")
secret_id = os.getenv("CLIENT_SECRET")

#returns the token for spotify
def get_token():
    auth_string = client_id  + ":" + secret_id
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result  = post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization":  "Bearer " + token}

#returns the artist's general info
def get_artist_info(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    
    query_url = url + query

    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) <= 0:
        print("No artist with this name exists")
        return None
    
    return json_result[0]

#returns the proper feature values to populate the table
def get_artist_features(token, artist_id):
    #get top tracks of an artist
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    json_result = json.loads(result.content)["tracks"]

    if len(json_result) <= 0:
        print("Not Valid")
        return None

    songCount = len(json_result)
    name = json_result[0]["artists"][0]["name"]
    artist_info = get_artist_info(token, name)
    followers = artist_info["followers"]["total"]
    genre = artist_info["genres"]
    avg_popularity = 0
    explicit_score = 0
    avg_duration = 0

    #gets averages for every top track
    for song in json_result:
        avg_popularity += int(song["popularity"])

        if(song["explicit"]):
            explicit_score += 1

        avg_duration += int(song["duration_ms"]/1000)

    followersb = 0
    if(followers > 12500):
        followersb = 1
    
    features = {
        "name": name,
        "followers": followersb,
        "artist_genre": genre,
        "average_popularity": avg_popularity/songCount,
        "explicit_score": explicit_score,
        "average_duration": avg_duration/songCount
    }

    return features

#a file with a list of artists to generate data from
artists = open("artists.txt", "r")

token = get_token()

#initialized dictionary for data
dataD = {'name':[], "followers":[], 'artist_genre':[], "average_popularity":[], "explicit_score":[], "average_duration":[]}

#provides entries for the dictionary
genres = [None]

for l in artists:
    artist_name = l.strip()
    result = get_artist_info(token, artist_name)
    artist_id = result["id"]

    features = get_artist_features(token, artist_id)
    if features == None:
        continue
    if not len(features["artist_genre"]) == 0 and not (features["artist_genre"][0] in genres):
        genres += [features["artist_genre"][0]]
    for k in features:
        if(k == "artist_genre"):
            if(len(features[k]) == 0):
                dataD[k] += [0]
                continue
            dataD[k] += [genres.index(features[k][0])]
            continue
        dataD[k] += [features[k]]



#converts the dictionary to a csv file
data = pd.DataFrame.from_dict(dataD)
data.to_csv("spotify_data.csv", index = False)

