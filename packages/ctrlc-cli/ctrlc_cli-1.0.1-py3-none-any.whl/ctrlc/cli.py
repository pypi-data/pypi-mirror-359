import click, os
from .core import collect_files, write_bundle
from .config import load_config

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

class RichHelpGroup(click.Group):
    def format_help(self, ctx, formatter):
        # rich replaces the entire help output
        self.rich_help()

    def invoke(self, ctx):
        if "--help" in ctx.args or "-h" in ctx.args:
            self.rich_help()
            ctx.exit()
        super().invoke(ctx)

    def rich_help(self):
        console.print(Panel.fit(
            Text.from_markup("[bold]Bundle your codebase context[/] for AI tools, debugging, and sharing.", justify="center"),
            title="[bold green]📦 Ctrl+C",
            border_style="green"
        ))

        table = Table.grid(padding=(0, 2))
        table.add_column("Option", style="cyan bold")
        table.add_column("Description", style="white")

        table.add_row("--ignore-files \\[none|all|git|context]",
                      "Ignore files using .gitignore/.contextignore. Default: all.")
        table.add_row("--threshold <bytes>",
                      "Skip files larger than this size (in bytes).")
        table.add_row("--compress \\[none|gzip|zip|tar.gz]",
                      "Compress the output. Default: none.")
        table.add_row("--output <filename>",
                      "Name of output file (e.g. context.txt)")

        console.print(table)
        console.print("\n[bold yellow]Example:[/] [green]ctrlc run --compress gzip --threshold 1000000\n[/]")

@click.group(cls=RichHelpGroup)
def main():
    """Ctrl+C: bundle project context"""
    pass

@main.command()
@click.option(
    '--ignore-files',
    type=click.Choice(['none', 'all', 'git', 'context']),
    default=None,
    show_choices=False,
    help='Ignore patterns: none, git, context, or all'
)
@click.option(
    '--threshold',
    type=int,
    default=None,
    help='Skip files larger than this size in bytes'
)
@click.option(
    '--compress',
    type=click.Choice(['none', 'gzip', 'zip', 'tar.gz'], case_sensitive=False),
    default='none',
    show_choices=False,
    help='Compression method: none, gzip, zip, or tar.gz'
)
@click.option(
    '--output',
    default='context.txt',
    help='Base output filename'
)
def run(ignore_files, threshold, compress, output):
    root = os.getcwd()
    cfg = load_config(root)
    mode = ignore_files or cfg.get('ignore_files', 'all')
    thr = threshold or cfg.get('threshold')

    # files, git_ignored, ctx_ignored, size_skipped, builtin_ignored = collect_files(root, mode, threshold)
    files, git_ignored, ctx_ignored, size_skipped, builtin_ignored, git_exists, ctx_exists = collect_files(root, mode, threshold)
    write_bundle(root, output, files, compress)
    # Reporting
    console.print(Panel.fit(f"Wrote {len(files)} files to {output}", title="Ctrl+C", style="green"))

    # TO BE CHANGED TO RICH PRINTS
    # if builtin_ignored:
    #     click.echo(f"{builtin_ignored} files skipped due to built-in ignore rules (e.g., .git, node_modules, etc.)")

    # # Gitignore reporting
    # if mode in ('all', 'git'):
    #     if git_exists:
    #         if git_ignored:
    #             click.echo(f".gitignore file found and used to ignore {git_ignored} files")
    #         else:
    #             click.echo(".gitignore file found but did not match any files")
    #     else:
    #         click.echo(".gitignore mode active, but no .gitignore file found")

    # # Contextignore reporting
    # if mode in ('all', 'context'):
    #     if ctx_exists:
    #         if ctx_ignored:
    #             click.echo(f".contextignore file found and used to ignore {ctx_ignored} files")
    #         else:
    #             click.echo(".contextignore file found but did not match any files")
    #     else:
    #         click.echo(".contextignore mode active, but no .contextignore file found")

    # Size threshold
    if threshold:
        click.echo(f"{size_skipped} files skipped due to size threshold ({threshold} bytes)")

if __name__ == '__main__':
    main()