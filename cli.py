<<<<<<< HEAD
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
=======
import sys
from runtime import run_container

def main():
    # Minimal CLI:
    # python3 cli.py run <image> [--] <cmd...>
    # (image ignored for now; we always use /root/miniroot)
    if len(sys.argv) < 2:
        print("Usage: python3 cli.py run <image> [--] <cmd...>")
        return

    action = sys.argv[1]

    if action != "run":
        print("Only 'run' supported")
        return

    # Defaults
    env = {}
    workdir = "/"

    # Parse args
    args = sys.argv[2:]
    cmd = []

    i = 0
    while i < len(args):
        if args[i] == "-e" and i + 1 < len(args):
            k, v = args[i+1].split("=", 1)
            env[k] = v
            i += 2
        elif args[i] == "-w" and i + 1 < len(args):
            workdir = args[i+1]
            i += 2
        elif args[i] == "--":
            cmd = args[i+1:]
            break
        else:
            # skip <image> or accumulate until --
            i += 1

    if not cmd:
        # default command
        cmd = ["/bin/bash"]

    run_container(cmd, env=env, workdir=workdir)

if __name__ == "__main__":
    main()
>>>>>>> origin/586
