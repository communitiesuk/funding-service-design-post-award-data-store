import time
from contextlib import contextmanager
from os import getpid

from celery import Task


def make_task(app):
    class FSDTask(Task):
        abstract = True
        start = None

        @property
        def queue_name(self):
            delivery_info = self.request.delivery_info or {}
            return delivery_info.get("routing_key", "none")

        @contextmanager
        def app_context(self):
            with app.app_context():
                yield

        def on_success(self, retval, task_id, args, kwargs):
            with self.app_context():
                elapsed_time = time.monotonic() - self.start

                app.logger.info(
                    "Celery task %s (task_id: %s, queue: %s) took %.4f",
                    self.name,
                    self.request.id,
                    self.queue_name,
                    elapsed_time,
                    extra={
                        "task_id": self.request.id,
                        "celery_task": self.name,
                        "queue_name": self.queue_name,
                        "time_taken": elapsed_time,
                        # avoid name collision with LogRecord's own `process` attribute
                        "process_": getpid(),
                    },
                )

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            with self.app_context():
                elapsed_time = time.monotonic() - self.start

                app.logger.exception(
                    "Celery task %s (task_id: %s, queue: %s) failed after %.4f",
                    self.name,
                    self.request.id,
                    self.queue_name,
                    elapsed_time,
                    extra={
                        "task_id": self.request.id,
                        "celery_task": self.name,
                        "queue_name": self.queue_name,
                        "time_taken": elapsed_time,
                        # avoid name collision with LogRecord's own `process` attribute
                        "process_": getpid(),
                    },
                )

        def __call__(self, *args, **kwargs):
            # ensure task has flask context to access config, logger, etc
            with self.app_context():
                self.start = time.monotonic()

                app.logger.info(
                    "Celery task %s (task_id: %s, queue: %s) starting",
                    self.name,
                    self.request.id,
                    self.queue_name,
                    extra={
                        "task_id": self.request.id,
                        "celery_task": self.name,
                        "queue_name": self.queue_name,
                        # avoid name collision with LogRecord's own `process` attribute
                        "process_": getpid(),
                    },
                )

                return super().__call__(*args, **kwargs)

    return FSDTask
