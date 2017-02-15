# Anime Recommender System
**Sapienza - Università di Roma** <br/>
*Master of Science in Engineering in Computer Science* <br/>
*Data Mining, a.y. 2016-17* <br/>

This package contains two scripts used to collect our dataset:
* download-dataset_users.py, used to download users;
* download-dataset-anime.py, used to download data about animes.

Both scripts are based on *BeautifulSoup* library,  a Python library 
designed to help programmers during the scraping phase, and on 
*urllib2*, a module that define functions and classes 
which help in opening URLs.

**download-dataset_users.py** <br/>
*download-dataset_users.py* accesses to the web site to 
download users from 42 countries (we try to get up to 400 users
from each country, in order to provide heterogeneity to the dataset).
 Our dataset is made by 9'868 users. <br/>
One issue related to this part of the crawling is related to 
the fact that myanimelist.net allows users to customize their 
lists of animes, and this causes different users to have profiles with different HTML structures.
 For this reason, we decided to work only on those users that 
 have a profile with default structure. This check is done by the function
  *is_good_user()*, which takes a reference to the html page 
  we want to analyze, and checks two main conditions:
* First of all tries to get the "table" tag which contains
 all data about anime watched by the user (all this data is contained)
 in a tag attribute called "data-items" as a JSON object;
* We try to select only users that can be relevant for our project: 
therefore we check whether the users watched a given amount of animes.
 
**download-dataset_anime.py** <br/>
Since it is easier to get access to animes' data with respect to 
users, *download-dataset_anime.py* performs both crawling and scraping
 of the data about shows, building up a JSON object where each anime 
 is represented as a set of features.
 We selected as features the following information:
 * the type (e.g., TV show, Movie, Special, ...); 
 * the genre (e.g., Action, Comedy, Kids, ...);
 * the rating (i.e., the target age).