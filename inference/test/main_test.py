# from main  import parse_filters


def parse_filters(json_filter):
    dict_operator = {"price": "$lte", "bathrooms": "$eq"}
    base_dict = {}
    for amenity, operator in dict_operator.items():
        add_dict = (
            {amenity: {operator: json_filter[amenity]}} if json_filter[amenity] else {}
        )
        base_dict = base_dict | add_dict

    return base_dict


# content of test_class.py
class TestParseFilters:
    def test_filter_all(self):
        condition = {"price": 3, "bathrooms": 10}
        parsed_filters = parse_filters(condition)
        expected_filters = {"price": {"$lte": 3}, "bathrooms": {"$eq": 10}}

        assert parsed_filters == expected_filters

    def test_filter_none(self):
        condition = {"price": 3, "bathrooms": None}
        parsed_filters = parse_filters(condition)
        expected_filters = {"price": {"$lte": 3}}

        assert parsed_filters == expected_filters
