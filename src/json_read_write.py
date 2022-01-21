import json


def read_json(file_name):
    with open(file_name, "r") as fp:
        return json.load(fp)


def write_json(file_name, data):
    with open(file_name, "w") as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)