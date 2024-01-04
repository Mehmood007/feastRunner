import datetime


def generate_order_number(pk: int):
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%S")
    order_number = current_datetime + str(pk)
    return order_number
