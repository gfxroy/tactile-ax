"""MCP server: gives any agent (Claude, Grok, ...) eyes and hands on the Linux desktop."""
from mcp.server.fastmcp import FastMCP
from . import core

mcp = FastMCP("tactile")


@mcp.tool()
def apps() -> list[dict]:
    """List running accessible apps."""
    return core.apps()


@mcp.tool()
def tree(app: str | None = None, depth: int = 30) -> str:
    """Compact UI tree. Each line: [id] role "name". Use ids or 'role:Name' as targets."""
    return core.render(core.tree(app, depth))


@mcp.tool()
def find(role: str | None = None, name: str | None = None, app: str | None = None) -> list[dict]:
    """Find elements by role and/or name (case-insensitive substring)."""
    return core.find(role, name, app)


@mcp.tool()
def click(target: str) -> str:
    """Click an element, e.g. 'push button:Save' or an id like 'a0.1.2'."""
    return core.click(target)


@mcp.tool()
def type_text(text: str, target: str | None = None) -> str:
    """Type text into a target field (or the focused one)."""
    return core.type_text(target, text)


@mcp.tool()
def focus(target: str) -> str:
    """Move keyboard focus to an element."""
    return core.focus(target)


@mcp.tool()
def read(target: str) -> dict:
    """Read an element's role, name, states and text."""
    return core.read(target)


def main():
    mcp.run()
