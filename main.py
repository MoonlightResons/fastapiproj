from fastapi import FastAPI
from api import auth, posts
from core.database import Base, engine

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)


def create_tables():
    Base.metadata.create_all(bind=engine)


def drop_tables():
    Base.metadata.drop_all(bind=engine)


def run_migrations():
    import subprocess

    subprocess.run(['alembic', 'upgrade', 'head'])


def setup():
    create_tables()
    # run_migrations()


setup()

