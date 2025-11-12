"""Runner using bubblewrap."""

import os
import shutil
import subprocess


class ExecutionResult:
    """Lightweight wrapper for the output of a single run."""

    def __init__(self, completed: subprocess.CompletedProcess[bytes]):
        self.returncode: int = completed.returncode
        self.stdout: bytes = completed.stdout
        self.stderr: bytes = completed.stderr

    @property
    def ok(self) -> bool:
        """Whether the sandboxed process exited with status 0."""

        return self.returncode == 0

    @property
    def timed_out(self) -> bool:
        """Return True if the Python code timed out."""

        return self.returncode == 124

    @property
    def success(self) -> bool:
        """If a execution times out or is ok, we'll call it a success."""
        return self.ok or self.timed_out

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        out = self.stdout.decode(errors="replace")
        err = self.stderr.decode(errors="replace")
        return f"<ExecutionResult rc={self.returncode} stdout={out!r} stderr={err!r}>"


class Runner:
    """Sandbox Python execution with bubblewrap."""

    def __init__(
        self,
        executable: str = "python",
        time_limit: int = 1,
    ) -> None:
        """Constructor.

        Args:
            time_limit: hard CPU/timeout limit in seconds.
        """

        self._bwrap = shutil.which("bwrap")
        if self._bwrap is None:
            raise RuntimeError(
                "bubblewrap (bwrap) not found in PATH. Please install it."
            )

        self.time_limit = int(time_limit)

        self._uv_path = shutil.which("uv")
        if self._uv_path is None:
            raise RuntimeError("'uv' executable not found in PATH. Please install uv.")

        default_args = [self._uv_path, "run", executable]

        self.executable_list: list[str] = [
            "timeout",
            str(self.time_limit),
        ] + default_args

        self._uv_dir = os.path.dirname(self._uv_path)

    def run(self, code: str) -> ExecutionResult:
        """Attempt to run the given code.

        Args:
            code: the program string.

        Returns:
            ExecutionResult
        """
        bwrap_bin = str(self._bwrap)

        cmd: list[str] = [
            bwrap_bin,
            "--unshare-all",
            "--die-with-parent",
            "--dir",
            "/tmp",
            "--tmpfs",
            "/tmp",
            "--chdir",
            "/tmp",
            "--ro-bind",
            "/usr",
            "/usr",
            "--ro-bind",
            "/bin",
            "/bin",
            "--ro-bind",
            "/lib",
            "/lib",
            "--ro-bind",
            "/lib64",
            "/lib64",
            "--dev",
            "/dev",
            "--proc",
            "/proc",
        ]

        # Bind-mount uv directory if it isn't already covered by standard binds
        essential_dirs = {"/usr", "/bin", "/lib", "/lib64"}
        if not any(
            self._uv_dir.startswith(p + os.sep) or self._uv_dir == p
            for p in essential_dirs
        ):
            cmd.extend(["--ro-bind", self._uv_dir, self._uv_dir])

        cmd.append("--")

        cmd.extend(self.executable_list)
        cmd.extend(["-I", "-S", "-B", "-"])

        completed = subprocess.run(
            cmd,
            input=code.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        return ExecutionResult(completed)
