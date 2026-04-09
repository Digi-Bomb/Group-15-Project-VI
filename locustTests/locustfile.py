from locust import HttpUser, task, between
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class BookEZUser(HttpUser):
    wait_time = between(1.0, 2.3)
    
    def on_start(self):
        response = self.client.get("/login")
        csrf_token = self.extract_csrf(response.text)

        self.client.post("/login", data={
            "username": "testuser1",
            "password": "password",
            "csrf_token": csrf_token
        })

    @task(5)
    def view_homepage(self):
        self.client.get("/")

    @task(3)
    def view_profile(self):
        self.client.get("/profile")

    @task(1)
    def create_booking(self):
        response = self.client.get("/booking?room_number=2A11")
        csrf_token = self.extract_csrf(response.text)
        start_str = self.current_booking_time.strftime("%H:%M")
        end_time_obj = self.current_booking_time + timedelta(minutes=1)
        end_str = end_time_obj.strftime("%H:%M")
        self.client.post("/booking?room_number=2A10", data={
            "meeting_date": "2026-04-08",
            "start_time": start_str,
            "end_time": end_str,
            "meeting_capacity": "3",
            "csrf_token": csrf_token
        })
        self.current_booking_time = end_time_obj
        if self.current_booking_time.hour >= 20:
            self.current_booking_time = datetime.strptime("08:00", "%H:%M")

    def on_stop(self):
        response = self.client.get("/")
        csrf_token = self.extract_csrf(response.text)
        
        self.client.post("/logout", data={
            "csrf_token": csrf_token
        })

    def extract_csrf(self, html_content):
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            token = soup.find("input", {"id": "csrf_token"})["value"]
            return token
        except TypeError:
            return ""