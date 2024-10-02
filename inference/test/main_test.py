from utils  import parse_filters

# content of test_class.py
class TestParseFilters:
    def test_filter_all(self):
        condition = {"price":3, "bathrooms": 10}
        parsed_filters = parse_filters(condition)
        expected_filters = {'price': {'$lte': 3}, 'bathrooms': {'$eq': 10}}

        assert parsed_filters == expected_filters

    def test_filter_None(self):
        condition = {"price":3, "bathrooms": None}
        parsed_filters = parse_filters(condition)
        expected_filters = {'price': {'$lte': 3}}

        assert parsed_filters == expected_filters