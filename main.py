from core.parser import parse_docksmithfile
from core.executor import execute_instructions

def main():
    instructions = parse_docksmithfile("Docksmithfile")

    layers = execute_instructions(instructions)

    print("\nFinal Layers:")
    for l in layers:
        print(l)

if __name__ == "__main__":
    main()