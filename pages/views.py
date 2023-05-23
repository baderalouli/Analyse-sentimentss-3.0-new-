from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth 
from .models import Signup
from googleapiclient.discovery import build
from nltk.sentiment import SentimentIntensityAnalyzer
from neo4j import GraphDatabase
from django.shortcuts import render
from joblib import load
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
import re

# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Signup.objects.get(username=username, password=password)
        except Signup.DoesNotExist:
            error_message = "Nom d'utilisateur ou mot de passe incorrect"
            return render(request, 'pages/login.html', {'error_message': error_message})
        return redirect('about')

    return render(request, 'pages/login.html')


def signup(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Création d'un nouvel objet Signup et sauvegarde dans la base de données
        signup = Signup(username=username, email=email, password=password, confirm_password=confirm_password)
        signup.save()

        return redirect('login')

    return render(request, 'pages/signup.html')



# Fonction pour extraire l'ID de la vidéo à partir du lien YouTube
def extract_video_id(link):
    return re.findall(r"v=(\w+)", link)[0]

# Fonction pour récupérer les commentaires de la vidéo
def extract_comments(video_id):
    api_key = "AIzaSyCiZxSLUuB_I2w7ew-x4X53HL7RVw7RHUI"
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    nextPageToken = None

    while True:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            pageToken=nextPageToken,
            textFormat='plainText'
        ).execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        if 'nextPageToken' in response:
            nextPageToken = response['nextPageToken']
        else:
            break

    return comments

# Fonction pour nettoyer les commentaires
def clean_comments(comments):
    cleaned_comments = []
    for comment in comments:
        # Supprimer les caractères spéciaux, les chiffres et les symboles de ponctuation
        cleaned_comment = re.sub(r"[^a-zA-Z\s]", "", comment)
        # Convertir en minuscules
        cleaned_comment = cleaned_comment.lower()
        # Supprimer les espaces supplémentaires
        cleaned_comment = " ".join(cleaned_comment.split())
        cleaned_comments.append(cleaned_comment)
    return cleaned_comments

positive_count = 0
negative_count = 0
neutral_count = 0

sentiment_mapping = {0: 'négatif', 1: 'neutre', 2: 'positif'}

driver = GraphDatabase.driver("bolt://44.200.57.70:7687", auth=("neo4j", "gang-mathematics-overvoltages"))

def store_comments(video_id, comments, sentiments):
    global positive_count, negative_count, neutral_count
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    with driver.session() as session:
        for comment, sentiment in zip(comments, sentiments):
            # Convertir la valeur du sentiment en numérique
            sentiment_numeric = list(sentiment_mapping.keys())[list(sentiment_mapping.values()).index(sentiment)]
            session.run(
                "CREATE (c:Commentaire {videoId: $videoId, commentaire: $commentaire, sentiment: $sentiment})",
                videoId=video_id,
                commentaire=comment,
                sentiment=sentiment_numeric
            )
            # Compter les sentiments
            if sentiment == 'positive':
                positive_count += 1
            elif sentiment == 'negative':
                negative_count += 1
            elif sentiment == 'neutral':
                neutral_count += 1

# Fonction pour effectuer l'analyse de sentiment et stocker les résultats dans Neo4j
def analyze_comments(video_id):
    global positive_count, negative_count, neutral_count
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    sid = SentimentIntensityAnalyzer()
    clf = load('naive_bayes_model.joblib')
    comments = extract_comments(video_id)
    cleaned_comments = clean_comments(comments)
    # Générer des étiquettes aléatoires pour chaque commentaire
    labels = np.random.choice(['positive', 'negative', 'neutral'], size=len(cleaned_comments))
    # Créer un objet vectoriseur
    vectorizer = TfidfVectorizer() 
    # Vectoriser les commentaires 
    vectorized_comments = vectorizer.fit_transform(cleaned_comments).toarray()  
    # Vérifiez la forme de vectorized_comments
    print("Forme originale de vectorized_comments :", vectorized_comments.shape)
    # Ajuster le nombre de caractéristiques
    if vectorized_comments.shape[1] != 1128:
    # Exemple de réduction du nombre de caractéristiques en utilisant SelectKBest avec le test du chi-carré
        k = 1128  # Nombre de caractéristiques souhaitées
        selector = SelectKBest(chi2, k=k)
        vectorized_comments = selector.fit_transform(vectorized_comments, labels)
    print("Forme ajustée de vectorized_comments :", vectorized_comments.shape)
    # Effectuer des prédictions avec GaussianNB
    result_clf = clf.predict(vectorized_comments)
    result_clf = [sentiment_mapping[sentiment] for sentiment in result_clf]
    store_comments(video_id, cleaned_comments, result_clf)
    # Calculer les pourcentages de chaque sentiment
    total_count = len(result_clf)
    positive_percentage = (positive_count / total_count) * 100
    negative_percentage = (negative_count / total_count) * 100
    neutral_percentage = (neutral_count / total_count) * 100

    # Créer une liste de commentaires avec leurs sentiments correspondants
    comments_with_sentiments = list(zip(cleaned_comments, result_clf))

    return positive_percentage, negative_percentage, neutral_percentage,comments_with_sentiments



def about(request):
    if request.method == 'POST':
        link = request.POST['link']
        video_id = extract_video_id(link)
        positive_percentage, negative_percentage, neutral_percentage, comments_with_sentiments = analyze_comments(video_id)
        message = 'L\'analyse des commentaires a été effectuée avec succès.'
        return render(request, 'pages/result.html', {
            'message': message,
            'positive_percentage': positive_percentage,
            'negative_percentage': negative_percentage,
            'neutral_percentage': neutral_percentage,
            'comments_with_sentiments': comments_with_sentiments,
        })
    else:
        return render(request, 'pages/about.html')


    

def result(request):
    return render(request,'pages/result.html')






















































































    # for comment in comments:
    #      sentiment = model.predict([comment['text']])
    #      if sentiment == 'positive':
    #          positive_count += 1
    #      elif sentiment == 'negative':
    #          negative_count += 1

    # comment['sentiment'] = sentiment
















