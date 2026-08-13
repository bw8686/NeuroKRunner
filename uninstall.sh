#!/bin/bash

# Exit if something fails
set -xo pipefail

prefix="${XDG_DATA_HOME:-$HOME/.local/share}"
krunner_dbusdir="$prefix/krunner/dbusplugins"
services_dir="$prefix/dbus-1/services"
app_dir="$prefix/neurokrunner"

echo "Uninstalling NeuroKRunner..."

echo "Removing D-Bus service..."
rm -f "$services_dir/org.kde.neurokrunner.service"

echo "Removing KRunner plugin configuration..."
rm -f "$krunner_dbusdir/neurokrunner.desktop"

echo "Removing desktop application file..."
rm -f "$prefix/applications/neurokrunner.desktop"

echo "Removing application source files..."
rm -rf "$app_dir"

echo "Refreshing KDE system cache..."
kbuildsycoca6 &> /dev/null || true
kquitapp6 krunner &> /dev/null || true

echo "Uninstallation complete!"
