"""Unit tests for DevReplicant."""

import unittest
from devreplicant.collector import get_system_info, generate_restore_script, generate_dockerfile


class TestDevReplicant(unittest.TestCase):
    def test_get_system_info(self):
        info = get_system_info()
        self.assertIn("system", info)
        self.assertIn("machine", info)
        self.assertIn("python_version", info)

    def test_generate_restore_script(self):
        sample_snap = {
            "packages": {
                "apt": ["curl", "git", "vim"],
                "pip": ["requests==2.31.0", "fastapi==0.110.0"],
                "npm_global": ["typescript@5.4.2"],
                "vscode_extensions": ["ms-python.python"]
            },
            "git_config": {
                "user.name": "Developer",
                "user.email": "dev@example.com"
            }
        }
        script = generate_restore_script(sample_snap)
        self.assertIn("#!/usr/bin/env bash", script)
        self.assertIn("apt-get install", script)
        self.assertIn("curl git vim", script)
        self.assertIn("pip3 install 'requests==2.31.0'", script)
        self.assertIn("npm install -g typescript@5.4.2", script)
        self.assertIn("code --install-extension ms-python.python", script)
        self.assertIn('git config --global "user.name" "Developer"', script)

    def test_generate_dockerfile(self):
        sample_snap = {
            "packages": {
                "pip": ["pytest==8.0.0"]
            }
        }
        df = generate_dockerfile(sample_snap)
        self.assertIn("FROM ubuntu:22.04", df)
        self.assertIn("pytest==8.0.0", df)


if __name__ == "__main__":
    unittest.main()
