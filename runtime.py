import os
import json
import tarfile
import subprocess
import shutil


def run_container(name_tag):
    name, tag = name_tag.split(":")

    # Load manifest
    image_path = os.path.expanduser(f"~/.docksmith/images/{name}_{tag}.json")

    if not os.path.exists(image_path):
        print("Image not found")
        return

    with open(image_path, "r") as f:
        manifest = json.load(f)

    layers = manifest["layers"]

    # Create temp runtime filesystem
    temp_fs = "/tmp/docksmith_runtime"

    if os.path.exists(temp_fs):
        shutil.rmtree(temp_fs)

    os.makedirs(temp_fs)

    # Extract layers in order
    layers_dir = os.path.expanduser("~/.docksmith/layers")

    for layer in layers:
        digest = layer["digest"]
        layer_path = os.path.join(layers_dir, digest + ".tar")

        if not os.path.exists(layer_path):
            print(f"Missing layer: {digest}")
            return

        with tarfile.open(layer_path, "r") as tar:
            tar.extractall(temp_fs)

    # Run command from manifest
    print("\nRunning container...\n")

    cmd = manifest["config"]["Cmd"]

    if not cmd:
        print("No CMD specified in image")
        return

    # 🔥 FIX: handle WORKDIR
    workdir = manifest["config"].get("WorkingDir", "/")
    actual_workdir = os.path.join(temp_fs, workdir.lstrip("/"))

    print(f"Running command: {' '.join(cmd)} in {workdir}\n")

    try:
        subprocess.run(
            cmd,
            cwd=actual_workdir
        )
    except Exception as e:
        print(f"Runtime error: {e}")

    # Cleanup
    shutil.rmtree(temp_fs)
