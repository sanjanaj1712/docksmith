import os
import shutil
import subprocess
import tempfile


def _which(cmd):
    return shutil.which(cmd)


def run_in_sandbox(root_lowerdir, cmd, capture_dir=None, timeout=None):
    """
    Run `cmd` inside a sandbox where writes do not persist to the host lowerdir.

    If capture_dir is provided (a path), then after the command exits, the modified files
    from the merged overlay are copied into capture_dir so the caller can persist them
    (used for build-time RUN to capture generated files into the next layer).

    Returns: subprocess returncode
    """
    # Try bubblewrap first
    bwrap = _which("bwrap")
    if bwrap:
        bcmd = [bwrap, "--ro-bind", root_lowerdir, "/", "--tmpfs", "/tmp", "--dev", "/dev", "--proc", "/proc", "--"] + ["sh", "-c", cmd]
        proc = subprocess.run(bcmd, check=False)
        return proc.returncode

    # Fallback: require Linux tools
    if os.name != "posix":
        raise RuntimeError("Sandbox not supported on this OS without bubblewrap")

    unshare = _which("unshare")
    mount = _which("mount") or _which("/bin/mount")
    umount = _which("umount") or _which("/bin/umount")

    if not unshare or not mount or not umount:
        raise RuntimeError("Required tools (unshare/mount/umount) not available for sandboxing")

    tmp = tempfile.mkdtemp(prefix="docksmith-sandbox-")
    upper = os.path.join(tmp, "upper")
    work = os.path.join(tmp, "work")
    merged = os.path.join(tmp, "merged")

    os.makedirs(upper, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    os.makedirs(merged, exist_ok=True)

    try:
        # mount tmpfs on upper to keep writes in memory
        subprocess.check_call(["mount", "-t", "tmpfs", "tmpfs", upper])

        # mount overlay: lowerdir=read-only unpacked image, upperdir=tmpfs, workdir
        opts = f"lowerdir={root_lowerdir},upperdir={upper},workdir={work}"
        subprocess.check_call(["mount", "-t", "overlay", "overlay", "-o", opts, merged])

        # Run command in a new mount namespace and chroot into merged
        full = f"chroot {merged} /bin/sh -c '{cmd}'"
        uncmd = [unshare, "--mount", "--uts", "--ipc", "--pid", "--fork", "--map-root-user", "--mount-proc", "--"] + ["/bin/sh", "-c", full]
        proc = subprocess.run(uncmd, check=False)
        rc = proc.returncode

        # If capture requested, copy changed files from merged into capture_dir
        if capture_dir and rc == 0:
            # Walk merged and copy files that are different/missing in root_lowerdir
            for root, dirs, files in os.walk(merged):
                for f in files:
                    merged_path = os.path.join(root, f)
                    rel = os.path.relpath(merged_path, merged)
                    target = os.path.join(capture_dir, rel)
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    shutil.copy2(merged_path, target)

        return rc

    finally:
        # cleanup mounts
        try:
            subprocess.call(["umount", merged])
        except Exception:
            pass
        try:
            subprocess.call(["umount", upper])
        except Exception:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
