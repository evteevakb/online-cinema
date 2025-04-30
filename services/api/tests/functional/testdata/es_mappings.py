"""
Contains utilities for Elasticsearch index mappings.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class IndexMapping(BaseModel):
    """Mapping class for Elasticsearch index"""

    settings: dict[str, Any]
    mappings: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Converts the index mapping to a dictionary.

        Returns:
            dict[str, Any]: a dictionary representation of the index mapping.
        """
        return self.model_dump()


class ElasticMappings:
    """Class to manage Elasticsearch index mappings"""

    _mappings: dict[str, IndexMapping] = {}

    @classmethod
    def load_all(cls, mapping_dir: Path) -> None:
        """Loads all index mappings from JSON files in the specified directory.

        Args:
            mapping_dir (Path): path to the directory containing JSON mapping files.
        """
        for json_file in mapping_dir.glob("*.json"):
            index_name = json_file.stem
            with open(json_file) as f:
                data = json.load(f)
            cls._mappings[index_name] = IndexMapping(**data)

    @classmethod
    def get(cls, index_name: str) -> IndexMapping:
        """Retrieves the index mapping for a given index name.

        Args:
            index_name (str): name of the index.

        Returns:
            IndexMapping: corresponding mapping object.

        Raises:
            KeyError: if the mapping for the given index name is not found.
        """
        if index_name in cls._mappings:
            return cls._mappings[index_name]
        raise KeyError(f"Mapping for index '{index_name}' not found")

    @classmethod
    def __getattr__(cls, item: str) -> IndexMapping:
        """Allows attribute-style access to index mappings.

        Args:
            item (str): name of the index.

        Returns:
            IndexMapping: corresponding mapping object.

        Raises:
            AttributeError: if no mapping is found for the given index name.
        """
        if item in cls._mappings:
            return cls._mappings[item]
        raise AttributeError(f"No mapping found for index '{item}'")

    def __dir__(self) -> list[str]:
        """Lists available index names as attributes.

        Returns:
            list[str]: list of index names for which mappings are available.
        """
        return list(self._mappings.keys())
