from inventory.models import Product
from inventory.constants import MAX_TITLE_LEN

from django.db.models.query import *
from decimal import *
from typing import Tuple

class ProductSearch:
    """
    Represents a Product search by filter parameters. All parameters
    are optional, a search with no parameters will return every
    Product in inventory.

    uses Django filters to implement Product filtering.

    Attributes
    ----------

    min_qty: int
        positive integer, defaults to 0. minimum inventory count 
        required for product to appear in search.

    title: str
        part or whole of product title. defaults to empty string,
        which will match any product.
        will be truncated if longer than MAX_TITLE_LEN

    price_range: Tuple[Decimal, Decimal]
        inclusive price interval for product search.
    
    """
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

        """
        Perform search with current parameters.

        return a QuerySet with every matching Product. 
        """

        match = Product.objects.filter(inventory_count__gte=self.min_qty)

        if self.title is not None:
            match = match.filter(title__contains=self.title)

        if self.price_range is not None:
            match = match.filter(price__range=self.price_range)

        return match
