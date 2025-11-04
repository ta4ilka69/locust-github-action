from locust import HttpUser, task, between, tag


class TaggedUser(HttpUser):
    wait_time = between(0.1, 0.2)

    @task(5)
    @tag("fast")
    def ok(self):
        self.client.get("/status/200", name="ok")

    @task(1)
    @tag("slow")
    def delayed(self):
        self.client.get("/delay/0.05", name="delay")
