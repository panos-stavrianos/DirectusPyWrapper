import os
import unittest
from datetime import datetime

import requests
from dotenv import load_dotenv
from rich import print

from DirectusPyWrapper import Directus
from DirectusPyWrapper._and import _and
from DirectusPyWrapper._or import _or
from DirectusPyWrapper.aggregation_operators import AggregationOperators
from DirectusPyWrapper.directus_response import DirectusResponse
from DirectusPyWrapper.filter import Filter
from DirectusPyWrapper.logical_operators import LogicalOperators
from DirectusPyWrapper.operators import Operators

load_dotenv()
url = os.environ['DIRECTUS_URL']
email = os.environ['DIRECTUS_EMAIL']
password = os.environ['DIRECTUS_PASSWORD']
token = os.environ['DIRECTUS_TOKEN']


class TestDirectus(unittest.TestCase):
    def test_multiple_users_same_session(self):
        session = requests.Session()
        directus1 = Directus(url, token=token, session=session)

        directus2 = Directus(url, token=token, session=session)
        for _ in range(50):
            response1: DirectusResponse = directus1.read_me()
            response2: DirectusResponse = directus2.read_me()

            self.assertIsNotNone(response1.item)
            self.assertIsNotNone(response2.item)
        directus1.logout()
        directus2.logout()

        # Path: directus.py

    def test_login(self):
        with Directus(url, email, password) as directus:
            self.assertIsNotNone(directus._token)

    # Path: directus_request.py
    def test_read_one(self):
        with Directus(url) as directus:
            directus.token = token
            response: DirectusResponse = directus.items('directus_users').read_one(
                "5c4a0fbc-d454-4094-bbf4-5f72f4e57098")
            print(response.errors)
            print(response.item)
            self.assertIsNotNone(response.item)

    def test_read_me(self):
        with Directus(url) as directus:
            directus.token = token
            response: DirectusResponse = directus.read_me()
            print(response.errors)
            print(response.item)
            self.assertTrue(response.is_success)
            self.assertIsNotNone(response.item)

    # Path: directus_request.py
    def test_read_many(self):
        with Directus(url, email, password) as directus:
            filters = [
                _and(
                    _or(
                        Filter(Operators.Equals, location="Administrator"),
                        Filter(Operators.Equals, location=None),
                        Filter(Operators.Equals, location=None)
                    ),
                    Filter(Operators.Equals, **{"role.name": "Administrator"}),
                    Filter(Operators.Equals, last_name="Stavrianos")
                )
            ]

            response: DirectusResponse = directus.items('directus_users') \
                .filter({'first_name': 'Dict!!'}) \
                .filter(Operators.Equals, LogicalOperators.Or, first_name="Panos", location=None) \
                .filter(Operators.Equals, last_name="Stavrianos") \
                .filter(Operators.Equals, first_name="Panos") \
                .filters(filters) \
                .filters(filters) \
                .fields('first_name', 'last_name') \
                .sort('first_name', True) \
                .limit(3) \
                .include_count() \
                .read_many()
            print(response.errors)
            print("counts", response.filtered_count, response.total_count)
            print(response.items)
            self.assertTrue(response.is_success)
            self.assertIsNotNone(response.items)

    # Path: directus_request.py
    def test_aggregate(self):
        with Directus(url, email, password) as directus:
            response: DirectusResponse = directus.items('directus_users') \
                .aggregate(AggregationOperators.Count).read_many()
            print(response.errors)
            print(response.query)

            print(response.item)
            self.assertTrue(response.is_success)
            self.assertIsNotNone(response.items)

    # Path: directus_request.py
    def test_create_one(self):
        with Directus(url, email, password) as directus:
            response: DirectusResponse = directus.items('directus_users').create_one(
                {"first_name": "Python1", "last_name": ""})
            print(response.errors)
            print(response.item)
            self.assertTrue(response.is_success)
            self.assertIsNotNone(response.item)

    def test_create_many(self):
        with Directus(url, email, password) as directus:
            response: DirectusResponse = directus.items('directus_users').create_many(
                [{"first_name": "Python2", "last_name": ""}, {"first_name": "Python3", "last_name": ""}])
            print(response.errors)
            print(response.items)
            self.assertTrue(response.is_success)
            self.assertIsNotNone(response.items)

    def test_update_one(self):
        # get id of user with first_name = "Python1"
        with Directus(url, email, password) as directus:
            response: DirectusResponse = directus.items('directus_users') \
                .filter(Operators.Equals, first_name="Python1").read_many()
            user = response.items[0]
            response: DirectusResponse = directus.items('directus_users') \
                .update_one(user['id'], {"last_name": f"Updated {datetime.now()}"})
            print(response.errors)

    def test_update_many(self):
        # get id of user with first_name = "Python1"
        with Directus(url, email, password) as directus:
            response: DirectusResponse = directus.items('directus_users') \
                .filter(Operators.Contains, first_name="Python").read_many()
            ids = list(map(lambda x: x['id'], response.items))
            response: DirectusResponse = directus.items('directus_users') \
                .update_many(ids, {"last_name": f"Updated {datetime.now()}"})
            print(response.errors)

    def test_delete_one(self):
        # get id of user with first_name = "Python1"
        with Directus(url, email, password) as directus:
            response: DirectusResponse = directus.items('directus_users') \
                .filter(Operators.Equals, first_name="Python1").read_many()
            user = response.items[0]
            response: DirectusResponse = directus.items('directus_users') \
                .delete_one(user['id'])
            print(response.errors)

    def test_delete_many(self):
        # get id of user with first_name = "Python1"
        with Directus(url, email, password) as directus:
            response: DirectusResponse = directus.items('directus_users') \
                .filter(Operators.Contains, first_name="Python").read_many()
            ids = list(map(lambda x: x['id'], response.items))
            response: DirectusResponse = directus.items('directus_users') \
                .delete_many(ids)
            print(response.errors)


if __name__ == '__main__':
    unittest.main()
