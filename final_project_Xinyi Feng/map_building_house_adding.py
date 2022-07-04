"""
    CS 5001 Project Name: Where to live in SF?--May 2nd 2022
    Xinyi Feng
    This is the Main Part of the project:
    Builds SF-base map and crime map layer , adding NEU markers and houses sources on the map with detail info
    More codes about pre-process crime data is in "crime_data_process.py"
    Tests of the functions of this py file is in "test.py"
    See the final html version : "Where_to_live_in_SF.html"
    or access by github link: https://fentpam.github.io/WhereToLiveInSF/
    Please read "ReadMe_directory.doc" for more info
"""

import folium
import pandas as pd
import requests


def draw_base_map():
    """ Creates a sf-base map
        :param: None
        :return: sf_map(a base map)
    """

    # creates sf-base map with folium first
    sf_map = folium.Map(location=[37.77, -122.42], zoom_start=12, tiles=None)
    folium.TileLayer(
        'https://api.mapbox.com/styles/v1/wzphc2022/cl28kymxy003d15p5rg05dh6o/tiles/256/{z}/{x}/{'
        'y}@2x?access_token=pk.eyJ1Ijoid3pwaGMyMDIyIiwiYSI6ImNsMjhoeXAwNzAwZ2MzYnFqdDU4OXFsbWgifQ.pU4VojoF8AlETQci'
        '-e048Q',
        attr='sf_map',
        name="Where to Live in SF").add_to(sf_map)
    return sf_map


def add_crime_data_layer(map, df):
    """ Adds crime data layer onto sf_map
       :param: a folium map, a data frame
       :return: None
    """
    # reads data from a json file to draw map
    # source from: https://geodata.lib.berkeley.edu/catalog/ark28722-s7jg7w
    try:
        gjson = r'data_files/mapsf.json'
    except Exception as err:
        raise ("Something wrong with the file", err)
    # generates crime-rate choropleth map with data from mapsf.json
    folium.Choropleth(
        name="crime-rate map",  # create a name for map
        geo_data=gjson,  # import area-boundary data
        data=df,  # use processed crime number data, see more in "crime_data_process.py"
        columns=['ZipCode', 'Count'],  # use data
        # coloring areas in terms of its zip code in json file "mapsf.json"
        key_on='feature.properties.ZIP_CODE',
        fill_color='PuBu',  # choose base colors for map
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Crime Rate in San Francisco from 2018 to 2022'
    ).add_to(map)  # adds crime data layer onto map


def mark_neu_on_map(map):
    """ Marks NEU on sf-base map
        :param: a folium map
        :return: None
    """
    # creates Northeastern university popup html body, adding link and image
    neu_html = f"""
        <body>
        <h3 align="center"><a href=https://www.northeastern.edu/ target="_blank">Northeastern University</a ></h3>
        <p align="center">
        <img src =https://upload.wikimedia.org/wikipedia/en/b/bd/Northeastern_University_seal.svg
        alt="NEU" width="100" height="100">
        </p >
        </body>
        """
    # sets up values of popup and marker
    neu_iframe = folium.IFrame(neu_html)
    neu_popup = folium.Popup(neu_iframe, min_width=300, max_width=300)
    folium.Marker(
        location=[37.79310, -122.40463],
        popup=neu_popup,
        tooltip='Northeastern University',
        icon=folium.Icon(color='darkred', icon='fa-solid fa-graduation-cap', prefix='fa')
    ).add_to(map)


def get_house_list():
    """Gets houses information and writes into a list
        :param: None
        :return: a list
    """

    # reads house info from a given Excel file, the file created by myself
    # houses sources are collected from "www.zillow.com"
    try:
        house_excel = pd.read_excel("data_files/house_list.xlsx", "Sheet1")
    except Exception as err:
        raise ("Something wrong with the file", err)
    house_list = []

    # converts each excel row into a dictionary with index name
    index_name = ['name', 'address', 'location', 'price', 'image', 'link']
    for row in range(house_excel.shape[0]):
        house_dictionary = {}
        for col in range(house_excel.shape[1]):
            if col == 2:
                house_dictionary[index_name[col]] = tuple(
                    map(float, house_excel.iat[row, col].split(',')))
            else:
                house_dictionary[index_name[col]] = house_excel.iat[row, col]
        house_list.append(house_dictionary)
    return house_list


def mark_houses_on_map(house_list, points_layer):
    """Marks houses on map with blue icon
       :param: a list, a folium feature group
       :return: None
    """
    # marks houses onto the sf_base map
    for house in house_list:
        folium.Marker(
            location=house["location"],
            tooltip=house["name"],
            icon=folium.Icon(color='blue', icon='fa-huici', prefix='fa')
        ).add_to(points_layer)


def call_google_maps_api(house_address):
    """Calls google maps api to compute duration time from house to NEU
        https://developers.google.com/maps/documentation/distance-matrix/overview
        Parameter: tuple (longitude, latitude)
        Return: DistanceMatrixResponse
        https://developers.google.com/maps/documentation/distance-matrix/distance-matrix#DistanceMatrixResponse
    """
    API_KEY = 'AIzaSyByr-VhA9PkaQKvdo0O4fNxAJvzaeTaWMw'
    NEU_address = [37.79300904052274, -122.40464758727728]
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={house_address[0]},{house_address[1]}' \
          f'&destinations={NEU_address[0]},{NEU_address[1]}&mode=transit&key={API_KEY} '
    payload = {}
    headers = {}
    return requests.request("GET", url, headers=headers, data=payload)


def adds_details_of_houses(house_list):
    """ Adds detail information including price, distance, fare, duration of houses on popup
        Defensively codes: if the fare is null, implies it doesn't need to take transit
        :param: a list
        :return: None
    """
    if len(house_list) == 0:
        raise ValueError  # ("Something wrong with house_list")
    for house in house_list:
        # gets details(distance, duration, fare) of houses by calling api
        response = call_google_maps_api(house["location"])
        duration = response.json(
        )["rows"][0]["elements"][0]["duration"]["text"]
        distance = response.json(
        )["rows"][0]["elements"][0]["distance"]["text"]
        # if fare is null, then it is a walk distance
        try:
            fare = response.json()["rows"][0]["elements"][0]["fare"]["text"]
        except BaseException:
            fare = "Walk distance"
        # adds details info to the house dictionary
        house["duration"] = duration
        house["distance"] = distance
        house["fare"] = fare


def marks_houses_with_popup_on_the_map(house_list, points_layer):
    """Marks houses with popup on the map, includes detail information
       :param: a list, a folium feature group
       :return: None
    """
    if len(house_list) == 0:
        raise ValueError("Something wrong with house_list")
    for house in house_list:
        # defines popup presenting details of houses
        house_html = f"""
        <body>
        <h3 align="center"><a href={house["link"]} target="_blank">{house["name"]}</a ></h3>
        <p align="center">
        <img src = {house["image"]} alt="test" width="200" height="100">
        </p >
        <p style = "margin-left:33%">
        Distance: &nbsp&nbsp{house["distance"]}<br>
        Duration: &nbsp&nbsp{house["duration"]}&nbsp{house["fare"]}<br>
        Price:&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp${house["price"]}
        </p >
        </body>
        """
        # adds details on popup
        house_iframe = folium.IFrame(house_html)
        house_popup = folium.Popup(house_iframe, min_width=370, max_width=370)
        folium.Marker(
            location=house["location"],
            popup=house_popup,
            tooltip=house["name"],
            icon=folium.Icon(color='blue', icon='huici', prefix='fa')
        ).add_to(points_layer)


def calculate_score(house, zip_count):
    """ A simulated algorithm designed to rank houses
        Calculates score for a single house, and extends dictionary with "score" key-value pair
        :param: a dictionary of house, a dictionary of zip
        :return: None
    """
    __crime_factor = 0.5
    __commute_factor = 100
    __price_factor = 1.0
    commute_time = int(house["duration"].split(" ")[0])
    price = house["price"]
    zip_code = int(house["address"][-5:])
    score = zip_count[zip_code] * __crime_factor + \
            commute_time * __commute_factor + price * __price_factor
    house["score"] = score


def rank_houses(house_list, df):
    """ Rank houses by crime rate, commute time and price
        :param: a list, a data frame
        :return: None
    """
    zip_count = dict(zip(df.ZipCode, df.Count))
    for house in house_list:
        calculate_score(house, zip_count)

    # sorts house according to its score
    house_list.sort(key=lambda x: x["score"])


def number_div_icon(color, number):
    """ Create a 'numbered' icon
        :param: color code of icon, and the rank number
        :return: a folium icon
    """
    icon = folium.DivIcon(
        icon_size=(150, 36),
        icon_anchor=(15, 40),
        html="""<span class="fa-stack " style="font-size: 12pt" >>
                    <!-- The icon that will wrap the number -->
                    <span class="fa fa-circle-o fa-stack-2x" style="color : {:s}"></span>
                    <!-- a strong element with the custom content, in this case a number -->
                    <strong class="fa-stack-1x" style="color:{:s}">
                         {:d}
                    </strong>
                </span>""".format(color, color, number)
    )
    return icon


def marks_houses_with_ranked_icon_on_the_map(house_list, points_layer):
    """ Marks houses with a 'numbered' icon on the map
        :param: a list of house, and a folium layer
        :return: None
    """
    # adds link and image and duration, price infor of houses to the popup
    for i in range(len(house_list)):
        ranked_house_html = f"""
        <body>
        <h3 align="center"><a href={house_list[i]["link"]} target="_blank">{house_list[i]["name"]}</a ></h3>
        <p align="center">
        <img src = {house_list[i]["image"]} alt="test" width="200" height="100">
        </p >
        <p style = "margin-left:33%">
        Distance: &nbsp&nbsp{house_list[i]["distance"]}<br>
        Duration: &nbsp&nbsp{house_list[i]["duration"]}&nbsp{house_list[i]["fare"]}<br>
        Price:&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp${house_list[i]["price"]}<br>
        </p >
        </body>
        """
        ranked_house_iframe = folium.IFrame(ranked_house_html)
        ranked_house_popup = folium.Popup(
            ranked_house_iframe, min_width=370, max_width=370)
        folium.Marker(
            location=house_list[i]["location"],
            popup=ranked_house_popup,
            tooltip=house_list[i]["name"],
            icon=number_div_icon('#ffffff', i + 1)
        ).add_to(points_layer)


def marks_top10_houses_with_nearby_info_on_the_map(house_list, points_layer):
    """ Marks top10 houses with a 'numbered' icon on the map, and displays nearby links
        :param: a list of house, and a folium layer
        :return: None
    """
    # filters top 10 houses with pink color
    for item in range(len(house_list)):
        folium.Marker(
            location=house_list[item]["location"],
            popup=house_list[item]["name"],
            tooltip=house_list[item]["name"],
            icon=folium.Icon(color='lightred', icon='fa-huici', prefix='fa')
        ).add_to(points_layer)
    # adds the info about nearby dinning and nearby transit on the popup
    for i in range(len(house_list)):
        html = f"""
        <body>
        <h3 align="center"><a href={house_list[i]["link"]} target="_blank">{house_list[i]["name"]}</a ></h3>
        <p align="center">
        <img src = {house_list[i]["image"]} alt="test" width="200" height="100">
        </p >
        <p style = "margin-left:33%">
        Price:&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp${house_list[i]["price"]}<br>
        Duration: &nbsp&nbsp{house_list[i]["duration"]}<br>
        <a href=https://fentpam.github.io/sf_dinning/>{"See Nearby Dinning"}</a ><br>
        <a href=https://fentpam.github.io/sf_map_transit/>{"See Nearby Transit"}</a ><br>
        </p >
        </body>
        """
        iframe = folium.IFrame(html)
        popup = folium.Popup(iframe, min_width=370, max_width=370)
        folium.Marker(
            location=house_list[i]["location"],
            popup=popup,
            tooltip=house_list[i]["name"],
            icon=number_div_icon('#ffffff', i + 1)
        ).add_to(points_layer)


def main():
    sf_map = draw_base_map()
    # reads datas of crime from a pre-processed csv file, source from 'data sf'
    df = pd.read_csv("data_files/crime_rate_output.csv")  # pre-processed csv file, see more in "crime_data_process.py"
    add_crime_data_layer(sf_map, df)  # adds crime-data layer
    mark_neu_on_map(sf_map)  # marks school on the map
    house_list = get_house_list()
    # builds a new layer with houses
    all_house_markers = folium.FeatureGroup(name="houses")
    # adds house layer onto sf base map
    all_house_markers.add_to(sf_map)
    mark_houses_on_map(house_list, all_house_markers)
    adds_details_of_houses(house_list)  # adds details onto houses
    marks_houses_with_popup_on_the_map(house_list, all_house_markers)
    rank_houses(house_list, df)  # ranks houses
    marks_houses_with_ranked_icon_on_the_map(house_list, all_house_markers)
    # builds another layer with only top 10 houses
    top10_house_markers = folium.FeatureGroup(name="top 10 houses")
    top10_house_markers.add_to(sf_map)
    marks_top10_houses_with_nearby_info_on_the_map(
        house_list[:10], top10_house_markers)
    folium.LayerControl().add_to(sf_map)
    return sf_map


if __name__ == "__main__":
    main()
