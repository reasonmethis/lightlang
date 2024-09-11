import asyncio
from concurrent.futures import ThreadPoolExecutor

# NOTE: consider using async_to_sync from asgiref.sync library


def run_task_sync(task):
    """
    Run an asyncio task (more precisely, a coroutine object, such as the result of
    calling an async function) synchronously.
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, task)
        return future.result()


def make_sync(async_func):
    """
    Make an asynchronous function synchronous.
    """

    def wrapper(*args, **kwargs):
        return run_task_sync(async_func(*args, **kwargs))

    return wrapper


def gather_tasks_sync(tasks):
    """
    Run a list of asyncio tasks synchronously.
    """

    async def coroutine_from_tasks():
        return await asyncio.gather(*tasks)

    return run_task_sync(coroutine_from_tasks())
