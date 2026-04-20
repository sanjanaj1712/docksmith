import os
import json
from datetime import datetime

def create_manifest(tag, layers, config):
    name, tag = tag.split(":")

    manifest = {
        "name": name,
        "tag": tag,
        "created": datetime.utcnow().isoformat(),
        "config": config,   # ✅ THIS IS THE MOST IMPORTANT LINE
        "layers": layers
    }

    images_dir = os.path.expanduser("~/.docksmith/images")
    os.makedirs(images_dir, exist_ok=True)

    manifest_path = os.path.join(images_dir, f"{name}_{tag}.json")

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    return "saved"
