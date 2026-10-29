# tactile

**Let AI agents see and click any Linux app by name, not by pixels.**

tactile reads the buttons, fields and menus that apps already expose to screen readers (AT-SPI), so it works on GNOME, KDE, X11 and Wayland. It doesn't need screenshots or coordinates.

Site: https://gfxroy.github.io/tactile-ax/

## Quickstart

```bash
sudo apt install python3-gi gir1.2-atspi-2.0 at-spi2-core   # Debian/Ubuntu
pip install "tactile-ax[mcp] @ git+https://github.com/gfxroy/tactile-ax"

tactile apps                          # running apps
tactile tree --app gedit              # compact UI tree: [id] role "name"
tactile find --name save              # search by role and/or name
tactile click 'push button:Save'      # act by role:name, by name, or by id (a0.0.2)
tactile type 'text:Document' 'Hello'  # type into a field
tactile focus 'text:Document'
tactile read 'text:Document'          # role, states, text
tactile --json tree                   # JSON for programs
```

If nothing shows up, turn accessibility on: `gsettings set org.gnome.desktop.interface toolkit-accessibility true`.

## Use from any AI agent (MCP)

```json
{ "mcpServers": { "tactile": { "command": "tactile-mcp" } } }
```

Tools: `apps`, `tree`, `find`, `click`, `type_text`, `focus`, `read`.

## Python

```python
import tactile
print(tactile.render(tactile.tree("gedit")))
tactile.click("push button:Save")
```

## What's tested

Tested (`scripts/run-tests.sh` runs headless with Xvfb, D-Bus and AT-SPI, against a GTK3 demo app; it also runs in CI):
- tree, find, click (the label changes to "saved"), type, read, focus, and the CLI's JSON output
- the compact text format

Not tested yet:
- Qt/KDE apps, Electron/Chrome apps (Chrome needs `--force-renderer-accessibility`), and Firefox
- a real Wayland compositor session. AT-SPI itself doesn't depend on the display server, but the keyboard and mouse fallback (`generate_*_event`) may not work on Wayland
- running the MCP server against a live agent client (the module loads and registers its tools)

## License

MIT
