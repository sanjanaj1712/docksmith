import json
import os
from datetime import datetime
import hashlib


def create_manifest(name_tag, layers, config):
    name, tag = name_tag.split(":")

    manifest = {
        "name": name,
        "tag": tag,
        "digest": "",
        "created": datetime.utcnow().isoformat(),
        "config": config,
        "layers": [{"digest": l} for l in layers]
    }

    # Compute digest (without digest field)
    temp_manifest = manifest.copy()
    temp_manifest["digest"] = ""

    manifest_bytes = json.dumps(temp_manifest, sort_keys=True).encode()
    digest = hashlib.sha256(manifest_bytes).hexdigest()

    manifest["digest"] = "sha256:" + digest

    # Save manifest
    images_dir = os.path.expanduser("~/.docksmith/images")
    os.makedirs(images_dir, exist_ok=True)

    file_path = os.path.join(images_dir, f"{name}_{tag}.json")

    with open(file_path, "w") as f:
        json.dump(manifest, f, indent=4)

    return manifest["digest"]
