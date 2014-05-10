README for TwitterStats
Dave Sharples and Assaph Aharoni

TwitterStats is built on our HW9 twitter assignment - it uses the Twitter API to grab a bunch of public data from the input twitter account name and produce some interesting stats about it. TwitterStats has two components: a twitterstats.py library to do the number crunching and a flask app to serve up the results.

To run the program, go into the project directory and run ‘flask_twitter.py’. Then go to a web browser and navigate to 127.0.0.1:5000 - you’ll see a short description of the project and an inviting search bar where you can enter the twitter handle to explore!

TwitterStats will pull as many as 3,200 tweets from Twitter’s database (the maximum allowable by the twitter API), so it might take a second to load the info page. The function to get all those tweets is pretty interesting - we had to do it in many iterations to work around the tweet download cap. We also have a pretty slick curseword counting function - check it out!