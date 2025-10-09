from snowflake import SnowflakeGenerator
from app.config import settings
from app.utils import set_snowflake_generator

workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
bind = f"{settings.HOST}:{settings.PORT}"
reload = True


def post_fork(server, worker):
    worker_id = worker.pid % 1024
    gen = SnowflakeGenerator(worker_id)
    set_snowflake_generator(gen)
    print(
        f"Worker PID {worker.pid} snowflake generator initialized with worker id {worker_id}"
    )
