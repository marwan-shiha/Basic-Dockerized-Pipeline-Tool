import importlib.util
import platform
import shutil
import subprocess
import sys

DEPENDENCIES = {
    "pandas": "pandas",
    "pyarrow": "pyarrow",
    "click": "click",
    "sqlalchemy": "sqlalchemy",
    "psycopg2": "psycopg2-binary",
    "tqdm": "tqdm",
    "rich": "rich",
}

def ensure_python_dependencies() -> None:
    for module_name, package_name in DEPENDENCIES.items():
        if importlib.util.find_spec(module_name) is None:
            print(f"[Setup] Installing {package_name}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )

def ensure_docker() -> None:
    if shutil.which("docker") is None:
        os_name = platform.system()
        print("\n[Error] Docker is not installed.")
        if os_name == "Windows":
            print("Install via: winget install Docker.DockerDesktop")
        elif os_name == "Darwin":
            print("Install via: brew install --cask docker")
        else:
            print("Install via: https://docs.docker.com/engine/install/")
        sys.exit(1)

    # Verify the Docker daemon is actually running
    check = subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if check.returncode != 0:
        print("\n[Error] Docker is installed, but the Docker daemon is not running.")
        print("Start Docker Desktop (or the docker service) and run this again.")
        sys.exit(1)

if __name__ == "__main__":
    ensure_python_dependencies()
    ensure_docker()

    # Safe to import Rich/Click now that dependencies are guaranteed
    from src.cli import main
    main()