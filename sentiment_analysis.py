
# coding: utf-8

# In[23]:

# Sentiment_Analysis
# by Patrick Walsh
# Januray 29, 2016


"""The following begins a modification of the 'Sentiment_Analysis' module.  The goal is to introduce a degree
of control over the number of comments processed for a given post, such as intoducing random sampling when the number
of comments is over a certain theshold, and implementing a maximum number of comments to be processed.

Upon further review, we've noticed that comments are ordered by the number of likes that each receives.  
Rather than sampling randomly, we've decided to take the first 'x' comments 
where x is an integer such that x % 25 = 0

Note: it takes approximately    34 seconds to process a post with 100 comments
                                20 seconds for 50
                                10 seconds for 25"""

def avg_sentiment(url, pages):
    """
    accepts a post url and the maximum number of pages allowed (upt o 25 comments per page)
    and returns metrics sumarizing the sentiment of comments in the form of a pandas dataframe
    """
    import requests
    from textblob import TextBlob
    import datetime
    import json
    import string
    import nltk
    import pandas as pd
    import numpy

    #print "Intitalizing"
    number_of_comments = 0
    avg_polarity = 0
    avg_subjectivity = 0
    avg_words = 0
    avg_sentences = 0
    count = 0
    page_count = 0
    
    access_token = 'CAAAACuIpepUBACIH5lgj4qpAZA30qSpTZCvIAsDGnMrNYg5xgM8nC5iUsg56khHgjzWMO6MBSZALGDLzRZANvfrTPmXFuRZBcMKxBR8GOmpE6WmEQDzbNZBrYvXx5x1rscW7pnb3ROeYw82T8OtLpVGuUrdped1VB0AWGJJAziDf1eujZAv3StfRHIKZCJ39u6MZD'
    graph_url = 'https://graph.facebook.com/comments/?ids=%s&access_token=%s&summary=1' %(url, access_token)
    results = requests.get(graph_url).json() #pings facebook graph api returning a page of up to 25 comments
    

    # initial ping: necessary b/c formatting changes on paginated results
    try:
        num_comments = len(results[url]['comments']['data'])
    except:
        num_comments = 0
        
    if num_comments > 0:
        number_of_comments = number_of_comments + num_comments
        total_comments = results[url]['comments']['summary']['total_count']
        page_count = 1
        
        # if comments --> start analysis on first page
        for rep in range(num_comments):
            text = results[url]['comments']['data'][rep]['message'] # note this is different than the call that must be made for subsequent pages
            text = TextBlob(text)
            text = text.correct()
            
            comment_polarity = text.sentiment.polarity
            comment_subjectivity = text.sentiment.subjectivity
            words = len(text.words)
            sentences = len(text.sentences)

            avg_polarity += comment_polarity
            avg_subjectivity += comment_subjectivity
            avg_words += words
            avg_sentences += sentences
            count = count +1
        
        # proceed to subsequent pages
        try:
            graph_url = results[url]['comments']['paging']['next']
        except:
            graph_url = None    

        while (graph_url != None) and (page_count < pages):
            results = requests.get(graph_url).json() #pings facebook graph api returning a page of up to 25 comments

            try:
                num_comments = len(results['data'])

            except:
                num_comments = 0

            if num_comments > 0:
                page_count = page_count + 1
                number_of_comments = number_of_comments + num_comments
                for rep in range(num_comments):
                    text = results['data'][rep]['message'] # note this is different than the call that must be made for first page
                    text = TextBlob(text)
                    text = text.correct()

                    comment_polarity = text.sentiment.polarity
                    comment_subjectivity = text.sentiment.subjectivity
                    words = len(text.words)
                    sentences = len(text.sentences)

                    avg_polarity += comment_polarity
                    avg_subjectivity += comment_subjectivity
                    avg_words += words
                    avg_sentences += sentences
                    count = count + 1

                try:
                    graph_url = results['paging']['next'] # try to retrieve next page    
                except:
                    graph_url = None   
            else:
                number_of_comments = number_of_comments + 0


        
    else:
        total_comments = 0
        number_of_comments = 0
        avg_polarity = " "
        avg_subjectivity = " " 
        avg_words = " "
        avg_sentences = " " 
        
    
    # post processing
    comments_processed = count
    
    if comments_processed > 0:
        avg_polarity = avg_polarity / count
        avg_subjectivity = avg_subjectivity / count
        avg_words = avg_words / count
        avg_sentences = avg_sentences / count
    else:
        pass
    
    df = pd.DataFrame(columns = ('url', 'total_comments','comments_processed', 'avg_words','avg_sentences','avg_polarity','avg_subjectivity'))
    df.loc[0] = url, total_comments, comments_processed, avg_words, avg_sentences, avg_polarity, avg_subjectivity
    return df


