"""
    CS 5001 Project Name: Where to live in SF?--May 2nd 2022
    Xinyi Feng
    This is the test file for testing functions in "map_building_house_adding.py"
    See main project py file : "map_building_house_adding.py"
    The data preprocess file is: "crime_data_process.py"
    Please read "ReadMe_directory.doc" for more info
"""
from map_building_house_adding import *
import unittest


class FunctionTest(unittest.TestCase):
    def test_get_house_list(self):
        actual_house_list = get_house_list()
        expect_house_1 = {
            'name': 'AVA',
            'address': '55 9th St, San Francisco, CA 94103',
            'location': (
                37.77717904136104,
                -122.41537614494942),
            'price': 3100,
            'image': 'https://avalonbay-avalon-communities-prod.cdn.arcpublishing.com/resizer'
            '/Fc4Vwh8iJ3wXU_1OdFJYL_pxn38=/1440x810/filters:quality('
            '85)/cloudfront-us-east-1.images.arcpublishing.com/avalonbay'
            '/APJTOWWIFVP6BIBN3FQ7DQPP4I.jpg',
            'link': 'https://new.avaloncommunities.com/california/san-francisco-apartments/ava-55-ninth/'}
        # checks the total houses are successfully added.
        self.assertEqual(len(actual_house_list), 38)
        # checks all the items in first house
        self.assertEqual(actual_house_list[0], expect_house_1)

    def test_adds_details_of_houses(self):
        # test if house list is empty
        house_list = []
        with self.assertRaises(ValueError):
            adds_details_of_houses(house_list)

    def test_calculate_score(self):
        # test the simulated algorithm of scoring house
        house = {"duration": "35 km", "price": 3100,
                 "address": "55 9th St, San Francisco, CA 94103"}
        zip_count = {94103: 8300}
        calculate_score(house, zip_count)
        self. assertEqual(house["score"], 10750.0)


def main():
    unittest.main(verbosity=3)


if __name__ == '__main__':
    main()
