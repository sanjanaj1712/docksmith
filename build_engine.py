from parser import parse_docksmithfile
from layer import handle_copy, handle_run, create_layer, snapshot_fs
from manifest import create_manifest
import os
import json
import hashlib


# =========================
# FILE HASH FUNCTION
# =========================
def hash_files(context):
    file_hash = hashlib.sha256()

    for root, dirs, files in os.walk(context):
        for file in sorted(files):
            path = os.path.join(root, file)
            try:
                with open(path, "rb") as f:
                    file_hash.update(f.read())
            except Exception:
                continue

    return file_hash.hexdigest()


# =========================
# BASE IMAGE BOOTSTRAPPER
# =========================
def bootstrap_base_image(image_name):
    """Creates a blank base image manifest if it doesn't exist."""
    images_dir = os.path.expanduser("~/.docksmith/images")
    os.makedirs(images_dir, exist_ok=True)

    image_file = os.path.join(images_dir, image_name.replace(":", "_") + ".json")

    if os.path.exists(image_file):
        return  # already exists

    name = image_name.split(":")[0]
    tag = image_name.split(":")[1] if ":" in image_name else "latest"

    manifest = {
        "name": name,
        "tag": tag,
        "created": "1970-01-01T00:00:00",
        "config": {"Env": [], "Cmd": [], "WorkingDir": "/"},
        "layers": [],
        "digest": "0" * 64
    }

    with open(image_file, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"[INFO] Bootstrapped empty base image: {image_name}")


# =========================
# BUILD
# =========================
def build_image(tag, context):
    instructions = parse_docksmithfile(f"{context}/Docksmithfile")

    step = 1
    total = len(instructions)

    temp_fs = "/tmp/docksmith_fs"

    if os.path.exists(temp_fs):
        os.system(f"rm -rf {temp_fs}")

    os.makedirs(temp_fs)

    layers = []
    layers_dir = os.path.expanduser("~/.docksmith/layers")

    cache_dir = os.path.expanduser("~/.docksmith/cache")
    os.makedirs(cache_dir, exist_ok=True)

    config = {
        "Env": [],
        "Cmd": [],
        "WorkingDir": "/"
    }

    prev_layer = ""

    print(f"Building image: {tag}\n")

    for instr, arg in instructions:
        print(f"Step {step}/{total} : {instr} {arg}")

        # =========================
        # FROM
        # =========================
        if instr == "FROM":
            image_name = arg.strip()

            # Auto-bootstrap if base image doesn't exist
            bootstrap_base_image(image_name)

            images_dir = os.path.expanduser("~/.docksmith/images")
            image_file = os.path.join(images_dir, image_name.replace(":", "_") + ".json")

            with open(image_file, "r") as f:
                base_manifest = json.load(f)

            print(f"Using base image: {image_name}")

            base_digest = base_manifest.get("digest", "")
            prev_layer = base_digest

            base_layers = base_manifest.get("layers", [])
            for layer in base_layers:
                if isinstance(layer, dict):
                    layers.append(layer.get("digest"))
                else:
                    layers.append(layer)

        # =========================
        # WORKDIR
        # =========================
        elif instr == "WORKDIR":
            config["WorkingDir"] = arg
            os.makedirs(os.path.join(temp_fs, arg.lstrip("/")), exist_ok=True)
            print(f"Setting working directory to {arg}")

        # =========================
        # COPY
        # =========================
        elif instr == "COPY":
            parts = arg.split()
            if len(parts) != 2:
                print("Error: COPY requires src and dest")
                return

            src, dest = parts

            file_hash = hash_files(context)
            env_string = "|".join(sorted(config["Env"]))
            workdir = config["WorkingDir"]

            key_string = f"{instr} {arg} {prev_layer} {file_hash} {workdir} {env_string}"
            cache_key = hashlib.sha256(key_string.encode()).hexdigest()
            cache_path = os.path.join(cache_dir, cache_key)

            if os.path.exists(cache_path):
                print("[CACHE HIT]")
                with open(cache_path, "r") as f:
                    digest = f.read().strip()
            else:
                print("[CACHE MISS]")
                try:
                    before = snapshot_fs(temp_fs)
                    handle_copy(src, dest, context, temp_fs)
                    digest = create_layer(temp_fs, layers_dir, before_snapshot=before)

                    with open(cache_path, "w") as f:
                        f.write(digest)

                    print(f"Copied {src} to {dest} → Layer {digest[:12]}")
                except Exception as e:
                    print(f"COPY failed: {e}")
                    return

            layers.append(digest)
            prev_layer = digest

        # =========================
        # RUN
        # =========================
        elif instr == "RUN":
            env_string = "|".join(sorted(config["Env"]))
            workdir = config["WorkingDir"]

            key_string = f"{instr} {arg} {prev_layer} {workdir} {env_string}"
            cache_key = hashlib.sha256(key_string.encode()).hexdigest()
            cache_path = os.path.join(cache_dir, cache_key)

            if os.path.exists(cache_path):
                print("[CACHE HIT]")
                with open(cache_path, "r") as f:
                    digest = f.read().strip()
            else:
                print("[CACHE MISS]")
                try:
                    before = snapshot_fs(temp_fs)
                    handle_run(arg, temp_fs)
                    digest = create_layer(temp_fs, layers_dir, before_snapshot=before)

                    with open(cache_path, "w") as f:
                        f.write(digest)

                    print(f"Executed RUN: {arg} → Layer {digest[:12]}")
                except Exception as e:
                    print(f"RUN failed: {e}")
                    return

            layers.append(digest)
            prev_layer = digest

        # =========================
        # ENV
        # =========================
        elif instr == "ENV":
            config["Env"].append(arg)
            print(f"Setting ENV {arg}")

        # =========================
        # CMD
        # =========================
        elif instr == "CMD":
            try:
                config["Cmd"] = json.loads(arg)
                print(f"Setting CMD {config['Cmd']}")
            except Exception:
                print("Invalid CMD format (must be JSON array)")
                return

        # =========================
        # UNKNOWN
        # =========================
        else:
            print(f"Unknown instruction: {instr}")
            return

        step += 1

    image_digest = create_manifest(tag, layers, config)

    print("\nBuild completed successfully")
    print(f"Image created with digest: {image_digest}")
