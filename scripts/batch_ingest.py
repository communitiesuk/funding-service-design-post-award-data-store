import argparse
import os

import requests


def post_file(file_path, endpoint_url):
    with open(file_path, "rb") as file:
        response = requests.post(
            endpoint_url,
            files={
                "excel_file": (file.name, file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            },
            data={"source_type": "tf_round_three"},
        )
    return response


def save_response(file_path, response, output_folder):
    file_name = os.path.basename(file_path)
    folder_name = os.path.splitext(file_name)[0]
    folder_path = os.path.join(output_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    response_file_path = os.path.join(folder_path, "response.txt")
    with open(response_file_path, "w") as file:
        file.write(response.text)


parser = argparse.ArgumentParser(description="Process files and post to an endpoint.")
parser.add_argument("directory_path", type=str, help="Path to the directory containing the files.")
parser.add_argument("endpoint_url", type=str, help="URL of the endpoint to post the files to.")
args = parser.parse_args()

output_folder = os.path.join(args.directory_path, "output")
os.makedirs(output_folder, exist_ok=True)

success_responses = []
failure_responses = []

dir_items = os.listdir(args.directory_path)
for idx, file_name in enumerate(dir_items):
    if file_name == "output":
        continue

    print(
        f"Testing file {idx}/{len(dir_items)} - {file_name}. \nSuccess ({len(success_responses)}), "
        f"Failed ({len(failure_responses)})"
    )

    file_path = os.path.join(args.directory_path, file_name)
    if os.path.isfile(file_path):
        response = post_file(file_path, args.endpoint_url)

        if response.status_code == requests.codes.ok:
            success_responses.append(file_name)
            print("Success.")
        else:
            failure_responses.append(file_name)
            save_response(file_path, response, output_folder)
            print("Failed.")
    print()

with open(os.path.join(output_folder, "success_responses.txt"), "w") as success_file:
    success_file.write("\n\n".join(success_responses))

with open(os.path.join(output_folder, "failure_responses.txt"), "w") as failure_file:
    failure_file.write("\n\n".join(failure_responses))
