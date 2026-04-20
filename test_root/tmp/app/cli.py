import sys
from runtime import run_container


def main():
    # Minimal CLI for the test fixture
    if len(sys.argv) < 2:
        print("Usage: python3 cli.py run [-e KEY=VALUE] <name:tag>")
        return

    action = sys.argv[1]
    if action != "run":
        print("Only 'run' supported")
        return

    args = sys.argv[2:]
    extra_env = []
    i = 0
    while i < len(args):
        if args[i] == "-e":
            if i + 1 >= len(args):
                print("[ERROR] Missing value after -e")
                return
            extra_env.append(args[i+1])
            i += 2
        else:
            break

    if i >= len(args):
        print("[ERROR] Missing image name")
        return

    image_name = args[i]
    run_container(image_name, extra_env)


if __name__ == "__main__":
    main()
