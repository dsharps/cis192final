import requests
import base64

consumer_key = 'swxgDjmwyDgArD7qzLt9oOmsO'
consumer_secret = 'c3eGzKi5O2sXZ7bivL491Mm84XTEocEjuLFtqNjZoQRSyfyzBd'

def get_access_token(consumer_key, consumer_secret):
    ''' Implement application-only authentication, as described here:
    https://dev.twitter.com/docs/auth/application-only-auth

    The function returns an access token, which can then be used
    to make authenticated requests in the rest of the code.
    '''

    #Encode consumer key and secret
    request_token = 'Basic ' + base64.b64encode('%s:%s' % (consumer_key, consumer_secret))

    #Request access token
    data = {'grant_type': 'client_credentials'}
    headers = {'Authorization': request_token, 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    request_url = 'https://api.twitter.com/oauth2/token'
    req = requests.post(request_url, data=data, headers=headers)

    #Raise an exception if we get a bad access code
    if (req.status_code != 200):
        req.raise_for_status()

    #Get access token from the returned request
    return 'Bearer ' + req.json()['access_token']


#Get the access token for our key and secret
access_token = get_access_token(consumer_key, consumer_secret)
headers = {'Authorization': access_token}


class TwitterUser(object):
    ''' A Twitter user entity that takes a screen name as input.

    Makes appropriate API calls to populate screen_name, tweets, followers.
    Used API Documentation here: https://dev.twitter.com/docs/api/1.1

    TwitterUser instances contain the following attributes: screen_name,
    tweets (a list of at most the last 3200 tweets by the user),
    followers_num (number of followers), following_num (number of users
    twitter user follows), followers (alphabetically sorted list of ten
    most recent followers).
    '''


    def __init__(self, name):
        self.screen_name = name

        #find the list of the first 200 tweets (note that 200 includes deleted tweets)
        tweets_search_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        tweets_params = {'screen_name': name, 'count': 200}
        tweets_req = requests.get(tweets_search_url, params=tweets_params, headers=headers)


        '''NEED TO DECIDE HOW TO ERROR HANDLE:
        The following few lines of code will throw an error if the username entered is either
        invalid or the user's tweets are protected. Need to decide if we are just going to throw
        an error, or if we're going to create a TwitterUser, or what.

        NOTE that we also have to handle errors for the functions with the stats--a lot of users
        have 0 tweets so that will cause an issue when we do some calculations.

        I'm not sure how you want to handle this. I've noted which functions could be problematic.
        '''
        #Check to make sure have access to tweets (won't pass if tweets protected)
        if (tweets_req.status_code != 200):
            req.raise_for_status()

        self.tweets = [Tweet(tweet_dict) for tweet_dict in tweets_req.json()]

        #Loop 15 times because already got 200 and 16*200 = 3200 is the most twitter can recover
        for _ in xrange(15):
            #subtract 1 to make it exclusively older than last one
            last_tweet_id = self.tweets[-1].id - 1
            tweets_params_new = {'screen_name': name, 'count': 200, 'max_id' : last_tweet_id}
            tweets_req_new = requests.get(tweets_search_url, params=tweets_params_new, headers=headers)

            for tweet_dict in tweets_req_new.json():
                self.tweets.append(Tweet(tweet_dict))

        #Get the number of followers and following
        self.followers_num = tweets_req.json()[0]['user']['followers_count']
        self.following_num = tweets_req.json()[0]['user']['friends_count']

        self.most_pop = most_popular_tweet(self)

        #find the list of last ten followers
        followers_search_url = 'https://api.twitter.com/1.1/followers/list.json'
        followers_params = {'screen_name': name, 'count': 10}
        followers_req = requests.get(followers_search_url, params=followers_params, headers=headers)
        self.followers = sorted([follower['screen_name'] for follower in followers_req.json()['users']])



class Tweet(object):
    ''' An entity corresponding to a single tweet.

    The constructor takes a dictionary because the user timeline lookup
    returns a dictionary for each tweet.

    Tweet instances contain the following attributes: text (the tweet)
    text), id (unique), hashtags (a list of hashtags appearing in the tweet),
    time_created (time tweet created), favorite_count, retweet_count,
    and a list of the screennames of the first (up to) five users who
    retweeted it.

    The screen names of rewteeters are lazily loaded using the
    @property decorator. That is, the value of retweeted is initially 
    set to None, and is then populated upon the first access.
    '''

    def __init__(self, tweet_dict):
        self.text = tweet_dict['text']
        self.hashtags = tweet_dict['entities']['hashtags']
        self.id = tweet_dict['id']
        self.time_created = tweet_dict['created_at']
        self.favorite_count = tweet_dict['favorite_count']
        self.retweet_count = tweet_dict['retweet_count']

    #Find the list of retweeters' usernames
    @property
    def retweeted(self):
        if not hasattr(self, '_retweeted'):
            retweeted_url = 'https://api.twitter.com/1.1/statuses/retweets/' + repr(self.id) + '.json'
            retweeted_params = {'id': self.id, 'count': 5}
            retweeted_req = requests.get(retweeted_url, params=retweeted_params, headers=headers)
            self._retweeted = [rt['user']['screen_name'] for rt in retweeted_req.json()]
        return self._retweeted



#MIGHT THROW AN ERROR IF FIRST_TWEET IS NONE
def find_num_tweets(twitter_user):
    num_tweets = len(twitter_user.tweets)
    first_tweet = twitter_user.tweets[-1]
    time = first_tweet.time_created
    return (num_tweets, time)

    '''Need to put time into better format, calcualte how many days have passed since time
    first tweeted, and then compute the average tweets per day'''


#NEED TO CHECK IF THERE ARE ANY FOLLOWERS, ERROR HANDLE
def following_followers_ratio(twitter_user):
    return float(twitter_user.following_num)/float(twitter_user.followers_num)

    #Maybe have tiers--if your ratio is below 1/1000, CELEBRITY STATUS WOOHOO


#NEED TO CHECK IF THERE ARE ANY TWEETS, ERROR HANDLE
def least_popular_tweet(twitter_user):
    #Calculate tweet popularity as favorites+retweets
    least_pop = twitter_user.tweets[0]

    for tweet in twitter_user.tweets:
        if (tweet.favorite_count+tweet.retweet_count < least_pop.favorite_count+least_pop.retweet_count):
            least_pop = tweet

    return least_pop


#NEED TO CHECK IF THERE ARE ANY TWEETS, ERROR HANDLE
def most_popular_tweet(twitter_user):
    #Calculate tweet popularity as favorites+retweets
    most_pop = twitter_user.tweets[0]

    for tweet in twitter_user.tweets:
        if (tweet.favorite_count+tweet.retweet_count > most_pop.favorite_count+most_pop.retweet_count):
            most_pop = tweet

    return most_pop


#NEED TO CHECK IF THERE ARE ANY TWEETS, ERROR HANDLE
def average_hashtags(twitter_user):
    #Calculate the average number of hashtags per tweet
    hashtag_num = 0

    for tweet in twitter_user.tweets:
        hashtag_num += len(tweet.hashtags)

    return float(hashtag_num)/float(len(twitter_user.tweets))

    '''Neil's average hashtags per tweet seems super low, either he actually doesn't do it much
    or something is wrong'''


#NEED TO CHECK IF THERE ARE ANY TWEETS, ERROR HANDLE
def average_favorites(twitter_user):
    #Calculate the average number of favorites per tweet
    favorites_num = 0

    #If no tweets, return 0
    #if twitter_user.tweets == []:


    for tweet in twitter_user.tweets:
        favorites_num += tweet.favorite_count

    return float(favorites_num)/float(len(twitter_user.tweets))


    '''This claims that CatpunAmerica has 3 favorites, not two... not sure why'''



'''Potentially also want to add the following stats:
    -variety of vocabulary
    -average length of tweet
    -average curse words per tweet
    -average number of links
'''




def main():
    nph = TwitterUser('ActuallyNPH')
    catpun = TwitterUser('CatpunAmerica')

    nph_numtweets = find_num_tweets(nph)
    print nph.screen_name + " has tweeted " + str(nph_numtweets[0]) + \
        " times since " + str(nph_numtweets[1])

    print nph.screen_name + "'s Following/Followers ratio is " + str(following_followers_ratio(nph))

    nph_leastpop = least_popular_tweet(nph)
    print nph.screen_name + "'s least popular tweet is: \"" + nph_leastpop.text + "\" with " + \
        str(nph_leastpop.favorite_count) + " favorites and " + str(nph_leastpop.retweet_count) + \
        " retweets" + " from " + nph_leastpop.time_created

    nph_mostpop = most_popular_tweet(nph)
    print nph.screen_name + "'s most popular tweet is: \"" + nph_mostpop.text + "\" with " + \
        str(nph_mostpop.favorite_count) + " favorites and " + str(nph_mostpop.retweet_count) + \
        " retweets" + " from " + nph_mostpop.time_created

    print nph.screen_name + " has an average of " + str(average_hashtags(nph)) + " hashtags per tweet" 
    print catpun.screen_name + " has an average of " + str(average_hashtags(catpun)) + " hashtags per tweet"

    print nph.screen_name + " has an average of " + str(average_favorites(nph)) + " favorites per tweet" 
    print catpun.screen_name + " has an average of " + str(average_favorites(catpun)) + " favorites per tweet"  
    

if __name__ == "__main__":
    main()