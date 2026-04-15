# core/parser.py

VALID_INSTRUCTIONS = ["FROM", "COPY", "RUN", "WORKDIR", "ENV", "CMD"]

def parse_docksmithfile(filepath):
    instructions = []

    with open(filepath, "r") as file:
        for line_no, line in enumerate(file, start=1):
            line = line.strip()

            # Ignore empty lines and comments
            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=1)

            if len(parts) == 0:
                continue

            instruction = parts[0].upper()

            if instruction not in VALID_INSTRUCTIONS:
                raise ValueError(f"Invalid instruction '{instruction}' at line {line_no}")

            argument = parts[1] if len(parts) > 1 else ""

            instructions.append((instruction, argument))

    return instructions