import requests
from urllib.parse import urlparse
import json

import logging

logger = logging.getLogger(__name__)


class JSONBlobClient:
    # Blob is removed after 30 days of inactivity
    # Approximately
    CONTENT_LENGTH_LIMIT = 1500503  # response.headers.get("Content-Length")

    def __init__(self):
        self.api_url = "https://jsonblob.com/api/jsonBlob"

    def create(self, data: dict) -> str:
        response = requests.post(self.api_url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        response.raise_for_status()

        location = response.headers.get("Location")
        new_blob_id = urlparse(location).path.split("/")[-1]
        return new_blob_id

    def update(self, blob_id: str, data: dict) -> bool:
        response = requests.put(
            f"{self.api_url}/{blob_id}", headers={"Content-Type": "application/json"}, data=json.dumps(data)
        )
        response.raise_for_status()

    def get(self, blob_id: str) -> dict:
        response = requests.get(f"{self.api_url}/{blob_id}")
        response.raise_for_status()
        data = response.json()
        return data


class JSONBlobStorage:

    def __init__(self, keys_blob_id: str = None):
        self.json_blob_client = JSONBlobClient()
        self.keys = {}
        self.keys_blob_id = keys_blob_id

        self.keys = self.json_blob_client.get(self.keys_blob_id)
        assert isinstance(self.keys, dict), f"Something wrong with keys: {self.keys}"

    @staticmethod
    def create() -> str:
        json_blob_client = JSONBlobClient()
        keys_blob_id = json_blob_client.create({})
        return keys_blob_id

    def set(self, key: str, value: dict) -> bool:
        is_new_key = False
        blob_id = self.keys.get(key)
        if blob_id:
            self.json_blob_client.update(blob_id, value)
        else:
            blob_id = self.json_blob_client.create(value)
            assert blob_id
            self.keys[key] = blob_id
            # Update keys
            self.json_blob_client.update(self.keys_blob_id, self.keys)
            is_new_key = True
        return is_new_key

    def get(self, key: str) -> dict:
        blob_id = self.keys.get(key)
        assert blob_id, f"Key '{key}' is missing"

        return self.json_blob_client.get(blob_id)
