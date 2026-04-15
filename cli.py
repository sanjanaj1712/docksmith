import click
from build_engine import build_image
from runtime import run_container


@click.group()
def cli():
    pass


# -------- BUILD COMMAND --------
@cli.command()
@click.option('-t', '--tag', required=True)
@click.argument('context')
def build(tag, context):
    build_image(tag, context)


# -------- RUN COMMAND --------
@cli.command()
@click.argument('image')
def run(image):
    run_container(image)


if __name__ == "__main__":
    cli()
