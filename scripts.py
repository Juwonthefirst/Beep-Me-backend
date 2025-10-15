import subprocess, sys


postgres_file_location = "C:\\Program Files\\PostgreSQL\\17\\data"


def start_database():
    subprocess.run(["pg_ctl", "-D", postgres_file_location, "start"])


def stop_database():
    subprocess.run(["pg_ctl", "-D", postgres_file_location, "stop"])


def make_migrations_and_migrate():
    subprocess.run(["uv", "run", "manage.py", "makemigrations"])
    subprocess.run(["uv", "run", "manage.py", "migrate"])


collectstatic = lambda: subprocess.run(["uv", "run", "manage.py", "collectstatic"])
runserver = lambda: subprocess.run(
    ["daphne", "BeepMe.asgi:application", "-b", "0.0.0.0"]
)


def run_development_server():
    start_database()
    collectstatic()
    runserver()


def run_production_server():
    subprocess.run(["uv", "run", "createsuperuser.py"])
    make_migrations_and_migrate()
    collectstatic()
    runserver()


def run_tests():
    start_database()
    subprocess.run(["uv", "run", "manage.py", "test"])


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
