# BD

## Launching

### Requirements

- Python 3.11 or higher
- Docker (for dockerizing all parts of app as microservice)

### Starting Installation

1. Clone this repository.

```bash
git clone https://github.com/TiksGal/BD.git
```

2. Create virtual enviroment and activate it.

```bash
python -m venv .venv
```
```bash
source .venv/Scripts/activate
```

3. Install requirements from "requirements.txt" file.

```bash
pip install -r requirements.txt
```

### Executing the program

Go to the directory where you clone this repository and type this:

```bash
python run.py
```
 or this:

 ```bash
flask run
```

### Docker

If you want to dockerize this app you should follow these steps:

This command build the container.
```bash
docker compose build --no-cache
```
This command run it.
```bash
docker compose up
```


### Gameplay instructions

1. Go to http://127.0.0.1:5000
2. Register and log in to your account.
3. Press "Sukurti naują turnyrą" if you want to create new tournament.
3. Create tourney and its questions, download tournament PDF file if needed.
4. Drop QR codes in different places and mark it in the map.
5. Invite peapole to acieve this tournament and give them tourney code.
6. Check the scoreboard after the tournament or create a new one!