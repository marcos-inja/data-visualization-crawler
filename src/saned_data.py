import json
import os

from dotenv import load_dotenv
from pymongo import MongoClient
import psycopg2


load_dotenv()

# Conection Mongo
cliente = MongoClient(os.getenv('MONGODB_URI'))
bd = cliente[os.getenv('MONGODB_NAME')]
BD_USER = bd[os.getenv('MONGODB_USER_CO')]
BD_ANIME = bd[os.getenv('MONGODB_ANIME_CO')]

# Conection Postgres
DB_HOST = os.getenv('POSTGRES_HOST')
DB_NAME = os.getenv('POSTGRES_NAME')
DB_USER_P = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')


class BDConect:
    def __init__(self):
        """
        Create conection with data base Postgres
        """
        self.conection = psycopg2.connect(dbname=DB_NAME,
                                          user=DB_USER_P, 
                                          host=DB_HOST, 
                                          password=DB_PASS)


    def run_sql(self, sql):
        """
        Running commands sql
        """
        cur = self.conection.cursor()
        cur.execute(sql)
        self.conection.commit()
        self.conection.close()


def constructor_querry(entry, tags, table):
    """ 
    creates a custom query for each set of information
    """
    array_choose = []
    for tag in tags:
        try:
            array_choose.append({tag.lower().replace(" ", "_"): entry[tag]})
        except:
            pass
    
    keys = ''
    value = ''

    for list_tag in array_choose:
        for key in list_tag:
            keys += f" {key}"
            word = list_tag[key]

            if key in ['Name', 'Location','Synonyms', 'Type', 'Status', 'Aired', 'Premiered', 'Source', 'Duration', 'Rating']:
                word = str(list_tag[key]).replace("'", "")

            value += f" '{word}'"
    
    keys = keys.strip().replace(' ', ', ')
    value = value.strip().replace(' \'', ',\'')

    sql = f"INSERT INTO {table} ({keys}) VALUES({value});"  
    return sql


def update_querry(entry, tags, table, key_anime, char=False):
    """ 
    Create custom sql for updates of data
    """
    array_choose = []
    for tag in tags:
        try:
            array_choose.append({tag.lower().replace(" ", "_"): entry[tag]})
        except:
            pass
    
    values = ''
    for list_tag in array_choose:
        for key in list_tag:
            if list_tag[key] in ['Unknown', 'N/A']:
                continue
            word = list_tag[key]
            if key in ['Demographic', 'Broadcast', 'Producers', 'Licensors', 'Studios', 'Japanese', 'English', 'German', 'Spanish', 'French']:
                word = list_tag[key].replace("'", "").replace("´", "")
            if not char:
                values += f"{key}={word} "
            else:
                values += f"{key}='{word}' "
            
            
    values = values.strip().replace(' ', ', ')
    if values:
        sql = f"UPDATE {table} SET {values} WHERE name='{key_anime}'"
        return sql


BD = BDConect()


# Try to create the database tables
try:
    sql = "CREATE TABLE user_info (name VARCHAR PRIMARY KEY, gender VARCHAR, location VARCHAR, joined VARCHAR, last_online VARCHAR, birthday VARCHAR);"
    BD.run_sql(sql)
    sql = "CREATE TABLE anime_view (id SERIAL PRIMARY KEY, name_user VARCHAR, name_anime VARCHAR)"
    BD.run_sql(sql)
    sql = "CREATE TABLE friendship (id SERIAL PRIMARY KEY, name_user VARCHAR, name_friend VARCHAR)"
    BD.run_sql(sql)
    sql = "CREATE TABLE anime (name VARCHAR PRIMARY KEY, synonyms VARCHAR, type VARCHAR, episodes INT, status VARCHAR, aired VARCHAR, premiered VARCHAR, source VARCHAR, duration VARCHAR, rating VARCHAR, members INT, favorites INT, score FLOAT, ranked INT, popularity INT, demographic VARCHAR, japanese VARCHAR, english VARCHAR, french VARCHAR, spanish VARCHAR, german VARCHAR, broadcast VARCHAR, producers VARCHAR, licensors VARCHAR, studios VARCHAR)"
    BD.run_sql(sql)
except:
    pass


# SQL commands for anime data
# execute SQL command according to data passed by parameters
cont = 0
for anime in BD_ANIME.find({},{'_id': 0}):
    try:
        cont += 1

        # Parameters used to build custom inserts for the database
        tags = ['Name', 'Synonyms', 'Type', 'Episodes', 'Status', 'Aired', 'Premiered', 'Source', 'Duration', 'Rating', 'Members', 'Favorites']
        table = 'anime'
        sql = constructor_querry(anime, tags, table)
        print(f"{cont}: {sql}")
        BD.run_sql(sql)
        
        """ -- Used to build custom updates with passed parameters -- """
        tags = ['Score', 'Ranked', 'Popularity']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Assessment'], tags, table, key_anime)
        print(f"{cont}: {sql}")
        BD.run_sql(sql)

        tags = ['Demographic']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Style'], tags, table, key_anime, True)
        print(f"{cont}: {sql}")
        BD.run_sql(sql)

        tags = ['Broadcast', 'Producers', 'Licensors', 'Studios']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Studio'], tags, table, key_anime, True)
        print(f"{cont}: {sql}")
        BD.run_sql(sql)

        tags = ['Japanese', 'English', 'German', 'Spanish', 'French']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Titles'], tags, table, key_anime, True)
        print(f"{cont}: {sql}")
        BD.run_sql(sql)

    except Exception as excep:
        # Send the main error output to a file
        with open('log_anime.out', 'a') as log:
            log.write(f'{excep}')
            log.close
    

""" Explanation of try except pass quantity

Excessive use of try except pass is seen as bad practice,
but here we are in python, this is python's ninja way of being.
PYTHÔNICO 
                    ~Jamal Marcos Vespestino da Tarde, 2022.
"""


# SQL commands for user data
# execute SQL command according to data passed by parameters
cont = 0
for user in BD_USER.find({},{'_id': 0}):
    try: 
        cont += 1
        # Parameters used to build custom inserts for the database
        tags = ['Name', 'Last Online', 'Gender', 'Birthday', 'Location', 'Joined']
        table = 'user_info'
        sql = constructor_querry(user, tags, table)
        BD.run_sql(sql)
        print(f"{cont}: {sql}")
    
        try:
            for anime in user['Anime_list']:
                try:
                    sql = f"INSERT INTO anime_view (name_user, name_anime) VALUES('{user['Name']}','{anime}');"
                    BD.run_sql(sql)
                except:
                    pass       
        except:
            pass

        try:
            for friend in user['Friends']:
                try:
                    sql = f"INSERT INTO friendship (name_user, name_friend) VALUES('{user['Name']}','{friend}');"
                    BD.run_sql(sql)
                except:
                    pass
        except:
            pass
    
    except Exception as excep:
        # Send the main error output to a file
        with open('log_user.out', 'a') as log:
            log.write(f'{excep}')
            log.close
