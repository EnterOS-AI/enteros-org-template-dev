from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADVERTISED = re.compile(r"\b(?:copy[- ]?paste|executable)\b", re.IGNORECASE)
FENCE_START = re.compile(
    r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>[^`]*)$"
)
SHELL_LANGUAGES = {"bash", "sh", "shell"}
SHELL_COMMAND = re.compile(
    r"^\s*(?:cd|git|gitea-curl|grep|mkdir|printf|python3|test)\b",
    re.MULTILINE,
)
PLACEHOLDER = re.compile(r"<[A-Za-z][^>\n]*>")
CANONICAL_INTERNAL_URL = "https://git.moleculesai.app/molecule-ai/internal.git"


@dataclass(frozen=True)
class ShellBlock:
    path: Path
    line: int
    body: str
    advertised: bool


def operational_shell_blocks(path: Path) -> list[ShellBlock]:
    lines = path.read_text(encoding="utf-8").splitlines()
    heading = ""
    blocks: list[ShellBlock] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if re.match(r"^ {0,3}#{1,6}\s", line):
            heading = line.strip()

        match = FENCE_START.fullmatch(line)
        if match is None:
            index += 1
            continue

        fence = match.group("fence")
        info = match.group("info").strip().split(maxsplit=1)
        language = info[0].lower() if info else ""
        start = index + 1
        context = "\n".join((heading, *lines[max(0, index - 3) : index]))
        index += 1
        body: list[str] = []
        closing = re.compile(
            rf"^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\s*$"
        )
        while index < len(lines) and closing.fullmatch(lines[index]) is None:
            body.append(lines[index])
            index += 1

        block_body = "\n".join(body) + "\n"
        is_shell = language in SHELL_LANGUAGES or (
            not language and SHELL_COMMAND.search(block_body) is not None
        )
        if is_shell:
            blocks.append(
                ShellBlock(
                    path=path.relative_to(ROOT),
                    line=start + 1,
                    body=block_body,
                    advertised=ADVERTISED.search(context) is not None,
                )
            )
        index += 1

    return blocks


def all_operational_shell_blocks() -> list[ShellBlock]:
    return [
        block
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
        for block in operational_shell_blocks(path)
    ]


class ExecutableShellBlockTests(unittest.TestCase):
    maxDiff = None

    expected_inventory = Counter(
        {
            Path("SHARED_RULES.md"): 4,
            Path("community-manager/system-prompt.md"): 1,
            Path("competitive-intelligence") / "system-prompt.md": 1,
            Path("content-marketer") / "schedules" / "landingpage-check.md": 2,
            Path("content-marketer/system-prompt.md"): 1,
            Path("market-analyst/system-prompt.md"): 1,
            Path("marketing-lead/idle-prompt.md"): 1,
            Path("marketing-lead") / "schedules" / "orchestrator-pulse.md": 2,
            Path("marketing-lead/system-prompt.md"): 1,
            Path("pm/schedules/orchestrator-pulse.md"): 2,
            Path("product-marketing-manager") / "idle-prompt.md": 1,
            Path("product-marketing-manager") / "system-prompt.md": 1,
            Path("research-lead/idle-prompt.md"): 1,
            Path("research-lead") / "schedules" / "orchestrator-pulse.md": 2,
            Path("research-lead/system-prompt.md"): 1,
            Path("seo-growth-analyst") / "schedules" / "landingpage-seo-check.md": 2,
            Path("social-media-brand/system-prompt.md"): 1,
        }
    )
    expected_advertised_paths = {
        Path("SHARED_RULES.md"),
        Path("community-manager/system-prompt.md"),
        Path("competitive-intelligence") / "system-prompt.md",
        Path("content-marketer/system-prompt.md"),
        Path("market-analyst/system-prompt.md"),
        Path("marketing-lead/system-prompt.md"),
        Path("product-marketing-manager") / "system-prompt.md",
        Path("research-lead/system-prompt.md"),
        Path("social-media-brand/system-prompt.md"),
    }

    def setUp(self) -> None:
        self.git = shutil.which("git")
        if self.git is None:
            self.skipTest("git is required")

    def run_git(
        self,
        *args: str,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> str:
        result = subprocess.run(
            [self.git, *args],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

    def git_environment(self, home: Path) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            HOME=str(home),
            GIT_AUTHOR_NAME="Shell Workflow Test",
            GIT_AUTHOR_EMAIL="shell-workflow@example.invalid",
            GIT_COMMITTER_NAME="Shell Workflow Test",
            GIT_COMMITTER_EMAIL="shell-workflow@example.invalid",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_NOSYSTEM="1",
        )
        return env

    def create_remote(self, root: Path, env: dict[str, str]) -> tuple[Path, str]:
        remote = root / "remote.git"
        seed = root / "seed"
        self.run_git("init", "--bare", "--initial-branch=main", str(remote), env=env)
        self.run_git("init", "--initial-branch=main", str(seed), env=env)
        (seed / "README.md").write_text("seed\n", encoding="utf-8")
        self.run_git("add", "README.md", cwd=seed, env=env)
        self.run_git("commit", "-m", "seed", cwd=seed, env=env)
        self.run_git("remote", "add", "origin", str(remote), cwd=seed, env=env)
        self.run_git("push", "-u", "origin", "main", cwd=seed, env=env)
        return remote, self.run_git(
            "--git-dir", str(remote), "rev-parse", "refs/heads/main", env=env
        )

    def create_editor(self, root: Path) -> Path:
        editor = root / "write-test-document"
        editor.write_text(
            "#!/bin/sh\nset -eu\nprintf '# generated by test\\n' > \"$1\"\n",
            encoding="utf-8",
        )
        editor.chmod(0o755)
        return editor

    def localize_legacy_block(
        self, body: str, remote: Path, clone_dir: Path
    ) -> str:
        if "INTERNAL_REPO_URL=" in body:
            return body
        return body.replace(
            CANONICAL_INTERNAL_URL, shlex.quote(str(remote))
        ).replace("~/repos/internal", shlex.quote(str(clone_dir)))

    def run_workflow(
        self,
        block: ShellBlock,
        *,
        cwd: Path,
        env: dict[str, str],
        remote: Path,
        clone_dir: Path,
        run_id: str,
    ) -> subprocess.CompletedProcess[str]:
        workflow_env = env.copy()
        workflow_env.update(
            EDITOR=str(env["TEST_EDITOR"]),
            INTERNAL_REPO_URL=str(remote),
            INTERNAL_REPO_DIR=str(clone_dir),
            WORKFLOW_RUN_ID=run_id,
        )
        return subprocess.run(
            ["bash"],
            input=self.localize_legacy_block(block.body, remote, clone_dir),
            cwd=cwd,
            env=workflow_env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_operational_shell_inventory_is_complete_and_syntax_valid(self) -> None:
        blocks = all_operational_shell_blocks()
        self.assertEqual(Counter(block.path for block in blocks), self.expected_inventory)
        self.assertEqual(
            {block.path for block in blocks if block.advertised},
            self.expected_advertised_paths,
        )

        errors: list[str] = []
        for block in blocks:
            result = subprocess.run(
                ["bash", "-n"],
                input=block.body,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                errors.append(f"{block.path}:{block.line}: {result.stderr.strip()}")
            if block.advertised:
                placeholders = PLACEHOLDER.findall(block.body)
                if placeholders:
                    errors.append(
                        f"{block.path}:{block.line}: literal placeholders: "
                        + ", ".join(sorted(set(placeholders)))
                    )
        worker_placeholder = "<my-" "worker-role>"
        self.assertNotIn(worker_placeholder, "".join(block.body for block in blocks))
        self.assertEqual(errors, [], "\n" + "\n".join(errors))

    def test_all_advertised_workflows_are_repeat_safe(self) -> None:
        blocks = [block for block in all_operational_shell_blocks() if block.advertised]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = self.git_environment(root / "home")
            env["TEST_EDITOR"] = str(self.create_editor(root))
            remote, original_main = self.create_remote(root, env)

            for index, block in enumerate(blocks):
                clone_dir = root / "clones" / str(index)
                first = self.run_workflow(
                    block,
                    cwd=root,
                    env=env,
                    remote=remote,
                    clone_dir=clone_dir,
                    run_id=f"repeat-{index}",
                )
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                branch = self.run_git(
                    "branch", "--show-current", cwd=clone_dir, env=env
                )
                self.assertNotEqual(branch, "main")
                self.assertIn(f"repeat-{index}", branch)
                pushed_head = self.run_git("rev-parse", "HEAD", cwd=clone_dir, env=env)
                self.assertEqual(
                    self.run_git(
                        "--git-dir",
                        str(remote),
                        "rev-parse",
                        f"refs/heads/{branch}",
                        env=env,
                    ),
                    pushed_head,
                )
                self.assertEqual(
                    self.run_git(
                        "--git-dir", str(remote), "rev-parse", "refs/heads/main", env=env
                    ),
                    original_main,
                )

                repeated = self.run_workflow(
                    block,
                    cwd=root,
                    env=env,
                    remote=remote,
                    clone_dir=clone_dir,
                    run_id=f"repeat-{index}",
                )
                self.assertNotEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
                self.assertEqual(
                    self.run_git(
                        "--git-dir",
                        str(remote),
                        "rev-parse",
                        f"refs/heads/{branch}",
                        env=env,
                    ),
                    pushed_head,
                )
                self.assertEqual(
                    self.run_git(
                        "--git-dir", str(remote), "rev-parse", "refs/heads/main", env=env
                    ),
                    original_main,
                )

    def test_failed_clone_or_cd_cannot_push_caller_main(self) -> None:
        block = next(
            block
            for block in all_operational_shell_blocks()
            if block.path == Path("SHARED_RULES.md") and block.advertised
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = self.git_environment(root / "home")
            env["TEST_EDITOR"] = str(self.create_editor(root))
            caller_remote, original_main = self.create_remote(root / "caller-source", env)

            for failure_mode in ("clone", "cd"):
                caller = root / f"caller-{failure_mode}"
                self.run_git("clone", str(caller_remote), str(caller), env=env)
                current_date = datetime.now(timezone.utc).date().isoformat()
                for branch in (
                    f"pmm/positioning-{current_date}",
                    "pmm/positioning-failure",
                ):
                    self.run_git("branch", branch, cwd=caller, env=env)
                caller_head = self.run_git("rev-parse", "HEAD", cwd=caller, env=env)

                mode_env = env.copy()
                if failure_mode == "clone":
                    internal_remote = root / "missing.git"
                else:
                    internal_remote = caller_remote
                    fake_bin = root / "fake-bin"
                    fake_bin.mkdir(exist_ok=True)
                    fake_git = fake_bin / "git"
                    fake_git.write_text(
                        "#!/bin/sh\n"
                        "if [ \"${1:-}\" = clone ]; then exit 0; fi\n"
                        "exec \"$REAL_GIT\" \"$@\"\n",
                        encoding="utf-8",
                    )
                    fake_git.chmod(0o755)
                    mode_env["PATH"] = f"{fake_bin}:{mode_env['PATH']}"
                    mode_env["REAL_GIT"] = self.git

                failed = self.run_workflow(
                    block,
                    cwd=caller,
                    env=mode_env,
                    remote=internal_remote,
                    clone_dir=root / f"internal-{failure_mode}",
                    run_id="failure",
                )
                self.assertNotEqual(failed.returncode, 0, failed.stdout + failed.stderr)
                if failure_mode == "cd":
                    self.assertIn("cd:", failed.stderr)
                self.assertFalse(
                    (caller / "historical" / "marketing" / "positioning.md").exists()
                )
                self.assertEqual(
                    self.run_git("branch", "--show-current", cwd=caller, env=env),
                    "main",
                )
                self.assertEqual(
                    self.run_git("rev-parse", "HEAD", cwd=caller, env=env),
                    caller_head,
                )
                self.assertEqual(
                    self.run_git(
                        "--git-dir",
                        str(caller_remote),
                        "rev-parse",
                        "refs/heads/main",
                        env=env,
                    ),
                    original_main,
                )


if __name__ == "__main__":
    unittest.main()
