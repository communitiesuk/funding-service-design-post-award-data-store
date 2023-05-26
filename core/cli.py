import requests


def create_cli(app):
    """Create command-line interface (CLI) commands for the Flask application.

    This function creates CLI commands for the Flask application.

    :param app: The Flask application object.
    """

    @app.cli.command("seed")
    def seed_db_cmd():
        """CLI command to seed the database with data from an Excel file.

        Example usage:
            flask seed
        """
        url = "http://localhost:8080/ingest"
        file_path = r"tests/controller_tests/resources/DLUCH_Data_Model_V3.4_EXAMPLE.xlsx"

        with open(file_path, "rb") as file:
            files = {
                "excel_file": (file.name, file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            }

            response = requests.post(url, files=files, data={"schema": "towns_fund"})

            if response.status_code == 200:
                print("File uploaded successfully.")
            else:
                print("File upload failed:", response.text)
