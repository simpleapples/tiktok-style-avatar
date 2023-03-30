from io import BytesIO
import urllib
from urllib.request import Request
import time
import requests
import uuid
import json
from requests_toolbelt import MultipartEncoder


class LarkHelper(object):
    _domain = "https://open.feishu.cn"

    def __init__(self, app_key, app_secret):
        self._app_key = app_key
        self._app_secret = app_secret
        self._access_token = ""
        self._expire = 0

    def _update_access_token(self):
        if self._access_token and time.time() < self._expire + 60:
            return None
        url = f"{self._domain}/open-apis/auth/v3/app_access_token/internal"
        data = {"app_id": self._app_key, "app_secret": self._app_secret}
        resp = requests.post(url, data=data)
        resp_json = resp.json()
        self._access_token = resp_json.get("app_access_token")
        self._expire = int(resp_json.get("expire")) + int(time.time())

    def download_img(self, msg):
        self._update_access_token()
        msg_obj = msg.get("event", {}).get("message", {})
        content_obj = json.loads(msg_obj.get("content", "{}"))
        img_key = ""
        if msg_obj.get("message_type") == "image":
            img_key = content_obj.get("image_key")
        elif msg_obj.get("message_type") == "post":
            for content_item in content_obj.get("content", []):
                for item in content_item:
                    if "image_key" in item:
                        img_key = item.get("image_key")
        if not img_key:
            return
        msg_id = msg_obj.get("message_id")
        url = f"{self._domain}/open-apis/im/v1/messages/{msg_id}/resources/{img_key}?type=image"
        req = Request(url)
        req.add_header("Authorization", f"Bearer {self._access_token}")
        data = urllib.request.urlopen(req).read()
        return data

    def upload_img(self, img):
        self._update_access_token()
        url = f"{self._domain}/open-apis/im/v1/images"
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        form = {
            "image_type": "message",
            "image": img_bytes,
        }
        multi_form = MultipartEncoder(form)
        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }
        headers["Content-Type"] = multi_form.content_type
        response = requests.request("POST", url, headers=headers, data=multi_form)
        return response.json().get("data", {}).get("image_key")

    def reply_img(self, msg_id, img_key):
        self._update_access_token()
        url = f"{self._domain}/open-apis/im/v1/messages/{msg_id}/reply"
        content = {"image_key": img_key}
        data = {
            "content": json.dumps(content),
            "uuid": str(uuid.uuid4()),
            "msg_type": "image",
        }
        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }
        requests.post(url, data=data, headers=headers)

    def reply_text(self, msg_id, text):
        self._update_access_token()
        url = f"{self._domain}/open-apis/im/v1/messages/{msg_id}/reply"
        data = {
            "content": json.dumps({"text": text}),
            "uuid": str(uuid.uuid4()),
            "msg_type": "text",
        }
        headers = {
            "Authorization": f"Bearer {self._access_token}",
        }
        resp = requests.post(url, data=data, headers=headers)
        print(resp.json())
