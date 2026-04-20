import sys
import os
from build_engine import build_image
from runtime import run_container


def main():
    if len(sys.argv) < 2:
        print("[ERROR] No command provided")
        print("Usage:")
        print("  build <name:tag> <context>")
        print("  run [-e KEY=VALUE] <name:tag>")
        print("  images")
        print("  rmi <name:tag>")
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
            print("Usage: run [-e KEY=VALUE] <name:tag>")
            return

        args = sys.argv[2:]
        extra_env = []

        i = 0
        while i < len(args):
            if args[i] == "-e":
                if i + 1 >= len(args):
                    print("[ERROR] Missing value after -e")
                    return
                extra_env.append(args[i + 1])
                i += 2
            else:
                break

        if i >= len(args):
            print("[ERROR] Missing image name")
            return

        image_name = args[i]

        print("[RUN START]")
        print(f"Running image: {image_name}")
        run_container(image_name, extra_env)
        print("[RUN END]")

    # =========================
    # IMAGES COMMAND
    # =========================
    elif command == "images":
        images_dir = os.path.expanduser("~/.docksmith/images")

        if not os.path.exists(images_dir) or not os.listdir(images_dir):
            print("No images found")
            return

        print("NAME\tTAG")

        for file in os.listdir(images_dir):
            if file.endswith(".json"):
                name_tag = file.replace(".json", "")
                if "_" in name_tag:
                    name, tag = name_tag.split("_", 1)
                    print(f"{name}\t{tag}")

    # =========================
    # RMI COMMAND
    # =========================
    elif command == "rmi":
        if len(sys.argv) < 3:
            print("Usage: rmi <name:tag>")
            return

        try:
            name, tag = sys.argv[2].split(":")
        except ValueError:
            print("Invalid format. Use name:tag")
            return

        image_path = os.path.expanduser(f"~/.docksmith/images/{name}_{tag}.json")

        if not os.path.exists(image_path):
            print("Image not found")
            return

        os.remove(image_path)
        print(f"Removed image {name}:{tag}")

    # =========================
    # UNKNOWN COMMAND
    # =========================
    else:
        print(f"[ERROR] Unknown command: {command}")


if __name__ == "__main__":
    main()
