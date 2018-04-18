import requests
import json
from bs4 import BeautifulSoup
import sqlite3

DBNAME = 'umma.sqlite'

CACHE_FNAME = 'artcache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


def get_umma_titles(term): #page will be an integer that tells you which page you want to get to 
    baseurl = 'https://exchange.umma.umich.edu/quick_search/query?utf8=%E2%9C%93&q='
    query_url = baseurl + term
    page_text = make_request_using_cache(query_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    result = page_soup.find_all(class_ = "text-left qsResultText") #finding all divs for each result

    #find each text attached to the href
    #make those into a list and print them next to a number 
    list_of_art= [] #making a list of all art restuls
    list_of_links = [] 

    for i in range(len(result)):
        titles = result[i].find("a") #add href to get the links!
        list_of_links.append(result[i].find("a")["href"])
        for each in titles:
            list_of_art.append(each) #making a list of all titles!

    # print(list_of_links)

    acc = 0
    for each in list_of_art:
        acc += 1
        print(acc, each)

    return list_of_links

def create_art_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = '''
            DROP TABLE IF EXISTS 'Artists';
        '''
        cur.execute(statement)
        conn.commit()
        statement = '''
        CREATE TABLE 'Artists' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'FirstName' TEXT NOT NULL,
            'LastName' TEXT NOT NULL,
            'Nationality' TEXT,
            'ObjectsInCollection' INTEGER
                );
            '''
        cur.execute(statement)
        conn.commit()

        statement = '''
            DROP TABLE IF EXISTS 'Art';
        '''
        cur.execute(statement)
        conn.commit()

        statement = '''
        CREATE TABLE 'Art' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT NOT NULL,
            'Artist' TEXT NOT NULL,
            'ArtistId' INTEGER NOT NULL,
            'ObjectCreationDate' TEXT NOT NULL,
            'Medium' TEXT NOT NULL,
            'Dimensions' TEXT NOT NULL,
            FOREIGN KEY('ArtistId') REFERENCES 'Artists(Id)' 
                );
            '''
        cur.execute(statement)
        conn.commit()

        conn.close()
    except:
        print("Sorry, cannot create database")


def crawl_and_populate(link_list):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    #SEARCH FOR ART TABLE INFO
    baseurl = 'https://exchange.umma.umich.edu'
    # artist_list = []
    for each_href in link_list:
        each_art_page = baseurl + each_href
        page_text = make_request_using_cache(each_art_page)
        page_soup = BeautifulSoup(page_text, 'html.parser')

        #FINDING TITLE
        art_title = page_soup.find("h2").text
        
        #FINDING ARTIST NAME
        try:
            art_artist = page_soup.find('span', class_="co-search co-artist").text #this is the class of the span which includes the artist text
        except:
            artists = page_soup.find_all(class_="col-sm-4 collectionObjectDetailText")
            art_artist = artists[0].find('a').text

        #split into first and last names for Artist table
        first_last = art_artist.split()
        # underscore_name = str(first_last[0] + "_" + first_last[1])
        if len(first_last) == 3:
            first = str(first_last[0] + first_last[1])
            last = first_last[-1]
        else: 
            first = first_last[0]
            last = first_last[-1]

        # artist_list.append(underscore_name)

        #FINDING THE REST....
        stuff = page_soup.find_all(class_="col-sm-4 collectionObjectDetailText")

        #FINDING DATE
        starting_location = (stuff[0].text).find("Creation Date") # this will return the first index of Creation Date1234
        # print (starting_location)
        # print (stuff[0].text[starting_location]) 
        year = stuff[0].text[starting_location+13: starting_location+17] 
        try:
            try: 
                art_date = int(year) #this is if there is just one year
            except: 
                art_date = int(stuff[0].text[starting_location+19: starting_location+23]) #this is if there is 'circa' in front of the year
        except:
            art_date = stuff[0].text[starting_location+13: starting_location+25] #this is if its xth century


        #FINDING MEDIUM AND DIMENSIONS
        medium_start = (stuff[0].text).find("Medium & Support") #len of Medium & Support is 16
        dimensions_start = (stuff[0].text).find("Dimensions") #len of dimenstions is 10
        credit_start = (stuff[0].text).find("Credit Line")  

        art_med = stuff[0].text[medium_start+16: dimensions_start]
        art_dim = stuff[0].text[dimensions_start+10: credit_start]

        #create instance of class instead 
        #POPULATING ARTIST TABLE
        insertion = (None, first, last, " ", " ") 
        statement = 'INSERT INTO "Artists" '
        statement += 'VALUES (?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

        #POPULATING ART TABLE
        insertion = (None, art_title, art_artist, " ", art_date, art_med, art_dim) 
        statement = 'INSERT INTO "Art" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()

    return artist_list
    


def get_artist_info(artist_list):
    #for each of the artist name in the list:
    #make a request to the API an d
    for each in artist_list: #iterating through the list of artists with each elem as first_last format
        data = requests.get('http://dbpedia.org/data/' + each + '.json').json()
        the_artist = data['http://dbpedia.org/resource/' + each]

        # the_artist is a dictionary with lots of keys
        # that correspond to the player's properties.
        # Each value is a list of dictionaries itself.

        birthday = the_artist['http://dbpedia.org/ontology/birthDate'][0]['value']
        print(birthday)
        pass
        # 1.88  (float)
        # birth_year = the_artist['http://dbpedia.org/ontology/birthYear'][0]['value']
        # # '1995'  (string)
        # hand = the_artist['http://dbpedia.org/ontology/plays'][0]['value']
        # 'Right-handed (two-handed backhand)'  (string)
        # singles_rank = the_artist['http://dbpedia.org/property/currentsinglesranking'][0]['value']
        



    #SEARCH FOR ARTISTS TABLE INFO
    #use api to get information for all of the artists that turn up in whatever query runs above ; use that date to populate the Artist table (simulateously)


create_art_db()


crawl_and_populate(get_umma_titles("apple"))

#CLASSES NOTE - option to define/mak instances of classes as you are pulling stuff from the database (define class that will represent that peice of data)

# DB: #homework 11, project 3 

#create function at bottom that will run all of the functions 

