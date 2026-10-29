import argparse, json, sys
from . import core


def main(argv=None):
    p = argparse.ArgumentParser(prog="tactile", description="See and click any Linux app by name.")
    p.add_argument("--json", action="store_true", help="JSON output")
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("apps")
    t = s.add_parser("tree"); t.add_argument("--app"); t.add_argument("--depth", type=int, default=30)
    f = s.add_parser("find"); f.add_argument("--role"); f.add_argument("--name"); f.add_argument("--app")
    for c in ("click", "focus", "read"):
        s.add_parser(c).add_argument("target")
    ty = s.add_parser("type"); ty.add_argument("args", nargs="+", help="[TARGET] TEXT")
    a = p.parse_args(argv)
    try:
        if a.cmd == "apps": r = core.apps()
        elif a.cmd == "tree":
            r = core.tree(a.app, a.depth)
            if not a.json:
                print(core.render(r)); return 0
        elif a.cmd == "find": r = core.find(a.role, a.name, a.app)
        elif a.cmd == "click": r = core.click(a.target)
        elif a.cmd == "focus": r = core.focus(a.target)
        elif a.cmd == "read": r = core.read(a.target)
        else:
            tgt, text = (a.args[0], a.args[1]) if len(a.args) > 1 else (None, a.args[0])
            r = core.type_text(tgt, text)
    except core.TactileError as e:
        print(f"error: {e}", file=sys.stderr); return 1
    if a.json or not isinstance(r, (str, list)):
        print(json.dumps(r, indent=None if a.json else 2))
    elif isinstance(r, list):
        for x in r: print(f'[{x["id"]}] {x.get("role", "application")} "{x["name"]}"')
    else:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
