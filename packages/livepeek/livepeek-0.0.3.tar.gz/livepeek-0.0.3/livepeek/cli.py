import typer
from livepeek.fetcher import fetch_json
from livepeek.viewer import display_json

app = typer.Typer()

@app.command()
def peek(url: str, watch: int = typer.Option(0, help="Auto-refresh every N seconds")):
    import time
    from rich.console import Console
    console = Console()

    while True:
        try:
            console.clear()
            data = fetch_json(url)
            display_json(data)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        if watch <= 0:
            break
        time.sleep(watch)

if __name__ == "__main__":
    app()
