class PersonElasticQueryBuilder:

    @staticmethod
    async def get_films_by_person_uuid_query(person_uuid: str) -> dict:
        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.id": person_uuid}},
                            }
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.id": person_uuid}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.id": person_uuid}},
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
        }

        return query

    @staticmethod
    async def get_person_search_query(
        query: str, page_number: int = 1, page_size: int = 50, sort: str = None
    ) -> dict:
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["full_name^2", "alternative_name"],
                }
            },
            "from": (page_number - 1) * page_size,
            "size": page_size,
        }

        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("-")
            es_query["sort"] = [{f"{field}.keyword": {"order": order}}]

        return es_query
