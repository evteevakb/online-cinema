modified_ids = """
SELECT DISTINCT id, 
       modified 
FROM content.{} 
WHERE modified > %(start_timestamptz)s 
AND modified <= %(stop_timestamptz)s 
ORDER BY modified 
LIMIT %(limit)s 
OFFSET %(offset)s;
"""

related_filmworks = """
SELECT fw.id, 
       fw.modified
FROM content.film_work AS fw 
LEFT JOIN content.{}_film_work rfw ON rfw.film_work_id = fw.id 
WHERE rfw.{}_id = ANY(%(ids)s)
ORDER BY fw.modified;
"""

filmworks_data = """
SELECT
  fw.id AS fw_id,
  fw.title,
  fw.description,
  fw.rating,
  fw.creation_date,
  COALESCE (
       json_agg(
            DISTINCT jsonb_build_object(
               'person_role', pfw.role,
               'person_id', p.id,
               'person_name', p.full_name
           )
       ) FILTER (WHERE p.id is not null),
       '[]'
   ) as persons,
  COALESCE (
       json_agg(
            DISTINCT jsonb_build_object(
               'genre_id', g.id,
               'genre_name', g.name
           )
       ) FILTER (WHERE g.id is not null),
       '[]'
   ) as genres
FROM content.film_work AS fw
LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person AS p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work AS gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre AS g ON g.id = gfw.genre_id
WHERE fw.id = ANY(%(ids)s)
GROUP BY fw.id;
"""

persons_data = """
SELECT p.id, p.full_name 
FROM content.person p
WHERE p.id = ANY(%(ids)s)
"""

genres_data = """
SELECT g.id, g.name
FROM content.genre g
WHERE g.id = ANY(%(ids)s)
"""
