import os
import shutil
import subprocess
from core.layer_manager import create_layer

FS_ROOT = "temp_fs"


def reset_filesystem():
    if os.path.exists(FS_ROOT):
        shutil.rmtree(FS_ROOT)
    os.makedirs(FS_ROOT)


def handle_workdir(path, state):
    full_path = os.path.join(FS_ROOT, path.lstrip("/"))
    os.makedirs(full_path, exist_ok=True)
    state["workdir"] = full_path


def handle_copy(args, state):
    src, dest = args.split()

    dest_path = os.path.join(state["workdir"], dest)
    
    if os.path.isdir(src):
        shutil.copytree(src, dest_path, dirs_exist_ok=True)
    else:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src, dest_path)

    return create_layer(FS_ROOT)


def handle_run(command, state):
    try:
        subprocess.run(
            command,
            shell=True,
            cwd=state["workdir"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("[ERROR] RUN command failed")

    return create_layer(FS_ROOT)


def execute_instructions(instructions):
    reset_filesystem()

    state = {
        "workdir": FS_ROOT
    }

    layers = []

    for instr, arg in instructions:
        print(f"\n>>> {instr} {arg}")

        if instr == "WORKDIR":
            handle_workdir(arg, state)

        elif instr == "COPY":
            layer = handle_copy(arg, state)
            layers.append(layer)

        elif instr == "RUN":
            layer = handle_run(arg, state)
            layers.append(layer)

        else:
            print(f"[SKIP] {instr} not implemented yet")

    return layers