from inventory.models import Product
from inventory.constants import MAX_TITLE_LEN

from django.db.models.query import *
from decimal import *
from typing import Tuple

class ProductSearch:

    def __init__(self,
            min_qty: int=0,
            title: str="",
            price_range: Tuple[Decimal, Decimal]=None):

        if len(title) > MAX_TITLE_LEN:
            title = title[0:MAX_TITLE_LEN]

        self.title = title
        self.price_range = price_range
        self.min_qty = min_qty


    def query(self) -> QuerySet:

        match = Product.objects.filter(inventory_count__gte=self.min_qty)

        if self.title is not None:

            match = match.filter(title__contains=self.title)

        if self.price_range is not None:
            match = match.filter(price__range=self.price_range)

        return match
