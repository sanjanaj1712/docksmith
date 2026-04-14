import os
import shutil
import subprocess

from core.layer_manager import create_layer
from storage.cache import generate_cache_key, get_cached_layer, store_cache

FS_ROOT = "temp_fs"


def reset_filesystem():
    if os.path.exists(FS_ROOT):
        shutil.rmtree(FS_ROOT)
    os.makedirs(FS_ROOT)


def handle_workdir(path, state):
    full_path = os.path.join(FS_ROOT, path.lstrip("/"))
    os.makedirs(full_path, exist_ok=True)
    state["workdir"] = full_path


def handle_env(args, state):
    key, value = args.split("=", 1)
    state["env"][key] = value


def handle_cmd(args, state):
    state["cmd"] = args


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
    env = os.environ.copy()
    env.update(state["env"])

    subprocess.run(
        command,
        shell=True,
        cwd=state["workdir"],
        env=env
    )

    return create_layer(FS_ROOT)


def execute_instructions(instructions, use_cache=True):
    reset_filesystem()

    state = {
        "workdir": FS_ROOT,
        "env": {},
        "cmd": None,
        "prev_layer": "base"
    }

    layers = []

    for instr, arg in instructions:
        print(f"\n>>> {instr} {arg}")

        if instr == "WORKDIR":
            handle_workdir(arg, state)

        elif instr == "ENV":
            handle_env(arg, state)

        elif instr == "CMD":
            handle_cmd(arg, state)

        elif instr in ["COPY", "RUN"]:
            cache_key = generate_cache_key(
                state["prev_layer"],
                f"{instr} {arg}",
                state["workdir"],
                state["env"]
            )

            if use_cache:
                cached = get_cached_layer(cache_key)
                if cached:
                    print(f"[CACHE HIT] {cached}")
                    state["prev_layer"] = cached
                    layers.append(cached)
                    continue

            if instr == "COPY":
                layer = handle_copy(arg, state)
            else:
                layer = handle_run(arg, state)

            store_cache(cache_key, layer)

            state["prev_layer"] = layer
            layers.append(layer)

        else:
            print(f"[SKIP] {instr}")

    return layers, state