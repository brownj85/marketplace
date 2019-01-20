from django.test import TestCase
from inventory.search import ProductSearch
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

    def test_query_min_inv(self):
        srch = ProductSearch(1)

        qset = srch.query()

        for prod in qset:
            self.assertTrue(prod.inventory_count >= 1)

    def test_query_full_title(self):
        srch = ProductSearch(title="Persian Rug")

        qset = srch.query()

        self.assertEqual(len(qset), 1)
        self.assertEqual(qset[0].title, "Persian Rug")


    def test_query_partial_title_exact_match(self):
        srch = ProductSearch(title="wat")

        qset = srch.query()

        self.assertEqual(qset[0].title, "Water")
        self.assertEqual(len(qset), 1)

    def test_query_partial_title_multiple_match(self):
        srch = ProductSearch(title="Car")

        qset=srch.query()

        for prod in qset:
            self.assertIn("Car", prod.title)


    def test_query_price_range(self):
        srch = ProductSearch(price_range=(2, 3))

        qset = srch.query()

        for prod in qset:
            self.assertTrue(2 <= prod.price <= 3)


    def test_query_title_match_price_mismatch(self):
        srch = ProductSearch(title="Persian Rug", price_range=(0, 100))

        qset = srch.query()

        self.assertEqual(len(qset), 0)


    def test_query_price_match_title_mismatch(self):
        srch = ProductSearch(title="Widgets", price_range=(2, 3))

        qset = srch.query()

        self.assertEqual(len(qset), 0)


from cart.cart import Cart

class TestCartMethods(TestCase):

    fixtures = ['sample.json']

    def test_add_product_simple(self):
        water = ProductSearch(title="Water").query()[0]
        c = Cart()

        self.assertEqual(c.add_product(water), 1)

        self.assertEqual(len(c.entries), 1)
        
        for key, entry in c.entries.items():
            self.assertEqual(key, entry.product.id)
            self.assertTrue(entry.qty <= water.inventory_count)
            self.assertEqual(entry.product.title, "Water")
            self.assertEqual(entry.qty, 1)
            self.assertEqual(c.total, 1.50)

    def test_add_product_twice(self):
        water = ProductSearch(title="Water").query()[0]
        c = Cart()

        self.assertEqual(c.add_product(water), 1)
        self.assertEqual(c.add_product(water), 2)

        self.assertEqual(len(c.entries), 1)
        
        for key, entry in c.entries.items():
            self.assertEqual(key,entry.product.id)
            self.assertTrue(entry.qty <= water.inventory_count)
            self.assertEqual(entry.product.title, "Water")
            self.assertEqual(entry.qty, 2)
            self.assertEqual(c.total, water.price * 2)

    def test_add_product_multiple(self):
        water = ProductSearch(title="Water").query()[0]
        laptop = ProductSearch(title="Laptop").query()[0]
        c = Cart()

        self.assertEqual(c.add_product(product=water, qty=3), 3)
        self.assertEqual(c.add_product(product=laptop, qty=10), 10)

        self.assertEqual(c.entries[water.id].qty, 3)
        self.assertEqual(c.entries[laptop.id].qty, 10)
        self.assertEqual(c.total, laptop.price * 10 + water.price * 3)
        self.assertEqual(len(c.entries), 2)

    def test_remove_one_of_product(self):

        water = ProductSearch(title="Water").query()[0]
        c = Cart()

        c.add_product(product=water, qty=3)

        self.assertEqual(c.remove_product(water, 1), 2)
        self.assertEqual(len(c.entries), 1)
        self.assertEqual(c.entries[water.id].qty, 2)
        self.assertEqual(c.total, water.price * 2)


    def test_remove_all_product(self):
        
        water = ProductSearch(title="Water").query()[0]
        c = Cart()

        self.assertEqual(c.add_product(water), 1)
        self.assertEqual(c.remove_product(water), 0)
        self.assertEqual(len(c.entries), 0)
        self.assertEqual(c.total, 0)


    def test_add_more_than_available(self):

        rug = ProductSearch(title="Persian Rug").query()[0]

        c = Cart()

        self.assertEqual(c.add_product(product=rug, qty = 5), 2)
        self.assertEqual(len(c.entries), 1)

        self.assertEqual(c.entries[rug.id].qty, 2)
        self.assertEqual(c.total, rug.price * 2)


    def test_remove_more_than_entry_qty(self):

        laptop = ProductSearch(title="Laptop").query()[0]
        water = ProductSearch(title="Water").query()[0]
        
        c = Cart()

        c.add_product(laptop, 10)
        c.add_product(water, 43)

        self.assertEqual(c.remove_product(laptop, 15), 0)

        self.assertEqual(len(c.entries), 1)
        self.assertEqual(c.total, water.price * 43)


    def test_complete_valid_cart(self):
        prods = ProductSearch(1).query()
        c = Cart()

        for prod in prods:
            c.add_product(prod, prod.inventory_count)

        self.assertTrue(c.complete_cart())


    def test_complete_invalid_cart(self):
        water = ProductSearch(title="Water").query()[0]
        c = Cart()
        c.add_product(water, 5)

        prods = ProductSearch(1).query()
        for prod in prods:
            c.add_product(prod, prod.inventory_count)

        water.purchase(water.inventory_count)

        self.assertFalse(c.complete_cart())        
