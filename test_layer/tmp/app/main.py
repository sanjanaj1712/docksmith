import sys
from build_engine import build_image
from runtime import run_container


def main():
    if len(sys.argv) < 2:
        print("[ERROR] No command provided")
        print("Usage:")
        print("  build <name:tag> <context>")
        print("  run <name:tag>")
        return

    command = sys.argv[1]

    # =========================
    # BUILD COMMAND
    # =========================
    if command == "build":
        if len(sys.argv) < 4:
            print("[ERROR] Missing arguments for build")
            print("Usage: build <name:tag> <context>")
            return

        tag = sys.argv[2]
        context = sys.argv[3]

        print("[BUILD START]")
        print(f"Building image: {tag}")
        build_image(tag, context)
        print("[BUILD END]")

    # =========================
    # RUN COMMAND
    # =========================
    elif command == "run":
        if len(sys.argv) < 3:
            print("[ERROR] Missing image name")
            print("Usage: run <name:tag>")
            return

        image_name = sys.argv[2]

        print("[RUN START]")
        print(f"Running image: {image_name}")
        run_container(image_name)
        print("[RUN END]")

    # =========================
    # UNKNOWN COMMAND
    # =========================
    else:
        print(f"[ERROR] Unknown command: {command}")


if __name__ == "__main__":
    main()
