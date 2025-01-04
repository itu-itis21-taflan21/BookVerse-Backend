from locust import HttpUser, task, between, events
import random
import string
import json

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class DjangoAPIUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://54.160.153.61:8000/"  

    def on_start(self):
        self.email = "metaflan@hotmail.com"
        self.password = "hello123"

        login_payload = {
            "email": self.email,
            "password": self.password
        }

        response = self.client.post("login/", json=login_payload)
        if response.status_code == 200 and "access" in response.json():
            self.token = response.json()["access"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"User {self.email} logged in successfully.")
        else:
            self.token = None
            self.headers = {}
            print(f"Failed to log in user {self.email}: {response.text}")

    @task(3)
    def list_books(self):
        self.client.get("get-book/", headers=self.headers)

    @task(2)
    def book_details(self):
        book_id = random.randint(1, 100)
        self.client.get(f"/get-book/?book_id={book_id}", headers=self.headers)

    def on_stop(self):
        if self.token:
            response = self.client.get("logout/", headers=self.headers)
            if response.status_code == 204:
                print(f"User {self.username} logged out successfully.")
            else:
                print(f"Failed to log out user {self.username}: {response.text}")
