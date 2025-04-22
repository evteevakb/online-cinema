class FilmElasticQueryBuilder:

    @staticmethod
    async def get_film_search_query(
        query: str = None,
        genre: str = None,
        sort: str = None,
        page_size: int = 50,
        page_number: int = 1,
    ) -> dict:
        query_filters = []

        if query:
            query_filters.append(
                {"match": {"title": {"query": query, "fuzziness": "auto"}}}
            )

        if genre:
            query_filters.append(
                {
                    "nested": {
                        "path": "genres",
                        "query": {"term": {"genres.id": genre}},
                    }
                }
            )

        if query_filters:
            query_body = {"query": {"bool": {"must": query_filters}}}
        else:
            query_body = {"query": {"match_all": {}}}

        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("-")
            query_body["sort"] = [{field: {"order": order}}]

        from_ = (page_number - 1) * page_size
        query_body["from"] = from_
        query_body["size"] = page_size

        return query_body
