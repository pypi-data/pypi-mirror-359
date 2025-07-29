import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent.parent))
from src.jsonblob import JSONBlobClient, JSONBlobStorage


def test1():
    json_blob_client = JSONBlobClient()
    blob_id = json_blob_client.create({})
    json_blob_client.update(blob_id, {"Hello": "World"})
    data = json_blob_client.get(blob_id)
    print(data)


def test2():
    keys_blob_id = JSONBlobStorage.create()
    json_blob_storage = JSONBlobStorage(keys_blob_id)
    print(json_blob_storage.keys_blob_id)
    print(json_blob_storage.keys)
    is_new_key = json_blob_storage.set("zebra", {"Hello": "World"})
    print(is_new_key)


def test3():
    keys_blob_id = "1389494844103254016"
    json_blob_storage = JSONBlobStorage(keys_blob_id)
    print(json_blob_storage.keys)
    data = json_blob_storage.get("zebra")
    print(data)
    is_new_key = json_blob_storage.set("zebra", {"Say": "Love"})
    print(is_new_key)


if __name__ == "__main__":
    test3()
