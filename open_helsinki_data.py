import requests
import pandas as pd
from typing import Dict


def openapi2restaurants(url: str, payload: Dict[str, str]) -> pd.DataFrame:
    """Gets data from an open api at url and payload, extracts the JSON, converts to pandas DataFrame and fitlers selectively

    Args:
        url (str): The URL of the MyHelsinki Open API
        payload (Dict[str, str]): key-value pairs to pass as query params

    Returns:
        pd.DataFrame: Filtered dataframe of restaurants with selected tags retained.
    """

    response = requests.get(url, params=payload)
    restaurants = response.json()

    data = []
    for restaurant in restaurants["data"]:
        id_code = restaurant["id"]
        name = restaurant["name"]["en"]
        url = restaurant["info_url"]
        lat = restaurant["location"]["lat"]
        lon = restaurant["location"]["lon"]
        address = ", ".join(restaurant["location"]["address"].values())
        tag_names = [tag["name"] for tag in restaurant["tags"]]
        tag_codes = [tag["id"] for tag in restaurant["tags"]]
        opening_hours = restaurant["opening_hours"]
        data.append(
            [
                id_code,
                name,
                url,
                lat,
                lon,
                address,
                tag_names,
                tag_codes,
                opening_hours,
            ]
        )

    pd_restaurants = pd.DataFrame(
        data,
        columns=[
            "id_code",
            "name",
            "url",
            "lat",
            "lon",
            "address",
            "tag_names",
            "tag_codes",
            "opening_hours",
        ],
    )
    wanted_tags = [
        "RESTAURANTS & CAFES",
        "Vegetarian",
        "Vegan",
        "Bakery",
        "Lunch",
        "Brunch",
        "Russian",
        "Pub",
        "Bistro",
        "Organic",
        "Pizza",
        "Italian",
        "Finnish",
        "International",
        "Hamburger",
        "Spanish",
        "Beef",
        "Vietnamese",
        "Chinese",
        "Asian",
        "StreetFood",
        "Thai",
        "MiddleEast",
        "French",
        "TraditionalFinnish",
        "Mexican",
        "Corean",
        "Japanese",
        "Fish",
        "Georgian",
        "Greek",
        "Sushi",
        "Indian",
        "FastFood",
        "Filipino",
        "Grocery",
    ]

    exploded_restaurants = pd_restaurants.explode("tag_names").reset_index(drop=True)

    filtered_exploded_restaurants = exploded_restaurants[
        exploded_restaurants["tag_names"].isin(wanted_tags)
    ]
    agg_functions = {col: "first" for col in filtered_exploded_restaurants.columns}
    agg_functions["tag_names"] = lambda group: group.tolist()
    filtered_restaurants = filtered_exploded_restaurants.groupby("id_code").agg(
        agg_functions
    )
    return filtered_restaurants.reset_index(drop=True)


url = "http://open-api.myhelsinki.fi/v1/places/"
payload = {"tags_search": "matko1:10", "language_filter": "en"}
pd_restaurants = openapi2restaurants(url, payload)