import os
import json
import tarfile
import shutil
from isolation import run_in_sandbox


def _shell_quote(s: str) -> str:
    # Quote a string for single-quoted shell usage
    return "'" + s.replace("'", "'\"'\"'") + "'"


def run_container(name_tag, extra_env=None):
    name, tag = name_tag.split(":")
    image_path = os.path.expanduser(f"~/.docksmith/images/{name}_{tag}.json")

    if not os.path.exists(image_path):
        print("Image not found")
        return

    with open(image_path, "r") as f:
        manifest = json.load(f)

    layers = manifest.get("layers", [])

    temp_fs = "/tmp/docksmith_runtime"
    if os.path.exists(temp_fs):
        shutil.rmtree(temp_fs)
    os.makedirs(temp_fs, exist_ok=True)

    layers_dir = os.path.expanduser("~/.docksmith/layers")

    # Extract layers in order
    for layer in layers:
        digest = layer["digest"] if isinstance(layer, dict) else layer
        layer_path = os.path.join(layers_dir, digest + ".tar")

        if not os.path.exists(layer_path):
            print(f"Missing layer: {digest}")
            shutil.rmtree(temp_fs)
            return

        with tarfile.open(layer_path, "r") as tar:
            tar.extractall(temp_fs)

    config = manifest.get("config", {})

    cmd = config.get("Cmd")
    if not cmd:
        print("No CMD specified in image")
        shutil.rmtree(temp_fs)
        return

    workdir = config.get("WorkingDir", "/")
    # inside the sandbox the lowerdir is mounted as /, so use that path
    actual_workdir = os.path.join("/", workdir.lstrip("/"))

    # Build environment variables as KEY=VAL list
    env_vars = [f"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", f"HOME={workdir}"]
    for env in config.get("Env", []):
        if "=" in env:
            env_vars.append(env)

    if extra_env:
        for env in extra_env:
            if "=" in env:
                env_vars.append(env)

    # Build shell command
    if isinstance(cmd, list):
        shell_cmd = "exec " + " ".join([_shell_quote(str(x)) for x in cmd])
    else:
        shell_cmd = cmd

    # Build env export prefix
    env_prefix_parts = []
    for e in env_vars:
        k, v = e.split("=", 1)
        env_prefix_parts.append(f"export {k}={_shell_quote(v)}")

    env_prefix = " && ".join(env_prefix_parts)
    full_cmd = f"cd {_shell_quote(actual_workdir)} && {env_prefix} && {shell_cmd}"

    try:
        rc = run_in_sandbox(temp_fs, full_cmd)
        if rc != 0:
            print(f"\n[WARN] Container exited with code {rc}")
    except FileNotFoundError:
        print("Error: command not found when running container")
    except Exception as e:
        print(f"Runtime error: {e}")
    finally:
        shutil.rmtree(temp_fs, ignore_errors=True)
