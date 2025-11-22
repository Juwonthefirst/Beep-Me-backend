import subprocess, sys


postgres_file_location = "C:\\Program Files\\PostgreSQL\\17\\data"


def stop_database():
    print("stoping database...")
    subprocess.run(["pg_ctl", "-D", postgres_file_location, "stop"])


def start_database():
    print("starting database...")
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


def run_production_server():
    subprocess.run(["uv", "run", "createsuperuser.py"])
    make_migrations_and_migrate()
    collectstatic()
    subprocess.run(["daphne", "BeepMe.asgi:application", "-b", "0.0.0.0"])


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
