import asyncio

import pytest


def pytest_pycollect_makeitem(collector, name, obj):
    """
    Fix pytest collecting for coroutines.
    """
    if collector.funcnamefilter(name) and asyncio.iscoroutinefunction(obj):
        obj = pytest.mark.asyncio(obj)
        return list(collector._genfunctions(name, obj))


@pytest.fixture(scope="function")
def pool(event_loop):
    from asyncpgsa import create_pool

    from . import DB_NAME, HOST, PASS, PORT, USER

    pool = create_pool(
        min_size=1,
        max_size=3,
        host=HOST,
        port=PORT,
        user=USER,
        password=PASS,
        database=DB_NAME,
        timeout=1,
        loop=event_loop,
    )

    event_loop.run_until_complete(pool)

    try:
        yield pool
    finally:
        event_loop.run_until_complete(pool.close())


@pytest.fixture(scope="function")
def connection(pool, event_loop):
    conn = event_loop.run_until_complete(pool.acquire(timeout=2))

    try:
        yield conn
    finally:
        event_loop.run_until_complete(pool.release(conn))
