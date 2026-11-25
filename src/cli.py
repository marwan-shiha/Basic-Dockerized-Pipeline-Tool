import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.extract import extract_dataset
from src.transform import inspect_dataset, clean_dataset
from src.docker_manager import start_containers, wait_for_postgres
from src.load import load_to_postgres

console = Console()



@click.command()
def main() -> None:
    """Basic-Dockerized-Pipeline Interactive CLI."""
    console.print(Panel.fit(
        "[bold cyan]Basic-Dockerized-Pipeline[/bold cyan]\n"
        "Extract -> Clean -> Containerize -> Publish to PostgreSQL",
        border_style="cyan",
    ))



    # Step 1: Ask for URL or local file path
    source = click.prompt("\nEnter dataset URL or local file path (.csv / .parquet)").strip()
    table_name = click.prompt("Target PostgreSQL table name", default="cleaned_data").strip()



    # Step 2: Extract & inspect (not loaded yet)
    with console.status("[bold green]Extracting dataset...[/bold green]"):
        df = extract_dataset(source)
        stats = inspect_dataset(df)



    # Show quick data quality snapshot before asking how to clean
    summary = Table(title="Dataset Preview & Issues Found")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", style="magenta")
    summary.add_row("Rows", f"{stats['rows']:,}")
    summary.add_row("Columns", str(stats["columns"]))
    summary.add_row("Empty Cells (Nulls)", f"{stats['null_cells']:,}")
    summary.add_row("Exact Duplicate Rows", f"{stats['duplicate_rows']:,}")
    console.print(summary)



    # Step 3: Interactive cleaning prompts
    null_choice = click.prompt(
        "\nHow should empty cells be handled?",
        type=click.Choice(["keep", "zero", "custom"], case_sensitive=False),
        default="keep",
    )
    custom_fill = None
    if null_choice == "custom":
        custom_fill = click.prompt("Enter the number or text to fill empty cells with")

    drop_dupes = click.confirm("Drop exact duplicate rows?", default=True)



    # Apply transformations
    df_clean = clean_dataset(
        df,
        null_strategy=null_choice,
        custom_fill=custom_fill,
        drop_duplicates=drop_dupes,
    )
    console.print(f"[green]✓ Transformation complete:[/green] {len(df_clean):,} rows ready.\n")



    # Step 4: Ask for custom PostgreSQL settings
    console.print("\n[bold cyan]PostgreSQL Configuration[/bold cyan]")
    db_user = click.prompt("PostgreSQL username", default="admin").strip()
    db_password = click.prompt("PostgreSQL password", default="0000", hide_input=True).strip()
    db_name = click.prompt("PostgreSQL database name", default="dockerized_pipeline_database").strip()
    db_port = click.prompt("PostgreSQL port", default="5433").strip()

    # Step 5: Spin up Postgres + pgAdmin via Docker Compose
    console.print("\n[bold blue]Starting Docker containers (pg-database & pgadmin)...[/bold blue]")
    start_containers(user=db_user, password=db_password, db_name=db_name, port=db_port)
    wait_for_postgres(user=db_user, db_name=db_name)

    # Step 6: Load into Postgres with tqdm progress bar
    console.print(f"\n[bold blue]Loading data into table '{table_name}'...[/bold blue]")
    load_to_postgres(
        df_clean,
        table_name=table_name,
        user=db_user,
        password=db_password,
        port=db_port,
        db_name=db_name,
    )

    # Step 7: Done summary
    console.print(Panel(
        f"[bold green]Pipeline Completed Successfully![/bold green]\n\n"
        f"• Table Loaded: [cyan]{table_name}[/cyan] ({len(df_clean):,} rows)\n"
        f"• PostgreSQL:   [yellow]localhost:{db_port}[/yellow] (db: {db_name} | user: {db_user})\n"
        f"• pgAdmin UI:   [link=http://localhost:8080]http://localhost:8080[/link] "
        f"(admin@admin.com / 0000)",
        border_style="green",
    ))