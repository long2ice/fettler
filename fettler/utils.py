import datetime
import json
from decimal import Decimal

import ciso8601

CONVERTERS = {
    "date": ciso8601.parse_datetime,
    "datetime": ciso8601.parse_datetime,
    "decimal": Decimal,
}


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {"val": obj.strftime("%Y-%m-%d %H:%M:%S"), "_spec_type": "datetime"}
        elif isinstance(obj, datetime.date):
            return {"val": obj.strftime("%Y-%m-%d"), "_spec_type": "date"}
        elif isinstance(obj, Decimal):
            return {"val": str(obj), "_spec_type": "decimal"}
        else:
            return super().default(obj)


def object_hook(obj):
    _spec_type = obj.get("_spec_type")
    if not _spec_type:
        return obj

    if _spec_type in CONVERTERS:
        return CONVERTERS[_spec_type](obj["val"])
    else:
        raise TypeError("Unknown {}".format(_spec_type))


def is_match_filters(values: dict, filters: dict) -> bool:
    """
    values is match filters or not
    :param values:
    :param filters:
    example:
        {
             "id": 1,
             "num": ["AND", ["GT", 1], ["LT", 1]]
        }
    all comparison operators: GT,GTE,LT,LTE,!EQ
    all logic operators: AND,OR
    :return:
    """
    for field, filter_ in filters.items():
        value = values[field]
        if isinstance(filter_, str):
            ret = value == filter_
            if not ret:
                return False
        elif isinstance(filter_, list):
            logic = filter_[0]
            operators = filters[1:]
            rets = []
            for operator in operators:
                op, exists_value = operator
                if op == "GT":
                    rets.append(value > exists_value)
                elif op == "GTE":
                    rets.append(value >= exists_value)
                elif op == "LT":
                    rets.append(value < exists_value)
                elif op == "LTE":
                    rets.append(value <= exists_value)
                elif op == "!EQ":
                    rets.append(value != exists_value)
            if logic == "AND":
                if not all(rets):
                    return False
            elif logic == "OR":
                if not any(rets):
                    return False
    return True
