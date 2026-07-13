"""Locust performance tests for EduGenie."""
from locust import HttpUser, between, task


class EduGenieUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(3)
    def landing_page(self):
        self.client.get("/", name="GET /")

    @task(2)
    def health_check(self):
        self.client.get("/health", name="GET /health")

    @task(2)
    def login_page(self):
        self.client.get("/login", name="GET /login")

    @task(1)
    def docs_page(self):
        self.client.get("/docs", name="GET /docs")
