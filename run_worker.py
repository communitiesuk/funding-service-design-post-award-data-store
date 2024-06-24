from app import app
from background_download import app as procrastinate_app

with app.app_context():
    procrastinate_app.run_worker(
        queues=[
            "download",
        ],
        name="download-worker",
    )
