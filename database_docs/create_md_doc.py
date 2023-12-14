import json
import os


def create_md_from_json():
    current_directory = os.path.dirname(os.path.realpath(__file__))

    json_file_path = f"{current_directory}/doc_base.json"

    readme_file_path = f"{current_directory}/README.md"

    with open(json_file_path, "r") as json_file:
        json_data = json.load(json_file)

    with open(readme_file_path, "w") as readme_file:
        readme_file.write("# Database Descriptions\n\n")

        for section, details in json_data.items():
            readme_file.write(f"## {section}\n\n")
            for key, value in details.items():
                readme_file.write(f"### {key}\n\n")
                readme_file.write(f"{value}\n\n")

    print(f"README has been created at {readme_file_path}")


if __name__ == "__main__":
    create_md_from_json()
