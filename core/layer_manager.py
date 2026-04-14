import os
import tarfile
import hashlib

LAYERS_DIR = "storage/layers"


def ensure_layers_dir():
    if not os.path.exists(LAYERS_DIR):
        os.makedirs(LAYERS_DIR)


def hash_directory(directory):
    sha = hashlib.sha256()

    for root, dirs, files in os.walk(directory):
        for file in sorted(files):
            filepath = os.path.join(root, file)

            with open(filepath, "rb") as f:
                while chunk := f.read(4096):
                    sha.update(chunk)

    return sha.hexdigest()


def create_layer(fs_path):
    ensure_layers_dir()

    digest = hash_directory(fs_path)
    tar_path = os.path.join(LAYERS_DIR, f"{digest}.tar")

    if os.path.exists(tar_path):
        print(f"[CACHE] Layer already exists: {digest}")
        return digest

    with tarfile.open(tar_path, "w") as tar:
        tar.add(fs_path, arcname=".")

    print(f"[NEW LAYER] Created: {digest}")
    return digest