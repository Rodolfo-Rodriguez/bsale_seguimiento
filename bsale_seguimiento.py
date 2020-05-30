import os

from app import create_app, db

HOST = '0.0.0.0'
PORT = 8080

app = create_app('development')

if __name__ == "__main__":
    app.run(host=HOST,port=PORT)
