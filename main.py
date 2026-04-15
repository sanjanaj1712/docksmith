from core.parser import parse_docksmithfile
from core.executor import execute_instructions
from storage.manifest import create_manifest

def main():
    instructions = parse_docksmithfile("Docksmithfile")

    layers, state = execute_instructions(instructions)

    image_id = create_manifest(layers, state)

    print(f"\nFinal Image ID: {image_id}")


if __name__ == "__main__":
    main()