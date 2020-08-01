# -*- coding: utf-8 -*-
"""PURE_OwnSpotifyData.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wr9Wt_SiT3Og36YUHdBBybWrvAgp5EUx
"""

!pip install spotipy

import argparse
import pprint
import sys
import os
import subprocess
import json
import spotipy
import spotipy.util as util
import pandas as pd
import time
from spotipy.oauth2 import SpotifyClientCredentials


client_credentials_manager = SpotifyClientCredentials(client_id= '77fbff4d863a482d82ce8fa6dbbc9f1b', client_secret='55c4c40ecaf445c0b9d742b5099d6888')
username = "11163955165"




def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print (" %d %s %s" % (i, track['artists'][0]['name'],track['name']))

def get_track_features(track_id,sp):
    if track_id is None:
        return None
    else:
        features = sp.audio_features([track_id])
    return features

def get_features(tracks,sp):
    tracks_with_features=[]
    
    for track in tracks:
        features = get_track_features(track['id'],sp)
        print(track['name'])
        
        
        if not features:
            print("passing track %s" % track['name'])
            pass
        else:
            f = features[0]

        tracks_with_features.append(dict(
                                        name=track['name'],
                                        artist=track['artist'],
                                        id=track['id'],
                                        danceability=f['danceability'],
                                        energy=f['energy'],
                                        loudness=f['loudness'],
                                        speechiness=f['speechiness'],
                                        acousticness=f['acousticness'],
                                        tempo=f['tempo'],
                                        liveness=f['liveness'],
                                        valence=f['valence']
                                        ))

        time.sleep(0.1)

    
    return tracks_with_features

def get_tracks_from_playlists(username, sp):
    playlists = sp.user_playlists(username)
    trackList = []
    for playlist in playlists['items']:
        #  if playlist['owner']['id'] == username:
            print(playlist['name'],' no. of tracks: ',playlist['tracks']['total'])
            results = sp.user_playlist(username, playlist['id'],fields="tracks")
            tracks = results['tracks']
            for i, item in enumerate(tracks['items']):
                track = item['track']
                trackList.append(dict(name=track['name'], id=track['id'], artist=track['artists'][0]['name']))

    
    return trackList

def write_to_csv(track_features):
    df = pd.DataFrame(track_features)
    # df.drop_duplicates(subset=['name','artist'])
    print ('Total tracks in data set', len(df))
    df.to_csv('mySongsDataset.csv',index=True)

def main(username):
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    print ("Getting user tracks from playlists")
    tracks = get_tracks_from_playlists(username, sp)
    print ("Getting track audio features")
    tracks_with_features = get_features(tracks,sp)
    print ("Storing into csv")
    write_to_csv(tracks_with_features)
    


if __name__ == '__main__':
    print ('Starting...')
    #parser = argparse.ArgumentParser()
    #parser.add_argument('--username', help='username')
    #args = parser.parse_args()
    main(username)

#loading mySongs.csv file to use

spotifysongs = pd.read_csv("/content/mySongsDataset.csv")
spotifysongs.info()



#looking for the features, there are 8 feature, we can use all of them for our learning algorithm
spotifysongs = spotifysongs.drop(['energy', 'tempo', 'Unnamed: 0'], axis=1)
spotifysongs.head(10)

spotifysongs.describe()

from sklearn import preprocessing

loudness = spotifysongs[['loudness']].values
min_max = preprocessing.MinMaxScaler()
loudness_scaler = min_max.fit_transform(loudness)
spotifysongs['loudness'] = pd.DataFrame(loudness_scaler)

spotifysongs.hist(bins=50, figsize=(18,14), color = 'green')
import warnings
warnings.filterwarnings(action='ignore')

import numpy as np
import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

#save the numbers
np.random.seed(50)

#plotting

mpl.rc('axes', labelsize = 10)
mpl.rc('xtick', labelsize = 10)
mpl.rc('ytick', labelsize = 10)

#colours for k-means clustering
import seaborn as sns
sns.set_style('white')
custompalette = ['#4682B4', '#8B4513', "#B22222", "#BDB76B"]
sns.set_palette(custompalette)
sns.palplot(custompalette)


#closing the Futurewarning
import warnings
warnings.filterwarnings(action='ignore')

# unsupervised learning algorithm - K-means Clustering
# to start clustering, remove song name, artist

# only_song_features = spotifysongs.copy()
# only_song_features = only_song_features.drop(['name', 'artist', 'id'], axis = 1)

only_song_features = spotifysongs.copy()
only_song_features = only_song_features.drop(['name', 'artist', 'id'], axis = 1)

from sklearn.cluster import KMeans

sum_of_squared_distances = []

for k in range(1,14):
  kmeans = KMeans(n_clusters=k).fit(only_song_features) 
  sum_of_squared_distances.append(kmeans.inertia_) # Sum of squared distances of samples to their closest cluster center.

# fit_predict(self, X[, y, sample_weight], Compute cluster centers and predict cluster index for each sample.

from sklearn.metrics import silhouette_score

for n_clusterss in range(2,14):
  clusterer = KMeans(n_clusters = n_clusterss)
  predictions = clusterer.fit_predict(only_song_features)
  K_centers = clusterer.cluster_centers_

  score = silhouette_score(only_song_features, predictions, metric= 'euclidean')
  print("For n_clusters = {}, silhouette score is {})".format(n_clusterss, score))

plt.plot(range(1,14), sum_of_squared_distances, 'rx-')
plt.xlabel('k')
plt.ylabel('Sum of Squared Distances')
plt.title('Elbow Method For Sufficient K')
plt.show()

#UTKU 
kmeans = KMeans(n_clusters = 4)
kmeans.fit(only_song_features)

# PCA is a method to reduce the dimension to 2
from sklearn.decomposition import PCA
y_kmeans = kmeans.predict(only_song_features)
PCA = PCA(n_components = 2)
principal_components = PCA.fit_transform(only_song_features)

PC = pd.DataFrame(principal_components)
PC['label'] = y_kmeans
PC.columns = ['x', 'y', 'label']
#plot data with Seaborn - sns, which I imported in earlier parts of the code

cluster = sns.lmplot(data = PC, x = 'x', y= 'y', hue = 'label', fit_reg = True, legend = True, legend_out = True) #Legend is the labels on the right

# We only used PCA because there is not any overlapping but if there were we could try t-SNE to reduce overlapping

from sklearn.manifold import TSNE #T-Distributed Stochastic Neighbor Embedding
#T-SNE with reducement to two dimensions
tsne = TSNE(n_components=2, perplexity=50)

tsne_components = tsne.fit_transform(only_song_features)

ts = pd.DataFrame(tsne_components)
ts['label'] = y_kmeans
ts.columns = ['x', 'y','label']

#plot data with seaborn
cluster = sns.lmplot(data=ts, x='x', y='y', hue='label', fit_reg=True, legend=True, legend_out=True)

# Going into 4 clusters

spotifysongs['label'] = y_kmeans

spotifysongs['label'].value_counts()

spotifysongs[spotifysongs['label'] == 3].sample(5)

spotifysongs[spotifysongs['label'] == 1].hist()

spotifysongs[spotifysongs['label'] == 1].hist()

spotifysongs[spotifysongs['label'] == 2].hist()

spotifysongs[spotifysongs['label'] == 3].hist()

spotifysongs[spotifysongs['label'] == 0].mean()

spotifysongs[spotifysongs['label'] == 1].mean()

spotifysongs[spotifysongs['label'] == 2].mean()

spotifysongs[spotifysongs['label'] == 3].mean()

# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.model_selection import cross_val_score
# from sklearn.metrics import classification_report, confusion_matrix
# from sklearn.utils.multiclass import unique_labels


# pred_x = only_song_features[:8]
# rf = RandomForestClassifier(max_depth=5, min_samples_leaf=6, random_state=12)
# rf.fit(only_song_features, y_kmeans)
# label_pred = rf.predict(pred_x)
# print(label_pred)

#MERT ILGINOGLU
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.multiclass import unique_labels

X = only_song_features
y = y_kmeans

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33)

rfc = RandomForestClassifier(max_depth=5, min_samples_leaf=6, random_state=12, n_estimators=100, criterion='gini')
rfc.fit(X_train, y_train)

y_pred = rfc.predict(X_test)

def plot_conf_matrix(y_true, y_pre, classes, normalize=False, title=None, cmap=plt.cm.Blues):

  #Plots the confusion matrix

  if not title:
    if normalize:
      title = 'Normalized confusion matrix'
    else:
      title = 'Confusion matrix'

#Compute the conf matrix
  cm = confusion_matrix(y_true, y_pred)

  if normalize:
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print("Normalized confusion matrix")
  else:
    print('Confusion matrix, without normalization')

  print(cm)

  fig, ax = plt.subplots()
  im = ax.imshow(cm, interpolation = 'nearest', cmap = cmap)
  ax.figure.colorbar(im, ax=ax)

  ax.set(xticks=np.arange(cm.shape[1]), 
         yticks=np.arange(cm.shape[0]),
         xticklabels=classes, yticklabels=classes,
         title=title,
         ylabel='True label',
         xlabel='Predicted label')
  
  #Rotate the labels and set their alignment
  plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

  #Loop data dimensions and create annotations
  fmt = '.2f'
  thresh = cm.max() / 2
  for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
      ax.text(j, i, format(cm[i, j], fmt), ha= 'center', va= 'center', color="black")
  fig.tight_layout()
  return ax

#MERT TURE
definitions = ['Party Mode','Cheerful','Metal','Chill']

plot_conf_matrix(y_test, y_pred, classes=definitions,
                      title='Confusion matrix for Random Forest')

from sklearn.neighbors import KNeighborsClassifier

knn =KNeighborsClassifier(n_neighbors=3, metric="manhattan")
#Training the model with training sets
knn.fit(X_train, y_train)

knn_pred = knn.predict(X_test)
plot_conf_matrix(y_test, knn_pred, classes=definitions, title='Confusion matrix for KNN')

print(classification_report(y_test,y_pred,target_names=definitions)+'forest')

print(classification_report(y_test,knn_pred,target_names=definitions)+'KNN')

from IPython.display import display
print("Please enter the song mood you want(Party, Cheerful , Metal, Chill): ")
users_desire = input()
if users_desire == "Party":
  display(spotifysongs[spotifysongs['label'] == 0].sample(5))
elif users_desire == "Cheerful":
  display(spotifysongs[spotifysongs['label'] == 1].sample(5))
elif users_desire == "Metal":
  display(spotifysongs[spotifysongs['label'] == 2].sample(5))
elif users_desire == "Chill":
  display(spotifysongs[spotifysongs['label'] == 3].sample(5))