from locust import HttpUser, task, between


class FailingUser(HttpUser):
    wait_time = between(0.1, 0.2)

    @task
    def fail(self):
        self.client.get("/status/500", name="fail")
