from inventory.models import Product
from typing import Dict, NamedTuple
from decimal import Decimal

class CartEntry:

    product: 'Product'
    qty: int

    def __init__(self, product: 'Product', qty: int) -> 'CartEntry':
        
        assert (qty >= 0), "qty cannot be less than 0"

        self.product = product
        self.qty = qty

    def __str__(self) -> str:
        return " : ".join((str(self.qty), str(self.product)))

    def is_valid(self) -> bool:
        return self.qty <= self.product.inventory_count

    def sub_total(self) -> Decimal:
        return self.product.price * self.qty


class Cart:

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

        if not product.id in self.entries:
            entry = CartEntry(product, 0)
            self.entries[product.id] = entry

        else:
            entry = self.entries[product.id]

        return self.__edit_entry(entry, qty)

    
    def remove_product(self, product: Product, qty: int=1) -> int:
        return self.add_product(product, -qty)

    
    def validate(self) -> bool:
        invalid = {}

        for key, entry in self.entries.items():
            if not entry.is_valid():
                invalid[key] = entry

        return len(invalid) == 0

    def complete_cart(self) -> bool:

        if not self.validate():
            return False

        for prod_id in self.entries:
            entry = self.entries[prod_id]

            entry.product.purchase(entry.qty)

        return True



        
