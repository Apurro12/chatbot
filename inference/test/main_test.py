from filter_extractor import FilterExtractor

filter_extractor_instance = FilterExtractor()

# content of test_class.py
class TestParseFilters:
    def test_filter_all(self):
        condition = {"price": 3, "bathrooms": 10}
        parsed_filters = filter_extractor_instance.parse_filters(condition)
        expected_filters = {"price": {"$lte": 3}, "bathrooms": {"$eq": 10}}

        assert parsed_filters == expected_filters

    def test_filter_none(self):
        condition = {"price": 3, "bathrooms": None}
        parsed_filters = filter_extractor_instance.parse_filters(condition)
        expected_filters = {"price": {"$lte": 3}}

        assert parsed_filters == expected_filters
