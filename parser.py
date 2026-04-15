def parse_docksmithfile(path):
    instructions = []

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=1)
            instr = parts[0]
            arg = parts[1] if len(parts) > 1 else ""

            instructions.append((instr, arg))

    return instructions
