import datetime
import json

from .models import Order


def generate_order_number(pk: int):
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%S")
    order_number = current_datetime + str(pk)
    return order_number


def get_order_by_vendor(order: Order, vendor_id: int) -> dict:
    sub_total = 0
    tax = 0
    tax_dict = {}
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    for key, val in data.items():
        sub_total += float(key)
        val = val.replace("'", '"')
        val = json.loads(val)
        tax_dict.update(val)

        for i in val:
            for j in val[i]:
                tax += float(val[i][j])
    grand_total = float(sub_total) + float(tax)
    context = {
        "sub_total": sub_total,
        "tax": tax,
        "tax_dict": tax_dict,
        "grand_total": grand_total,
    }

    return context
