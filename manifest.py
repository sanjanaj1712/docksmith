import os
import json
import hashlib
from datetime import datetime


def create_manifest(tag, layers, config, created=None):
    name, version = tag.split(":")

    if created is None:
        created = datetime.utcnow().isoformat()

    manifest = {
        "name": name,
        "tag": version,
        "created": created,
        "digest": "",  # placeholder for digest computation
        "config": config,
        "layers": layers  # already list of dicts with digest/size/createdBy
    }

    # Compute digest from canonical form (digest field = "")
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
    digest = "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()

    # Write final manifest with real digest
    manifest["digest"] = digest

    images_dir = os.path.expanduser("~/.docksmith/images")
    os.makedirs(images_dir, exist_ok=True)

    manifest_path = os.path.join(images_dir, f"{name}_{version}.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    return digest
