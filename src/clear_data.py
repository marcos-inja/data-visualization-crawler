import json_read_write

def subsections(new_animes):
    # Create new subsections
    new_animes["Assessment"] = {}
    new_animes["Style"] = {}
    new_animes["Studio"] = {}
    new_animes["Titles"] = {}

    def fors(tags_for_anime, tag):
        for tags in new_animes:
            if tags in tags_for_anime:
                new_animes[tag][tags] = new_animes[tags]
        # After relocating the tags, we have to delete them
        [new_animes.pop(key, None) for key in tags_for_anime]

    # Tags that will be relocated to a subsection
    tags_for_anime = ['Japanese', 'English', 'German', 'Spanish', 'French']
    fors(tags_for_anime, "Titles")
    
    tags_for_anime = ['Broadcast', 'Producers', 'Licensors', 'Studios']
    fors(tags_for_anime, "Studio")

    tags_for_anime = ['Genres', 'Themes', 'Demographic', 'Theme', 'Genre']
    fors(tags_for_anime, "Style")

    tags_for_anime = ['Score', 'Ranked', 'Popularity']
    fors(tags_for_anime, "Assessment")

    return new_animes


def saned_anime_data(file_names):
    """ Cleaning anime data
    Open the json with the raw data and put it
    in a standard format
    """
    for file in file_names:
        anime = json_read_write.read_json(file)
        new_animes = {}
        # get the name of the anime, from the name passed by parameter as address
        new_animes['Name'] = file.split(sep='/')[2].split(sep='.')[0]

        for data in anime:
            new_anime = []
            for tag in data:
                tag = str(tag).replace('\n', '').strip() # Remove the \n and empty space
                new_anime.append(tag)

            tags_not_n = [a for a in new_anime if a not in ['',',','.']] # Ignore items with this data

            index = tags_not_n[0].replace(':', '')
            # Create subcategories for the following tags
            if index in ["Themes","Genres", "Theme", "Genre"]:
                new_animes[index] = []
                # Taking the genres and themes 2 by 2
                for i in tags_not_n[1::2]:
                    new_animes[index].append(i)
            else:
                new_animes[index] = tags_not_n[1].replace('#', '') # Remove the "#" from the rank

        # Transform some data into int and float
        for tags in new_animes:
            if tags in ['Favorites', 'Members', 'Popularity', 'Ranked', 'Episodes']:
                # If it is one of those below, it does nothing, because there is no information
                if new_animes[tags] not in ['Unknown', 'N/A']:
                    new_animes[tags] = int(new_animes[tags].replace(',', ''))
            elif tags in 'Score':
                if new_animes[tags] not in ['Unknown', 'N/A']:
                    new_animes[tags] = float(new_animes[tags])
        
        # Adding subsections
        animes = subsections(new_animes)

        json_read_write.write_json(file, animes)


def user_info(info, user, animes, friends):
    """Merge user information
    """
    data_user = {}
    data_user["Name"] = user

    for i in info:
        data_user[i[0]] = i[1]
    # Put the name of all friends in the Friends array
    data_user["Friends"] = friends

    # Put the name of all anime in the Anime_list in the array
    data_user["Anime_list"] = []
    for anime in animes:
        data_user["Anime_list"].append(anime[0])

    file_name = f'output/user/{user}.json'
    json_read_write.write_json(file_name, data_user)
    return file_name
