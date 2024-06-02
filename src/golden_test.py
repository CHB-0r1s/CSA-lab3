import os
import subprocess
import tempfile

import pytest


@pytest.mark.golden_test("goldens/*.yml")
def test_translator_and_machine(golden):
    with tempfile.TemporaryDirectory() as tmpdir:
        prop = os.path.join(tmpdir, "prop.txt")
        inp = os.path.join(tmpdir, "in.txt")
        out = os.path.join(tmpdir, "out.txt")
        log = os.path.join(tmpdir, "log.txt")

        with open(prop, mode="w", encoding="utf-8") as f:
            f.write(golden["in_source"])
        with open(inp, mode="w", encoding="utf-8") as f:
            f.write(golden["in_stdin"])

        subprocess.Popen(["python", "./translator.py", prop, out], cwd="src").wait()
        subprocess.Popen(["python", "./machine.py", out, inp, log], cwd="src").wait()

        with open(out, "r") as f:
            machine_code = f.read()
        with open(log, "r") as f:
            logs = f.read()

        assert machine_code == golden["out_code"]
        assert logs == golden["out_log"]

pytest.main()