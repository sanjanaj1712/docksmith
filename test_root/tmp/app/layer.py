import shutil
import os
import subprocess
import tarfile
import hashlib


# ------------------ COPY ------------------
def handle_copy(src, dest, context, temp_fs):
    src_path = os.path.join(context, src)
    dest_path = os.path.join(temp_fs, dest.lstrip("/"))

    # Check if source exists
    if not os.path.exists(src_path):
        raise Exception(f"Source path does not exist: {src}")

    # Create destination directory
    os.makedirs(dest_path, exist_ok=True)

    # If copying a single file
    if os.path.isfile(src_path):
        shutil.copy2(src_path, os.path.join(dest_path, os.path.basename(src_path)))
        return

    # If copying a directory
    for item in os.listdir(src_path):

        # 🚫 IGNORE .git and hidden files
        if item == ".git" or item.startswith("."):
            continue

        s = os.path.join(src_path, item)
        d = os.path.join(dest_path, item)

        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


# ------------------ RUN ------------------
def handle_run(command, temp_fs):
    try:
        subprocess.run(
            command,
            shell=True,
            cwd=temp_fs,   # 👈 run inside container FS
            check=True
        )
    except subprocess.CalledProcessError:
        raise Exception(f"RUN command failed: {command}")


# ------------------ CREATE LAYER ------------------
def create_layer(temp_fs, layers_dir):
    tar_path = "/tmp/layer.tar"

    # Create tar archive of filesystem
    with tarfile.open(tar_path, "w") as tar:
        tar.add(temp_fs, arcname="")

    # Compute SHA-256 hash
    sha256 = hashlib.sha256()

    with open(tar_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)

    digest = sha256.hexdigest()

    # Ensure layers directory exists
    os.makedirs(layers_dir, exist_ok=True)

    # Final path for layer
    final_path = os.path.join(layers_dir, digest + ".tar")

    # Move tar to layers directory
    shutil.move(tar_path, final_path)

    return digest
