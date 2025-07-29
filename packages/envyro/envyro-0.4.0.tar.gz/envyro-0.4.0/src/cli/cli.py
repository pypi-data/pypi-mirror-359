import typer
from typer import Option
from rich.console import Console

from cli.utils.get_files import scan_envyro_files
from parser import EnvyroParser

app = typer.Typer()
console = Console()


@app.command()
def export(
    env: str = Option(
        None,
        "--env", "-e",
        help="For which environment do we need to export the .envyro file? (e.g., dev, prod, staging)"
    ),
    source: str = Option(
        None,
        "--source", "-s",
        help="Path to the source .envyro file that requires conversion"
    ),
    shell: bool = Option(
        False,
        "--shell",
        help="Export variables to shell instead of a file"
    ),
    format_type: str = Option(
        "env",
        "--format", "-f",
        help="Output format: env, json, yaml, or toml"
    ),
    output: str = Option(
        None,
        "--output", "-o",
        help="Output file path (optional)"
    ),
):

    if source is None:
        console.print(
            "[bold yellow]Source not mentioned, scanning current dir...[/bold yellow]")
        source = scan_envyro_files()
        if len(source) == 0:
            console.print(
                "[bold red]No .envyro files found in the current directory.[/bold red]")
            raise typer.Exit(code=1)
        elif len(source) > 1:  # More than one .envyro file found ::> should we give a prompt to select one? maybe yes, TODO
            console.print(
                "[bold red]Multiple .envyro files found, please specify one using --source option.[/bold red]")
            raise typer.Exit(code=1)
        else:
            source = source[0]
        console.print(
            f"[bold green]Using source file: {source}[/bold green]")
    else:
        source = source.strip()
        console.print(
            f"[bold green]Using source file: {source}[/bold green]")

    if env is None:
        console.print(
            "[bold red]Please provide at least one of the following options: --env")
        raise typer.Exit(code=1)
    # compiler = EnvyroCompiler(source, env)

    try:
        parser = EnvyroParser(source)

        # Validate format type
        supported_formats = ["env", "json", "yaml", "toml"]
        if format_type not in supported_formats:
            console.print(
                f"[bold red]Unsupported format: {format_type}. Supported formats: {', '.join(supported_formats)}[/bold red]")
            raise typer.Exit(code=1)

        if shell:
            env_vars = parser.get_env_vars(env)
            for key, val in env_vars.items():
                env_key = key.upper().replace(".", "_")
                print(f"export {env_key}={val}")
        else:
            # Use the new format export method
            parser.export_format(env, format_type, output)  # type: ignore
            output_file = output if output else f"config.{env}.{format_type}" if format_type != "env" else f".env.{env}"
            console.print(
                f"[bold green]Export successful for environment '{env}' to {output_file}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def split(source: str = Option(
    None,
    "--source", "-s",
    help="Path to the source .envyro file that requires conversion"
)):
    if source is None:

        console.print(
            "[bold yellow]Source not mentioned, scanning current dir...[/bold yellow]")
        source = scan_envyro_files()
        if len(source) == 0:
            console.print(
                "[bold red]No .envyro files found in the current directory.[/bold red]")
            raise typer.Exit(code=1)
        elif len(source) > 1:  # More than one .envyro file found ::> should we give a prompt to select one? maybe yes, TODO
            console.print(
                "[bold red]Multiple .envyro files found, please specify one using --source option.[/bold red]")
            raise typer.Exit(code=1)
        else:
            source = source[0]
    else:
        source = source.strip()
    console.print(
        f"[bold green]Using source file: {source}[/bold green]")

    try:
        parser = EnvyroParser(source)
        envs = parser.export_all()
        console.print(
            f"[bold green]Compilation successful for environments {', '.join(envs)}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def diff(
    env1: str = Option(
        ..., '--env1', '-a', help='First environment to compare (e.g., dev)'
    ),
    env2: str = Option(
        ..., '--env2', '-b', help='Second environment to compare (e.g., prod)'
    ),
    source: str = Option(
        None, '--source', '-s', help='Path to the source .envyro file'
    ),
):
    """Show the difference between two environments."""
    if source is None:
        console.print(
            '[bold yellow]Source not mentioned, scanning current dir...[/bold yellow]')
        source = scan_envyro_files()
        if len(source) == 0:
            console.print(
                '[bold red]No .envyro files found in the current directory.[/bold red]')
            raise typer.Exit(code=1)
        elif len(source) > 1:
            console.print(
                '[bold red]Multiple .envyro files found, please specify one using --source option.[/bold red]')
            raise typer.Exit(code=1)
        else:
            source = source[0]
        console.print(f'[bold green]Using source file: {source}[/bold green]')
    else:
        source = source.strip()
        console.print(f'[bold green]Using source file: {source}[/bold green]')

    try:
        parser = EnvyroParser(source)
        diff = parser.diff_envs(env1, env2)
        console.rule(f"[bold blue]Diff: {env1} vs {env2}")
        if diff['only_in_env1']:
            console.print(f"[bold yellow]Only in {env1}:[/bold yellow]")
            for k, v in diff['only_in_env1'].items():
                console.print(f"  [yellow]{k}[/yellow] = {v}")
        if diff['only_in_env2']:
            console.print(f"[bold yellow]Only in {env2}:[/bold yellow]")
            for k, v in diff['only_in_env2'].items():
                console.print(f"  [yellow]{k}[/yellow] = {v}")
        if diff['differing']:
            console.print("[bold magenta]Differing values:[/bold magenta]")
            for k, (v1, v2) in diff['differing'].items():
                console.print(
                    f"  [magenta]{k}[/magenta]: [red]{env1}={v1}[/red] | [green]{env2}={v2}[/green]")
        if not (diff['only_in_env1'] or diff['only_in_env2'] or diff['differing']):
            console.print("[bold green]No differences found![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
