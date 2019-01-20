from django.test import TestCase
from search import ProductSearch
from inventory.models import Product
from inventory.constants import *

class TestSearchMethods(TestCase):

    fixtures = ['sample.json']

    def test_title_truncated(self):

        srch = ProductSearch(0, 'a' * (MAX_TITLE_LEN *2))

        self.assertTrue(len(srch.title) == MAX_TITLE_LEN)


    def test_query_all(self):
        srch = ProductSearch()

        qset = srch.query()

        self.assertTrue(list(qset) == list(Product.objects.all()))

        print(qset)


    def test_query_min_inv(self):
        srch = ProductSearch(1)

        qset = srch.query()

        for prod in qset:
            self.assertTrue(prod.inventory_count >= 1)

    def test_query_full_title(self):
        srch = ProductSearch(title="Persian Rug")

        qset = srch.query()

        self.assertTrue(len(qset) == 1)
        self.assertTrue(qset[0].title == "Persian Rug")


    def test_query_partial_title_exact_match(self):
        srch = ProductSearch(title="wat")

        qset = srch.query()

        self.assertTrue(qset[0].title == "Water")
        self.assertTrue(len(qset) == 1)

    def test_query_partial_title_multiple_match(self):
        srch = ProductSearch(title="Car")

        qset=srch.query()

        for prod in qset:
            self.assertTrue("Car" in prod.title)


    def test_query_price_range(self):
        srch = ProductSearch(price_range=(2, 3))

        qset = srch.query()

        for prod in qset:
            self.assertTrue(2 <= prod.price <= 3)


    def test_query_title_match_price_mismatch(self):
        srch = ProductSearch(title="Persian Rug", price_range=(0, 100))

        qset = srch.query()

        self.assertTrue(len(qset) == 0)


    def test_query_price_match_title_mismatch(self):
        srch = ProductSearch(title="Widgets", price_range=(2, 3))

        qset = srch.query()

        self.assertTrue(len(qset) == 0)
