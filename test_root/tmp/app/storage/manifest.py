import json
import os
import hashlib

IMAGES_DIR = "storage/images"


def ensure_dir():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)


def create_manifest(layers, state):
    ensure_dir()

    manifest = {
        "layers": layers,
        "env": state["env"],
        "cmd": state["cmd"],
        "workdir": state["workdir"]
    }

    digest = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()

    path = os.path.join(IMAGES_DIR, f"{digest}.json")

    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[IMAGE CREATED] {digest}")

    return digest