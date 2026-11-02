# -*- coding: utf-8 -*-
"""各业务接口的语义化封装，用例只关心"做什么"而非"怎么拼 HTTP"。"""
import os


class UserApi:
    PATH_AUTH = "/api/user/auth"
    PATH_SEND_CODE = "/api/user/send-code"
    PATH_LOGOUT = "/api/user/logout"

    def __init__(self, client):
        self.c = client

    def login_by_password(self, account, password):
        return self.c.post(self.PATH_AUTH,
                           json={"account": account, "password": password})

    def send_code(self, email):
        return self.c.post(self.PATH_SEND_CODE, json={"email": email})

    def login_by_code(self, email, code):
        return self.c.post(self.PATH_AUTH,
                           json={"account": email, "verificationCode": code})

    def logout(self):
        return self.c.post(self.PATH_LOGOUT)


class FileApi:
    UPLOAD = "/api/file/upload/image"
    MY_IMAGES = "/api/file/my-images"
    SEARCH = "/api/file/search"
    EDIT = "/api/file/edit"
    MERGE = "/api/file/merge"

    def __init__(self, client):
        self.c = client

    def upload_image(self, filepath):
        name = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            return self.c.post(self.UPLOAD, files={"file": (name, f, "image/jpeg")})

    def upload_bytes(self, filename, content, content_type):
        return self.c.post(self.UPLOAD,
                           files={"file": (filename, content, content_type)})

    def my_images(self):
        return self.c.get(self.MY_IMAGES)

    def search_by_text(self, query):
        return self.c.post(self.SEARCH, data={"query": query})

    def search_by_image(self, filepath):
        name = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            return self.c.post(self.SEARCH, files={"file": (name, f, "image/jpeg")})

    def edit(self, image_url, instruction, timeout=None):
        return self.c.post(self.EDIT,
                           json={"image": image_url, "instruction": instruction},
                           timeout=timeout)

    def merge(self, image1_url, image2_url, instruction, timeout=None):
        return self.c.post(self.MERGE,
                           json={"image1": image1_url, "image2": image2_url,
                                 "instruction": instruction},
                           timeout=timeout)


class RecordApi:
    MY = "/api/record/my"

    def __init__(self, client):
        self.c = client

    def my(self, action=None):
        params = {"action": action} if action else None
        return self.c.get(self.MY, params=params)
