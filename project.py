import questionary
from rich.console import Console
from rich.panel import Panel
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime
import os
import gzip

console = Console()

def main():
    console.print(Panel("Backup My Database", title="DBackup", border_style="blue"))
    console.print(f"[red][WARNING][/red] YOU need to have the db installed at your system to be able to do the backup!")
    custom_style_fancy = questionary.Style([("highlighted", "bold"),])
    framework = questionary.select("What's your DB: ", choices=["MySQL", "PostgreSQL", "MongoDB"], pointer="->", show_selected=True, style=custom_style_fancy).unsafe_ask()
    db = credentials(framework)
    match framework:
        case "MySQL":
            mysql_backup(db)
        case "PostgreSQL":
            postgresql_backup(db)
        case "MongoDB":
            mongodb_backup(db)

def credentials(framework: str):
    autocompletelist = ["localhost", "root", "postgres"]
    db = {}
    try:
        with open('autocomplete', 'r', newline='') as file:
            for row in file:
                autocompletelist.append(row.rstrip())
    except FileNotFoundError:
        pass
    if framework == "MongoDB":
        db['uri'] = questionary.autocomplete("uri: ", choices=autocompletelist).unsafe_ask()
        db['password'] = questionary.password("password: ").unsafe_ask()  
        db['database'] = questionary.autocomplete("database: ", choices=autocompletelist).unsafe_ask()

    else:
        db['host'] = questionary.autocomplete("host: ", choices=autocompletelist).unsafe_ask()
        db['user'] = questionary.autocomplete("user: ", choices=autocompletelist).unsafe_ask()
        db['password'] = questionary.password("password: ").unsafe_ask()
        db['database'] = questionary.autocomplete("database name: ", choices=autocompletelist).unsafe_ask()
        if framework == "PostgreSQL":
            db['port'] = questionary.select("port: ", choices=["5432", "other"]).unsafe_ask()
            if db['port'] == "other":
                db['port'] = questionary.text("port: ").unsafe_ask()
    try:
        with open('autocomplete', mode='a', newline='', encoding="utf-8") as file:
            for value in db.values():
                if value not in autocompletelist:
                    file.write(f"{value}\n")
    except FileNotFoundError:
        pass
    return db

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H%M%S");

def mysql_backup(db: dict):
    install_connector("mysql")
    import mysql.connector
    from mysql.connector import Error
    try:
        with mysql.connector.connect(
                host=db["host"],
                user=db["user"],
                password=db["password"],
                database=db["database"]
        ) as connection:
            if connection.is_connected():
                console.print(f"[green]CONNECTED[/green] to database {db['database']}")

            start_backup = questionary.confirm("Initiate database backup? ").unsafe_ask()
            if start_backup:
                timestamp = get_timestamp()
                backup_file = f"{db['database']}_backup_{timestamp}.sql.gz"

                env = os.environ.copy()
                env["MYSQL_PWD"] = db["password"]

                command = [
                    "mariadb-dump",
                    f"-h{db['host']}",
                    f"-u{db['user']}",
                    db['database']
                ]

                console.print("[yellow]Processing backup and compressing... Please wait.[/yellow]")

                with gzip.open(backup_file, "wt", encoding="utf-8") as f:
                    subprocess.run(command, env=env, stdout=f, check=True)
                console.print(f"[green]SUCCESS[/green] Compressed backup saved to [bold]{backup_file}[/bold]")
                save_file(backup_file)
        return True
    except Error as e:
        console.print(f"[bold][red]FAIL[/bold][/red] connecting to the database {db['database']} error: {e}")
        return False
    except subprocess.CalledProcessError as e:
        if os.path.exists(backup_file):
            os.remove(backup_file)
        console.print(f"[bold][red]FAIL[/bold][/red] Backup process failed: {e}")
        return False

def postgresql_backup(db: dict):
    install_connector("postgresql")
    import psycopg2
    from psycopg2 import OperationalError
    connexion = f"host={db['host']} dbname={db['database']} user={db['user']} password={db['password']} port={db['port']}"
    try:
        console.print("Connecting to PostgreSQL database")
        with psycopg2.connect(connexion) as conn:
            console.print(f"[green]CONNECTED[/green] to database {db['database']}")
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone();
                console.print(f"PostgreSQL version: {version[0]}")
                command = [
                        "pg_dump",
                        f"-h{db['host']}",
                        f"-p{db['port']}",
                        f"-U{db['user']}",
                        f"-d{db['database']}"
                ]
                start_backup = questionary.confirm("start postgres backup: ").unsafe_ask()
                if start_backup:
                    timestamp = get_timestamp()
                    file = f"{db['database']}_backup_{timestamp}"
                    console.print("Starting backup and compressing...")
                    with gzip.open(file, "wt", encoding="utf-8") as f:
                        subprocess.run(command, stdout=f, check=True)
                        console.print(f"[green]Backup Successully made.[/green]")
                        save_file(file)
                else:
                    console.print(f"backup process [bold][red]cancelled[/red][/bold] by user")
        return True
    except OperationalError as error:
        console.print(f"[red][bold]Error[/bold][/red] connecting to database {db['database']}: {error}")
        return False
    except (subprocess.CalledProcessError, OSError) as e:
        console.print(f"[bold][red]FAIL[/bold][/red] Backup process or compression failed: {e}")
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass
        return False

def mongodb_backup(db: dict):
    install_connector("mongodb")
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
    file = None
    import re
    uri = re.sub(r"<db_password>", db['password'], db['uri'])
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.server_info()
        console.print(f"[green]CONNECTED[/green] to MongoDB server")
        start_backup = questionary.confirm("Start backup: ").unsafe_ask()
        if start_backup:
            timestamp = get_timestamp()
            file = f"{database}_mongobackup_{timestamp}"
            command = [
                    "mongodump",
                    f"--uri={uri}",
                    f"--db={db['database']}",
                    "--archive"
            ]
            console.print("Starting backup and compressing...")
            with gzip.open(file, "wt", encoding="utf-8") as f:
                subprocess.run(command, stdout=f, check=True)
            console.print("[green]SUCCESS[/green] Backup and compression finished")
            save_file(file)
            client.close()
        return True
    except (ServerSelectionTimeoutError, OperationFailure) as e:
        console.print(f"[bold][red]FAIL[/bold][/red] connecting to MongoDB: {e}")
        return False
    except (subprocess.CalledProcessError, OSError) as e:
        console.print(f"[bold][red]FAIL[/bold][/red] MongoDB backup process failed: {e}")
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                pass
        return False

def save_file(backup_file: str):
    cwd = Path.cwd()
    org = Path(str(cwd)+"/"+backup_file)
    dest = questionary.path("Save backup file in dir: ").unsafe_ask()
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    if org.exists():
        shutil.move(str(org), str(dest))
        console.print(f"{backup_file} [bold][green]saved[/green][/bold]")
    else:
        console.print(f"{backup_file} [bold][red]not found[/red][/bold]")

def install_connector(package: str):
    connectors = {"mysql": "mysql-connector-python", "postgresql": "psycopg2-binary", "mongodb": "pymongo"}
    package_exists = importlib.util.find_spec(connectors[package])
    console.print(f"[bright_yellow]VERIFYING[/bright_yellow] if connector for {package} exist...")
    if package_exists == None:
        console.print(f"Package [red][bold]{package}[/bold][/red] not installed or not found installing now")
        result = subprocess.run([sys.executable, "-m", "pip", "install", connectors[package]], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]SUCCESS[/green] Connector for [blue1][bold]{package}[/bold][/blue1] succefully installed")
        else:
            console.print(f"[red]FAIL[/red] Fail installing connector for {package}")
            console.print(result.stderr)
            sys.exit(1)
    else:
        console.print(f"Package [green][bold]{connectors[package]}[/bold][/green] already installed. Proceding")

if __name__ == "__main__":  
    try:
        main()
    except KeyboardInterrupt:
        console.print("Exiting...")
        sys.exit(1)
