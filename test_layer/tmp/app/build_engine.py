from parser import parse_docksmithfile
from layer import handle_copy, handle_run, create_layer
from manifest import create_manifest
import os
import json


def build_image(tag, context):
    instructions = parse_docksmithfile(f"{context}/Docksmithfile")

    step = 1
    total = len(instructions)

    # Temporary filesystem path
    temp_fs = "/tmp/docksmith_fs"

    # Clean old filesystem
    if os.path.exists(temp_fs):
        os.system(f"rm -rf {temp_fs}")

    os.makedirs(temp_fs)

    # Layer storage
    layers = []
    layers_dir = os.path.expanduser("~/.docksmith/layers")

    # Config (for manifest)
    config = {
        "Env": [],
        "Cmd": [],
        "WorkingDir": "/"
    }

    print(f"Building image: {tag}\n")

    for instr, arg in instructions:
        print(f"Step {step}/{total} : {instr} {arg}")

        # FROM
        if instr == "FROM":
            print("Using base image (simplified for now)")

        # WORKDIR
        elif instr == "WORKDIR":
            config["WorkingDir"] = arg
            print(f"Setting working directory to {arg}")

        # COPY
        elif instr == "COPY":
            parts = arg.split()

            if len(parts) != 2:
                print("Error: COPY requires src and dest")
                return

            src, dest = parts

            try:
                handle_copy(src, dest, context, temp_fs)

                digest = create_layer(temp_fs, layers_dir)
                layers.append(digest)

                print(f"Copied {src} to {dest} → Layer {digest[:12]}")
            except Exception as e:
                print(f"COPY failed: {e}")
                return

        # RUN
        elif instr == "RUN":
            try:
                handle_run(arg, temp_fs)

                digest = create_layer(temp_fs, layers_dir)
                layers.append(digest)

                print(f"Executed RUN: {arg} → Layer {digest[:12]}")
            except Exception as e:
                print(f"RUN failed: {e}")
                return

        # ENV
        elif instr == "ENV":
            config["Env"].append(arg)
            print(f"Setting ENV {arg}")

        # CMD
        elif instr == "CMD":
            try:
                config["Cmd"] = json.loads(arg)
                print(f"Setting CMD {config['Cmd']}")
            except Exception:
                print("Invalid CMD format (must be JSON array)")
                return

        # UNKNOWN
        else:
            print(f"Unknown instruction: {instr}")
            return

        step += 1

    # Create manifest
    image_digest = create_manifest(tag, layers, config)

    print("\nBuild completed successfully")
    print(f"Image created with digest: {image_digest}")
