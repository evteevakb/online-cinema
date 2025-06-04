import logging
import time

from clickhouse import ClickHouseLoader
from test_data import TestData, FilmFrame
from vertica import VerticaLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)

def compare_read_speed(clickhouse_loader, vertica_loader):
    logger.info("\n[Step 3] Comparing read speeds with sample...")

    start = time.time()
    _ = clickhouse_loader.read_sample('film_frame', limit=1000)
    logger.info(f"ClickHouse read (LIMIT 1000): {time.time() - start:.5f} seconds")

    start = time.time()
    _ = vertica_loader.read_sample('film_frame', limit=1000)
    logger.info(f"Vertica read (LIMIT 1000): {time.time() - start:.5f} seconds")


def compare_insert_while_loading(clickhouse_loader, vertica_loader, test_data):
    logger.info("\n[Step 4] Comparing insert + read speeds during concurrent loading...")

    for i, batch in enumerate(test_data.generate_data_multiprocessing(), start=1):
        start_ch_insert = time.time()
        clickhouse_loader.insert_batch('film_frame', fields=FilmFrame.model_fields.keys(), batch=batch)
        ch_insert_time = time.time() - start_ch_insert

        start_ch_read = time.time()
        _ = clickhouse_loader.read_sample('film_frame', limit=100)
        ch_read_time = time.time() - start_ch_read

        start_vt_insert = time.time()
        vertica_loader.insert_batch('film_frame', fields=FilmFrame.model_fields.keys(), batch=batch)
        vt_insert_time = time.time() - start_vt_insert

        start_vt_read = time.time()
        _ = vertica_loader.read_sample('film_frame', limit=100)
        vt_read_time = time.time() - start_vt_read

        logger.info(
            f"[Batch {i}] ClickHouse - insert: {ch_insert_time:.5f}s, read: {ch_read_time:.5f}s | "
            f"Vertica - insert: {vt_insert_time:.5f}s, read: {vt_read_time:.5f}s"
        )


def main():
    test_data = TestData(FilmFrame)
    clickhouse_loader = ClickHouseLoader()
    vertica_loader = VerticaLoader()

    # 1. Create dbs and tables
    clickhouse_loader.create_tables(['film_frame'])
    vertica_loader.create_tables(['film_frame'])

    # 2. Load data in both dbs
    for i, batch in enumerate(test_data.generate_data_multiprocessing(), start=1):
        clickhouse_loader.insert_batch(table='film_frame', fields=FilmFrame.model_fields.keys(), batch=batch)
        vertica_loader.insert_batch(table='film_frame', fields=FilmFrame.model_fields.keys(), batch=batch)
        logger.info(f'[Inserted batch №{i}]')

    # 3. Compare speed of read and insert with loaded data
    compare_read_speed(clickhouse_loader, vertica_loader)

    # 4. Compare speed of read and insert while loading new data
    test_data_concurrent = TestData(FilmFrame, size=100_000)
    compare_insert_while_loading(clickhouse_loader, vertica_loader, test_data_concurrent)


if __name__ == "__main__":
    start = time.time()
    main()
    logger.info(f"\nDone in {time.time() - start:.5f} seconds")
