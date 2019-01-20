from inventory.models import Product
from typing import Dict, NamedTuple
from decimal import Decimal


class CartEntry:
    """ Class representing a single product entry in a shopping cart.
    """

    product: 'Product'
    qty: int

    def __init__(self, product: 'Product', qty: int) -> 'CartEntry':
        
        assert (qty >= 0), "qty cannot be less than 0"

        self.product = product
        self.qty = qty

    def __str__(self) -> str:
        return " : ".join((str(self.qty), str(self.product)))

    def is_valid(self) -> bool:
        """
        verify whether a given entry is valid, i.e purchasable
        """
        return self.qty <= self.product.inventory_count

    def sub_total(self) -> Decimal:
        return self.product.price * self.qty


class Cart:
    """ Class representing a shopping cart.

        
        Attributes
        ----------

        entries: Dict[int, CartEntry]
            the products contained in the cart, keyed
            by the product id of the product in CartEntry

        total: Decimal
            the total cost of all products in the shopping cart

    """

    entries: Dict[int, 'CartEntry']
    total: Decimal

    def __init__(self) -> None:
        self.entries = {}
        self.total = 0

    def __str__(self) -> str:
        str_list = []

        for entry in self.entries.values():
            str_list.append(str(entry))

        str_list.append(str(self.total))

        return "\n".join(str_list)

    def __edit_entry(self, entry: 'CartEntry', d_qty: int) -> int:

        """
        if the sum of d_qty and entry.qty is <= 0, 
        remove entry from self.entries.

        otherwise, set entry.qty to the maximum of the sum
        or entry.product.inventory_count.

        return the new quantity of the given entry

        Arguments
        ---------

        entry: an entry in this cart's entries dict.

        d_qty: an integer

        """

        old_sub_total = entry.sub_total()
        new_qty = max(0, entry.qty + d_qty)

        if new_qty > entry.product.inventory_count:
            new_qty = entry.product.inventory_count

        entry.qty = new_qty
        self.total += (entry.sub_total() - old_sub_total)

        if new_qty == 0:
            self.entries.pop(entry.product.id)

        return new_qty


    def add_product(self, product: Product, qty: int=1) -> int:
        """
        add at the minimum of qty, product.inventory_count of 
        product to cart.

        return the number of the given product contained in 
        the cart after adding.

        Arguments
        ---------

        product: a product

        qty: a postive integer

        """
        if not product.id in self.entries:
            entry = CartEntry(product, 0)
            self.entries[product.id] = entry

        else:
            entry = self.entries[product.id]

        return self.__edit_entry(entry, qty)

    
    def remove_product(self, product: Product, qty: int=1) -> int:
        """
        remove the maximum of qty, and the current number of product in 
        this cart, to cart.

        return the number of the given product contained in the cart after
        removing

        Arguments
        ---------

        product: a product

        qty: a positive integer
        """
        return self.add_product(product, -qty)

    
    def validate(self) -> Dict[int, 'CartEntry']:
        """
        check each entry in the cart for validity,
        i.e. whether it is purchasable or not.

        return a dict containg every invalid entry
        """
        invalid = {}

        for key, entry in self.entries.items():
            if not entry.is_valid():
                invalid[key] = entry

        return invalid

    def complete_cart(self) -> bool:
        """
        if cart is valid, purchase each item and return True.

        otherwise, do nothing and return False.
        """

        if not len(self.validate()) == 0:
            return False

        for prod_id in self.entries:
            entry = self.entries[prod_id]

            entry.product.purchase(entry.qty)

        return True        
