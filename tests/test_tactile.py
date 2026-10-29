import json, os, subprocess, sys, time
import pytest
from tactile import core, render
from tactile.cli import main

FAKE = [{"id": "a0", "role": "application", "name": "x", "states": [], "children": [
    {"id": "a0.0", "role": "filler", "name": "", "states": ["enabled"], "children": [
        {"id": "a0.0.0", "role": "push button", "name": "Save", "states": ["enabled"], "children": []}]}]}]


def test_render_flattens():
    assert render(FAKE) == '[a0] application "x"\n  [a0.0.0] push button "Save"'


live = pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="needs headless session")


@pytest.fixture(scope="module")
def app():
    p = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "app_gtk.py")])
    for _ in range(50):
        time.sleep(0.2)
        try:
            if core.find(name="Save", app="app_gtk"):
                break
        except Exception:
            pass
    yield
    p.kill()


@live
def test_live(app, capsys):
    text = render(core.tree("app_gtk"))
    assert 'push button "Save"' in text and 'check box "Agree"' in text
    assert "clicked" in core.click("push button:Save")
    time.sleep(0.3)
    assert core.find(role="label", name="saved", exact=True)
    core.type_text("text:Name", "Ada")
    assert core.read("text:Name")["text"] == "Ada"
    assert "focused" in core.focus("text:Name")
    assert main(["--json", "find", "--name", "Save"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["name"] == "Save"
