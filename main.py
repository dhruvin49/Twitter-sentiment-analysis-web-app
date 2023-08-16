from flask import Flask,render_template, redirect, request
import numpy as np
import tweepy 
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import re

app = Flask(__name__)


@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():
    userid = request.form.get('userid')
    hashtag = request.form.get('hashtag')

    if userid == "" and hashtag == "":
        error = "Please Enter any one value"
        return render_template('index.html', error=error)
    
    if not userid == "" and not hashtag == "":
        error = "Both entry not allowed"
        return render_template('index.html', error=error)

    api_key = "4AhyUEfcBMKId6SRcU8MBQC9i"
    api_secret = "f878mwZZ00Y4uc6kca9udkShuowTO3N1dClteZTdvuVsuAuuXi"
    bearer_token = r"AAAAAAAAAAAAAAAAAAAAADuApQEAAAAA8a0cRvVT%2FdATQs0z7hoZyNlg56Q%3DZd746EDokKK6TvdrzddX9cqHq1vBY12N758MUWeIq7aDgz5fA2"
    consumerKey = "4AhyUEfcBMKId6SRcU8MBQC9i"
    consumerSecret = "f878mwZZ00Y4uc6kca9udkShuowTO3N1dClteZTdvuVsuAuuXi"
    accessToken = "1690737196788297728-GB9ZYUdXJOjWaqJckI3oyxwNocvr6v"
    accessTokenSecret = "QuWwsHVVKTD5eXhounw0MFta7ASFuJeekfGOHB5RlNOHr"
    
    
    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate)

    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text) # Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        return text
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity
    def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

    if userid == "":
        
        msgs = []
        msg =[]
        # for tweet in tweepy.Cursor(api.search, q=hashtag).items(500):
        for tweet in tweepy.Cursor(tweepy.API().search_tweets, q=hashtag).items(500):
            msg = [tweet.text] 
            msg = tuple(msg)                    
            msgs.append(msg)
        if len(msgs)==0:
            return render_template('index.html')

        df = pd.DataFrame(msgs)
        df['Tweets'] = df[0].apply(cleanTxt)
        print(df['Tweets'])
        df.drop(0, axis=1, inplace=True)
        df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
        df['Polarity'] = df['Tweets'].apply(getPolarity)
        df['Analysis'] = df['Polarity'].apply(getAnalysis)
        positive = df.loc[df['Analysis'].str.contains('Positive')]
        negative = df.loc[df['Analysis'].str.contains('Negative')]
        neutral = df.loc[df['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/df.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/df.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/df.shape[0])*100, 1)

        print(df)

        return render_template('sentiment.html', name=hashtag,positive=positive_per,negative=negative_per,neutral=neutral_per)
    else:
       
        username = "@"+userid
        try:
            post = api.user_timeline(screen_name=userid, count = 500, lang ="en", tweet_mode="extended")
        except tweepy.TweepError: 
            post = []
            print("Profile had had protected tweets")

        if len(post)==0:
            return render_template('index.html')
        twitter = pd.DataFrame([tweet.full_text for tweet in post], columns=['Tweets'])

        twitter['Tweets'] = twitter['Tweets'].apply(cleanTxt)
        twitter['Subjectivity'] = twitter['Tweets'].apply(getSubjectivity)
        twitter['Polarity'] = twitter['Tweets'].apply(getPolarity)

        twitter['Analysis'] = twitter['Polarity'].apply(getAnalysis)
        positive = twitter.loc[twitter['Analysis'].str.contains('Positive')]
        negative = twitter.loc[twitter['Analysis'].str.contains('Negative')]
        neutral = twitter.loc[twitter['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/twitter.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/twitter.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/twitter.shape[0])*100, 1)

        return render_template('sentiment.html', name=username,positive=positive_per,negative=negative_per,neutral=neutral_per)

@app.route('/')
def home():
    return render_template('index.html')
    
if __name__ == '__main__':
    app.run()
