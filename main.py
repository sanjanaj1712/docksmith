# main.py

from core.parser import parse_docksmithfile

def main():
    filepath = "Docksmithfile"

    try:
        instructions = parse_docksmithfile(filepath)

        print("\nParsed Instructions:\n")
        for instr, arg in instructions:
            print(f"{instr} -> {arg}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()