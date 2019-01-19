from django.db import models
from .constants import MAX_TITLE_LEN, MAX_PRICE_DIGITS

class Product(models.Model):
    """ Django product model. 
        Note that each product is assigned an unique id 
        by Django. """

    title = models.CharField(max_length=MAX_TITLE_LEN, default="")
    price = models.DecimalField(max_digits=MAX_PRICE_DIGITS, decimal_places=2, default=0)
    inventory_count = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.title

    def purchase(self, qty=1) -> None:

        self.inventory_count -= qty


