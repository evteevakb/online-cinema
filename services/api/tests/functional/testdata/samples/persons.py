import uuid
import random

from faker import Faker


fake = Faker()

person_id = str(uuid.uuid4())
name = str(fake.name())
person_sample = [
    {
        "id": person_id,
        "full_name": name
    }
]

film_sample = [
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": round(random.uniform(1, 10), 2),
        "genres": [{"id": str(uuid.uuid4()), "name": "Drama"}],
        "title": "Some Film Title",
        "description": "A drama film.",
        "directors_names": [],
        "actors_names": [name],
        "writers_names": [],
        "directors": [],
        "actors": [{"id": person_id, "name": name}],
        "writers": []
    },
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": round(random.uniform(1, 10), 2),
        "genres": [{"id": str(uuid.uuid4()), "name": "Comedy"}],
        "title": "Laugh Till Dawn",
        "description": "A group of friends embarks on a wild night of misadventures..",
        "directors_names": [],
        "actors_names": [name],
        "writers_names": [],
        "directors": [],
        "actors": [{"id": person_id, "name": name}],
        "writers": []
    },
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": round(random.uniform(1, 10), 2),
        "genres": [{"id": str(uuid.uuid4()), "name": "Sci-Fi"}],
        "title": "Beyond the Stars",
        "description": "In a distant future, humanity reaches beyond its limits.",
        "directors_names": [],
        "actors_names": [str(fake.name())],
        "writers_names": [],
        "directors": [],
        "actors": [{"id": person_id, "name": name}],
        "writers": []
    }
]


person_sample_search = [
    {
        "id": str(uuid.uuid4()),
        "full_name": 'Kacey Arnold'
    },
    {
        "id": str(uuid.uuid4()),
        "full_name": str(fake.name())
    },
    {
        "id": str(uuid.uuid4()),
        "full_name": str(fake.name())
    },
]

film_sample_search = [
    {
        "id": str(uuid.uuid4()),
        "title": "Sample Movie",
        "imdb_rating": round(random.uniform(1, 10), 2),
        "actors": [
            {"id": str(uuid.uuid4()), "name": str(fake.name())},
            {"id": str(uuid.uuid4()), "name": str(fake.name())}
        ],
        "writers": [],
        "directors": []
    }
]