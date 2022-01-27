import json
import os

from dotenv import load_dotenv
from pymongo import MongoClient
import psycopg2
from pypika import Query, Table, Column


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


def conection():
    """
    Create conection with data base Postgres
    """
    conection = psycopg2.connect(dbname=DB_NAME,
                                 user=DB_USER_P, 
                                 host=DB_HOST, 
                                 password=DB_PASS)
    return conection


def run_sql(sql):
    """
    Running commands sql
    """
    conn = conection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()


def constructor_querry(entry, tags, table):
    """ 
    Creates a custom query for each set of information
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


try:
    # Creates the table with user information, if it does not exist
    sql = Query.create_table("user_info").columns(
            Column("name", "VARCHAR", nullable=False),
            Column("gender", "VARCHAR", nullable=True),
            Column("location", "VARCHAR", nullable=True),
            Column("joined", "VARCHAR", nullable=True),
            Column("last_online", "VARCHAR", nullable=True),
            Column("birthday", "VARCHAR")) \
            .primary_key("name")
    run_sql(str(sql))
except:
    pass


try:
    # Creates the table with anime information, if it does not exist
    sql = Query.create_table("anime").columns(
            Column("name", "VARCHAR", nullable=False),
            Column("synonyms", "VARCHAR", nullable=True),
            Column("type", "VARCHAR", nullable=True),
            Column("episodes", "INT", nullable=True),
            Column("status", "VARCHAR", nullable=True),
            Column("aired", "VARCHAR", nullable=True),
            Column("premiered", "VARCHAR", nullable=True),
            Column("source", "VARCHAR", nullable=True),
            Column("duration", "VARCHAR", nullable=True),
            Column("rating", "VARCHAR", nullable=True),
            Column("members", "INT", nullable=True),
            Column("favorites", "INT", nullable=True),
            Column("score", "FLOAT", nullable=True),
            Column("ranked", "INT", nullable=True),
            Column("popularity", "INT", nullable=True),
            Column("demographic", "VARCHAR", nullable=True),
            Column("japanese", "VARCHAR", nullable=True),
            Column("english", "VARCHAR", nullable=True),
            Column("french", "VARCHAR", nullable=True),
            Column("spanish", "VARCHAR", nullable=True),
            Column("german", "VARCHAR", nullable=True),
            Column("broadcast", "VARCHAR", nullable=True),
            Column("producers", "VARCHAR", nullable=True),
            Column("licensors", "VARCHAR", nullable=True),
            Column("studios", "VARCHAR", nullable=True)) \
            .primary_key("name")
    run_sql(str(sql))
except:
    pass


try:
    # Creates the table with user friends, if it does not exist
    sql = Query.create_table("friendship").columns(
            Column("id", "SERIAL", nullable=False),
            Column("name_user", "VARCHAR", nullable=False),
            Column("name_friend", "VARCHAR", nullable=False)) \
            .primary_key("id").foreign_key(["name_user"],Table("user_info"), ["name"])
    # Remove the final parentheses, to be added when editing the string
    sql = str(sql).replace("))",")")
    sql = f'{sql}, FOREIGN KEY ("name_friend") REFERENCES "user_info" ("name"))'
    run_sql(str(sql))
except:
    pass

try:
    # Creates the table with user anime information, if it does not exist
    sql = Query.create_table("anime_view").columns(
            Column("id", "SERIAL", nullable=False),
            Column("name_user", "VARCHAR", nullable=False),
            Column("name_anime", "VARCHAR", nullable=False)) \
            .primary_key("id").foreign_key(["name_user"],Table("user_info"), ["name"])
    # Remove the final parentheses, to be added when editing the string
    sql = str(sql).replace("))",")")
    sql = f'{sql}, FOREIGN KEY ("name_anime") REFERENCES "anime" ("name"))'
    run_sql(sql)
except:
    pass


# SQL commands for anime data
# Execute SQL command according to data passed by parameters
for anime in BD_ANIME.find({},{'_id': 0}):
    try:
        # Parameters used to build custom inserts for the database
        tags = ['Name', 'Synonyms', 'Type', 'Episodes', 'Status', 'Aired', 'Premiered', 'Source', 'Duration', 'Rating', 'Members', 'Favorites']
        table = 'anime'
        sql = constructor_querry(anime, tags, table)

        run_sql(sql)
            
        """ -- Used to build custom updates with passed parameters -- """
        tags = ['Score', 'Ranked', 'Popularity']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Assessment'], tags, table, key_anime)

        run_sql(sql)

        tags = ['Demographic']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Style'], tags, table, key_anime, True)

        run_sql(sql)

        tags = ['Broadcast', 'Producers', 'Licensors', 'Studios']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Studio'], tags, table, key_anime, True)

        run_sql(sql)

        tags = ['Japanese', 'English', 'German', 'Spanish', 'French']
        table = 'anime'
        key_anime = anime['Name']
        sql = update_querry(anime['Titles'], tags, table, key_anime, True)

        run_sql(sql)

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
# Execute SQL command according to data passed by parameters
for user in BD_USER.find({},{'_id': 0}):
    try: 
        # Parameters used to build custom inserts for the database
        tags = ['Name', 'Last Online', 'Gender', 'Birthday', 'Location', 'Joined']
        table = 'user_info'
        sql = constructor_querry(user, tags, table)
        run_sql(str(sql))

        try:
            for anime in user['Anime_list']:
                try:
                    table_sql = Table('anime_view')
                    sql = Query.into(table_sql).columns('name_user', 'name_anime').insert(user['Name'], anime)
            
                    run_sql(str(sql))
                except:
                    pass       
        except:
            pass

        try:
            for friend in user['Friends']:
                try:
                    table_sql = Table('friendship')
                    sql = Query.into(table_sql).columns('name_user', 'name_friend').insert(user['Name'], friend)
            
                    run_sql(str(sql))
                except:
                    pass

        except:
            pass
    
    except Exception as excep:
        # Send the main error output to a file
        with open('log_user.out', 'a') as log:
            log.write(f'{excep}')
            log.close
