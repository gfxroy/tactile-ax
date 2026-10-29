"""Read and act on Linux UI elements through AT-SPI (works on X11 and Wayland)."""
from __future__ import annotations

SKIP_ROLES = {"filler", "panel", "unknown", "redundant object", "section", "scroll pane", "viewport"}


class TactileError(RuntimeError):
    pass


def _atspi():
    try:
        import gi
        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi
    except (ImportError, ValueError) as e:
        raise TactileError("AT-SPI not available. Install python3-gi and gir1.2-atspi-2.0.") from e
    return Atspi


def _desktop():
    d = _atspi().get_desktop(0)
    if d is None:
        raise TactileError("Accessibility bus not reachable. Try: gsettings set org.gnome.desktop.interface toolkit-accessibility true")
    return d


def _states(acc):
    Atspi = _atspi()
    s = acc.get_state_set()
    names = {"focused": Atspi.StateType.FOCUSED, "enabled": Atspi.StateType.ENABLED,
             "checked": Atspi.StateType.CHECKED, "showing": Atspi.StateType.SHOWING}
    return [k for k, v in names.items() if s.contains(v)]


def _node(acc, nid, depth, max_depth):
    try:
        role, name = acc.get_role_name(), acc.get_name() or ""
    except Exception:
        return None
    n = {"id": nid, "role": role, "name": name, "states": _states(acc), "children": []}
    if depth < max_depth:
        for i in range(acc.get_child_count()):
            c = acc.get_child_at_index(i)
            if c is not None:
                cn = _node(c, f"{nid}.{i}", depth + 1, max_depth)
                if cn:
                    n["children"].append(cn)
    return n


def apps() -> list[dict]:
    d = _desktop()
    out = []
    for i in range(d.get_child_count()):
        a = d.get_child_at_index(i)
        if a is not None:
            out.append({"id": f"a{i}", "name": a.get_name() or ""})
    return out


def tree(app: str | None = None, max_depth: int = 30) -> list[dict]:
    d = _desktop()
    out = []
    for i in range(d.get_child_count()):
        a = d.get_child_at_index(i)
        if a is None or (app and app.lower() not in (a.get_name() or "").lower()):
            continue
        n = _node(a, f"a{i}", 0, max_depth)
        if n:
            out.append(n)
    return out


def _walk(nodes):
    for n in nodes:
        yield n
        yield from _walk(n["children"])


def render(nodes: list[dict]) -> str:
    """Compact, token-cheap text: one line per meaningful node, unnamed containers flattened."""
    lines = []

    def go(n, ind):
        keep = not (n["role"] in SKIP_ROLES and not n["name"])
        if keep:
            st = [s for s in n["states"] if s in ("focused", "checked")] + ([] if "enabled" in n["states"] or n["role"] == "application" else ["disabled"])
            extra = f" ({', '.join(st)})" if st else ""
            lines.append(f'{"  " * ind}[{n["id"]}] {n["role"]} "{n["name"]}"{extra}')
        for c in n["children"]:
            go(c, ind + 1 if keep else ind)

    for n in nodes:
        go(n, 0)
    return "\n".join(lines)


def find(role: str | None = None, name: str | None = None, app: str | None = None, exact: bool = False) -> list[dict]:
    res = []
    for n in _walk(tree(app)):
        if role and n["role"] != role.lower():
            continue
        if name is not None:
            a, b = n["name"].lower(), name.lower()
            if (a != b) if exact else (b not in a):
                continue
        res.append({k: n[k] for k in ("id", "role", "name", "states")})
    return res


def _resolve(target: str):
    """Target: id 'a0.1.2', 'role:Name', or 'Name'."""
    d = _desktop()
    if target[:1] == "a" and target[1:2].isdigit() and all(p.isdigit() for p in target[1:].split(".")):
        parts = [int(p) for p in target[1:].split(".")]
        acc = d.get_child_at_index(parts[0])
        for p in parts[1:]:
            acc = acc.get_child_at_index(p) if acc else None
        if acc is None:
            raise TactileError(f"No element with id {target}")
        return acc
    role, _, name = target.rpartition(":")
    hits = find(role=role or None, name=name, exact=True) or find(role=role or None, name=name)
    if not hits:
        raise TactileError(f"No element matches {target!r}")
    return _resolve(hits[0]["id"])


def _desc(acc):
    return f'{acc.get_role_name()} "{acc.get_name() or ""}"'


def click(target: str) -> str:
    Atspi = _atspi()
    acc = _resolve(target)
    act = acc.get_action_iface()
    if act and act.get_n_actions():
        names = [act.get_action_name(i) for i in range(act.get_n_actions())]
        idx = next((names.index(k) for k in ("click", "press", "activate", "toggle") if k in names), 0)
        act.do_action(idx)
        return f"clicked {_desc(acc)}"
    comp = acc.get_component_iface()
    if comp:
        r = comp.get_extents(Atspi.CoordType.SCREEN)
        Atspi.generate_mouse_event(r.x + r.width // 2, r.y + r.height // 2, "b1c")
        return f"clicked {_desc(acc)} (mouse)"
    raise TactileError(f"{_desc(acc)} cannot be clicked")


def focus(target: str) -> str:
    acc = _resolve(target)
    comp = acc.get_component_iface()
    if not comp or not comp.grab_focus():
        raise TactileError(f"Could not focus {_desc(acc)}")
    return f"focused {_desc(acc)}"


def type_text(target: str | None, text: str) -> str:
    Atspi = _atspi()
    if target:
        acc = _resolve(target)
        ed = acc.get_editable_text_iface()
        if ed:
            ed.set_text_contents(text)
            return f"typed into {_desc(acc)}"
        focus(target)
    Atspi.generate_keyboard_event(0, text, Atspi.KeySynthType.STRING)
    return "typed via keyboard"


def read(target: str) -> dict:
    acc = _resolve(target)
    out = {"role": acc.get_role_name(), "name": acc.get_name() or "", "states": _states(acc)}
    t = acc.get_text_iface()
    if t:
        out["text"] = t.get_text(0, t.get_character_count())
    return out
