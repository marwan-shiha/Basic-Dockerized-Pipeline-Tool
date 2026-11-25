import os
import subprocess
import time

def start_containers(user: str, password: str, db_name: str, port: str) -> None:
    env = os.environ.copy()
    env["POSTGRES_USER"] = user
    env["POSTGRES_PASSWORD"] = password
    env["POSTGRES_DB"] = db_name
    env["POSTGRES_PORT"] = str(port)

    subprocess.run(["docker", "compose", "up", "-d"], env=env, check=True)

def wait_for_postgres(user: str, db_name: str, timeout: int = 30) -> None:
    command = ["docker", "exec", "pg-database", "pg_isready", "-U", user, "-d", db_name]
    start_time = time.time()

    while time.time() - start_time < timeout:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return
        time.sleep(2)

    raise TimeoutError("PostgreSQL did not become ready in time.")