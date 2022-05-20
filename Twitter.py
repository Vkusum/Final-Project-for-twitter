from logging import getLogger
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import tweepy
import requests
import json
import sys

header = st.container()
dataset = st.container()

with header:
    st.title("Project regarding user's discussing about cancer in Twitter!!!!!!! ")

with dataset:
    st.title('Dataset')
    consumer_key = 'CuCkoRvWWU3QlAVP04bzwAgMb'
    consumer_secret = 'mdVt6OFoAidXhslCeS9tRVjFyvyGJVT4tqouqOTpurSaIIRfR2'
    access_token = '821725153180680193-JPf0eNQqkJg7pVRI3Fj2GZIM8tvulgs'
    access_token_secret = 'wJiXrSkdQ9o7jftOLD98BC1MLME1E5nhC3j2aeVCH5nbA'
    Bearer_Token = 'AAAAAAAAAAAAAAAAAAAAAMYWZQEAAAAAhd3h4NczMdaPN9%2Fd2vyNrtXugpU%3DmiDb4EJE1QpMtbUv46DLfmfQc6M1xF4M6P3HoXYwM6XLWhSsiM'
    OAUTH_KEYS = {'consumer_key': consumer_key, 'consumer_secret': consumer_secret, 'access_token_key': access_token,
                  'access_token_secret': access_token_secret}
    auth = tweepy.OAuthHandler(OAUTH_KEYS['consumer_key'], OAUTH_KEYS['consumer_secret'])

    api = tweepy.API(auth)
    if (not api):
        print("Can't Authenticate")
        sys.exit(-1)
    else:
        print("Scraping data now")  # Enter lat and long and radius in Kms  q='hello'
        cursor = tweepy.Cursor(api.search_tweets, q="cancer", result_type="new", geocode="55.0000,4.0000,1000km",
                               lang='en', count=100)
        results = []
        for item in cursor.items(1000):  # Remove the limit to 1000
            results.append(item)


    def toDataFrame(tweets):
        # COnvert to data frame
        DataSet = pd.DataFrame()

        DataSet['tweetID'] = [tweet.id for tweet in tweets]
        DataSet['tweetText'] = [tweet.text.encode('utf-8') for tweet in tweets]
        DataSet['tweetRetweetCt'] = [tweet.retweet_count for tweet in tweets]
        DataSet['tweetFavoriteCt'] = [tweet.favorite_count for tweet in tweets]
        DataSet['tweetSource'] = [tweet.source for tweet in tweets]
        DataSet['tweetCreated'] = [tweet.created_at for tweet in tweets]
        DataSet['userID'] = [tweet.user.id for tweet in tweets]
        DataSet['userScreen'] = [tweet.user.screen_name for tweet in tweets]
        DataSet['userName'] = [tweet.user.name for tweet in tweets]
        DataSet['userCreateDt'] = [tweet.user.created_at for tweet in tweets]
        DataSet['userDesc'] = [tweet.user.description for tweet in tweets]
        DataSet['userFollowerCt'] = [tweet.user.followers_count for tweet in tweets]
        DataSet['userFriendsCt'] = [tweet.user.friends_count for tweet in tweets]
        DataSet['userLocation'] = [tweet.user.location for tweet in tweets]
        # DataSet['UserWhoRetweeted'] = [i for i in users_retweeted]

        return DataSet





    DataSet = toDataFrame(results)
    line_chart_data = DataSet.copy()

    import datetime

    DataSet.tweetCreated = pd.to_datetime(DataSet.tweetCreated)
    DataSet['tweetCreated_year'] = DataSet.tweetCreated.dt.year
    DataSet['tweetCreated_month'] = DataSet.tweetCreated.dt.month
    DataSet['tweetCreated_weekday'] = DataSet.tweetCreated.dt.weekday
    DataSet['tweetCreated_hour'] = DataSet.tweetCreated.dt.hour
    DataSet.userCreateDt = pd.to_datetime(DataSet.userCreateDt)
    DataSet['userCreate_year'] = DataSet.userCreateDt.dt.year
    DataSet['userCreate_month'] = DataSet.userCreateDt.dt.month
    DataSet['userCreate_weekday'] = DataSet.userCreateDt.dt.weekday
    DataSet['userCreate_hour'] = DataSet.userCreateDt.dt.hour
    DataSet = DataSet.drop(['tweetCreated', 'userCreateDt'], axis=1)
    st.write(DataSet.head())
    st.sidebar.subheader("When and where are users tweeting from?")
    hour = st.sidebar.slider("Hour to look at", 0, 23)
    modified_data = DataSet[DataSet['tweetCreated_hour'] == hour]

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #Streamlit Application Coding ____________________________
    if not st.sidebar.checkbox("Close", True, key='1'):
        st.markdown("### Tweet locations based on time of day")
        st.markdown("%i tweets between %i:00 and %i:00" % (len(modified_data), hour, (hour + 1) % 24))
        st.map(modified_data)
        if st.sidebar.checkbox("Show raw data", False):
            st.write(modified_data)
    st.header("Users created using sources")

    #st.sidebar.checkbox("Show Analysis by year", True, key=1)
    #select = st.sidebar.selectbox('Select a year', DataSet['userCreate_year'])

    # get the state selected in the selectbox
    #year_data = DataSet[DataSet['userCreate_year'] == select]
    #select_status = st.sidebar.radio(('Confirmed','Active', 'Recovered', 'Deceased'))

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #Bargraph 2:

    year_options = DataSet['userCreate_year'].unique().tolist()
    year = st.selectbox("Year you want to see: ",year_options,0 )
    DataSet = DataSet[DataSet['userCreate_year']==year]
    fig1 = px.bar(DataSet, x='userCreate_year', y="tweetSource")
    fig1.update_layout(width=800)
    st.write(fig1)
    #--------------------------------------------------------------------------

    #Piechart

    st.header("Pie Chart of Tweets regarding cancer")

    fig = px.pie(DataSet, values='tweetCreated_hour', names='userLocation',
                 title='tweets about cancer',
                 hover_data=['userLocation'], labels={'Tweets Created': 'tweetCreated_hour'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig)


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #Line Plot3:
    st.header("Line Plots for Hour of the source where users are created")


    line_chart_data['tweetCreated_date'] = pd.to_datetime(line_chart_data['tweetCreated']).dt.day_name()
    line_chart_data['tweetCreated_hour'] = line_chart_data['tweetCreated'].dt.hour
    hour_cross_tab = pd.crosstab(line_chart_data['tweetCreated_hour'],line_chart_data['tweetSource'])

    fig5 = px.line(hour_cross_tab)

    fig5.update_xaxes(type='category')
    st.write(fig5)
    #from wordcloud import WordCloud, STOPWORDS
    #import matplotlib.pyplot as plt
    import nltk

    #comment_words = ''
    #stopwords = set(STOPWORDS)
    #for val in DataSet.tweetText:
        #val = str(val)
        #tokens = val.split()
        #for i in range(len(tokens)):
            #tokens[i] = tokens[i].lower()

        #comment_words += " ".join(tokens) + " "
        #wordcloud = WordCloud(width=400, height=400,
                              #background_color='white',
                              #stopwords=stopwords,
                              #min_font_size=10).generate(comment_words)
    #st.header("Basic Wordcloud showing what users discuss need to work on worcloud for future!!!!")
    # plot the WordCloud image
    #fig6 =plt.figure(figsize=(10, 20), facecolor=None)
    #plt.imshow(wordcloud)
    #plt.axis("off")
    #plt.tight_layout(pad=0)
    #st.pyplot(fig6)
    #__________________________________________
    #area plot
    st.header("Number of followers for the users in Twitter")
    fig7 = px.area(DataSet, x="userScreen", y="userFollowerCt")
    st.write(fig7)
    #------------------------------
    #number of friends
    st.header("Number of friends for the users in Twitter")
    fig8 = px.bar(DataSet, x="userName", y="userFriendsCt")
    st.write(fig8)
    #-----------------------
    #Tweets count
    st.header("Number of tweets created in month for the users in Twitter")
    fig9 = px.bar(DataSet, x="tweetSource", y="tweetCreated_month")
    st.write(fig9)








