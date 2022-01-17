import json_read_write

def saned_anime_data(file_names):
    """ Cleaning anime data
    Open the json with the raw data and put it
    in a standard format
    """
    for file in file_names:
        anime = json_read_write.read_json(file)
        new_animes = {}

        for data in anime:
            new_anime = []
            for tag in data:
                tag = str(tag).replace('\n', '').strip() # Remove os \n e espaço vázios
                new_anime.append(tag)

            tags_not_n = [a for a in new_anime if a not in ['',',','.']] # Ignora os itens com esses dados
            new_animes[tags_not_n[0].replace(':', '')] = tags_not_n[1].replace('#', '') # Remove o "#" do rank

        # Transform some data into int and float
        for tags in new_animes:
            if tags in ['Favorites', 'Members', 'Popularity', 'Ranked', 'Episodes']:
                if new_animes[tags] not in ['Unknown', 'N/A']:
                    new_animes[tags] = int(new_animes[tags].replace(',', ''))
            elif tags in 'Score':
                if new_animes[tags] not in ['Unknown', 'N/A']:
                    new_animes[tags] = float(new_animes[tags])
        
        # Subsections
        new_animes["Languages"] = {}
        new_animes["Studio"] = {}
        new_animes["style"] = {}
        new_animes["assessment"] = {}

        def fors(tags_for_anime, tag):
            for tags in new_animes:
                if tags in tags_for_anime:
                    new_animes[tag][tags] = new_animes[tags]
            [new_animes.pop(key, None) for key in tags_for_anime]

        
        tags_for_anime = ['Japanese', 'English', 'German', 'Spanish', 'French']
        fors(tags_for_anime, "Languages")
        
        tags_for_anime = ['Broadcast', 'Producers', 'Licensors', 'Studios']
        fors(tags_for_anime, "Studio")

        tags_for_anime = ['Genres', 'Themes', 'Demographic', 'Theme', 'Genre']
        fors(tags_for_anime, "style")

        tags_for_anime = ['Score', 'Ranked', 'Popularity']
        fors(tags_for_anime, "assessment")

        json_read_write.write_json(file, new_animes)


def user_info(info, user, animes, friends):
    """Merge user information
    """
    data_user = {}
    data_user["anime"] = []
    data_user["name"] = user
    for i in info:
        data_user[i[0]] = i[1]
    
    for anime in animes:
        data_user["anime"].append(anime[0])
    
    data_user["friends"] = friends

    file_name = f'output/user/{user}.json'
    json_read_write.write_json(file_name, data_user)
    return file_name


# saned_anime_data(['json_example/anime.json'])