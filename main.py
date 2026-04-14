from core.parser import parse_docksmithfile
from core.executor import execute_instructions
from storage.manifest import create_manifest
import os

if not os.path.exists("storage/cache_index.json"):
    with open("storage/cache_index.json", "w") as f:
        f.write("{}")

def main():
    instructions = parse_docksmithfile("Docksmithfile")

    layers, state = execute_instructions(instructions, use_cache=True)

    image_id = create_manifest(layers, state)

    print("\nFinal Image ID:", image_id)


if __name__ == "__main__":
    main()