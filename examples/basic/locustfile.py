from locust import HttpUser, task, between


class BasicUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @task(5)
    def ok(self):
        self.client.get("/status/200", name="ok")

    @task(1)
    def delayed(self):
        self.client.get("/delay/0.1", name="delay")


