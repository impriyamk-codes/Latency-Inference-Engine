from locust import HttpUser, task, between

class FakeNewsUser(HttpUser):
    # 👇 This line prevents the "No Host" error
    host = "http://127.0.0.1:8000" 
    
    # Simulates a user waiting 1-3 seconds between clicks
    wait_time = between(1, 3)

    @task
    def predict_single(self):
        # 🚕 The Taxi: Sending 1 headline
        self.client.post("/predict", json={
            "text": "Breaking: Scientists discover that pizza is a vegetable."
        })

    @task
    def predict_batch(self):
        # 🚌 The Bus: Sending 5 headlines at once
        self.client.post("/predict_batch", json={
            "texts": [
                "Aliens land in New York",
                "Stock market crashes",
                "New AI robot takes over world",
                "Local cat wins mayor election",
                "Scientists invent teleportation"
            ]
        })