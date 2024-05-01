from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """ Vartotojo prisijungimo simuliacija """
        self.client.post("/login", {
            "username": "testuser",
            "password": "testpass"
        })

    @task
    def create_quiz(self):
        """ Quiz kūrimas """
        self.client.post("/create_quiz", {
            "title": "Sample Quiz",
            "description": "General Knowledge"
        })

    @task(2)
    def view_main_page(self):
        """ Pagrindinio puslapio peržiūra """
        self.client.get("/")

    @task(3)
    def register(self):
        """ Naujo vartotojo registracija """
        self.client.post("/register", {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "confirm password": "newpassword",
            "name": "John",
            "surname": "Doe"
        })

    def on_stop(self):
        """ Atsijungimas nuo sistemos """
        self.client.get("/logout")
