#!/usr/bin/env bash
# Headless session: Xvfb + D-Bus + AT-SPI bus, then pytest.
set -e
export DISPLAY=:99 GTK_MODULES=gail:atk-bridge NO_AT_BRIDGE=0
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & XPID=$!
sleep 1
eval "$(dbus-launch --sh-syntax)"
P=$(python -c 'import sys;print(sys.prefix)')
for d in "$P/libexec" /usr/libexec/at-spi2-core /usr/libexec /usr/lib/at-spi2-core; do
  [ -x "$d/at-spi-bus-launcher" ] && { "$d/at-spi-bus-launcher" --launch-immediately & break; }
done
sleep 2
trap 'kill $XPID $DBUS_SESSION_BUS_PID 2>/dev/null' EXIT
python -m pytest -q tests
