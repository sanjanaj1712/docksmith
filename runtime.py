import subprocess

def run_container(command, env=None, workdir="/"):
    rootfs = "/root/miniroot"

    print("Using rootfs:", rootfs)
    print("Running inside container...")

    env = env or {}

    # Build 'export' statements so variables are visible to the shell
    export_lines = "; ".join([f'export {k}="{v}"' for k, v in env.items()])

    # Combine export + working dir + command
    if export_lines:
        shell_cmd = f'{export_lines}; cd {workdir} && {" ".join(command)}'
    else:
        shell_cmd = f'cd {workdir} && {" ".join(command)}'

    cmd = ["chroot", rootfs, "/bin/bash", "-lc", shell_cmd]
    subprocess.run(cmd, check=False)

if __name__ == "__main__":
    run_container(["/bin/echo", "Hello from container"], env={"APP_ENV": "dev"})
