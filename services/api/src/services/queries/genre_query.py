class GenreElasticQueryBuilder:
    @staticmethod
    async def get_genre_search_query(page_size: int = 50, page_number: int = 1):
        query = {
            "query": {"match_all": {}},
            "sort": [{"name.keyword": "asc"}],
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }
        return query
