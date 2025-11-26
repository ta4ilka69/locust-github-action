import random
import string
from threading import Lock
from locust import HttpUser, task, between


_ids_lock = Lock()
_ids = []


def _rand_name() -> str:
    return "prod-" + "".join(random.choice(string.ascii_lowercase) for _ in range(6))


class StoreUser(HttpUser):
    wait_time = between(0.05, 0.15)

    @task(5)
    def list_products(self):
        self.client.get("/products", name="GET /products")

    @task(3)
    def create_and_get(self):
        name = _rand_name()
        price = round(random.uniform(1.0, 100.0), 2)
        r = self.client.post("/products", json={"name": name, "price": price}, name="POST /products")
        if r.status_code == 201:
            pid = r.json().get("id")
            if isinstance(pid, int):
                with _ids_lock:
                    _ids.append(pid)
                self.client.get(f"/products/{pid}", name="GET /products/:id")

    @task(1)
    def update_or_delete(self):
        with _ids_lock:
            pid = random.choice(_ids) if _ids else None
        if pid is None:
            return
        if random.random() < 0.5:
            self.client.put(f"/products/{pid}", json={"price": round(random.uniform(1.0, 100.0), 2)}, name="PUT /products/:id")
        else:
            r = self.client.delete(f"/products/{pid}", name="DELETE /products/:id")
            if r.status_code in (200, 204, 404):
                with _ids_lock:
                    try:
                        _ids.remove(pid)
                    except ValueError:
                        pass


