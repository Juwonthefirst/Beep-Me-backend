import subprocess, os, sys

from BeepMe.utils import load_enviroment_variables

load_enviroment_variables()
postgres_file_location = "C:\\Program Files\\PostgreSQL\\17\\data"


def stop_database():
    if os.getenv("ENVIROMENT") != "development":
        return
    print("stoping database server...")
    subprocess.run(["pg_ctl", "-D", postgres_file_location, "stop"])


def start_database():
    if os.getenv("ENVIROMENT") != "development":
        return
    print("starting database server...")
    subprocess.run(["pg_ctl", "-D", postgres_file_location, "start"])


def make_migrations_and_migrate():
    start_database()
    subprocess.run(["uv", "run", "manage.py", "makemigrations"])
    subprocess.run(["uv", "run", "manage.py", "migrate"])
    stop_database()


collectstatic = lambda: subprocess.run(["uv", "run", "manage.py", "collectstatic"])
run_devserver = lambda: subprocess.run(
    ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
)


def run_development_server():
    start_database()
    run_devserver()


port = int(os.getenv("PORT", "8000"))


def run_production_server():
    subprocess.run(["uv", "run", "createsuperuser.py"])
    make_migrations_and_migrate()
    collectstatic()
    subprocess.run(
        [
            "daphne",
            "--proxy-headers",
            "-b",
            "0.0.0.0",
            "-p",
            port,
            "-v",
            "2",
            "BeepMe.asgi:application",
        ]
    )


def run_tests():
    start_database()
    subprocess.run(["uv", "run", "manage.py", "test"])
    stop_database()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        match (sys.argv[1]):
            case "dev":
                run_development_server()
            case "prod":
                run_production_server()
            case "migrate":
                make_migrations_and_migrate()
            case "startdb":
                start_database()
            case "stopdb":
                stop_database()
            case "test":
                run_tests()
