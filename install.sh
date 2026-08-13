set -e

prefix="${XDG_DATA_HOME:-$HOME/.local/share}"
krunner_dbusdir="$prefix/krunner/dbusplugins"
services_dir="$prefix/dbus-1/services/"
# Define a permanent folder for your app files
app_dir="$prefix/neurokrunner"

echo "Setting up directories..."
mkdir -p "$krunner_dbusdir"
mkdir -p "$services_dir"
mkdir -p "$prefix/applications"
mkdir -p "$app_dir"

echo "Copying application source files..."
# Copy everything (Python scripts, QML, assets) to the permanent directory
cp -r main.py config.py settings_ui.py settings.qml assets/ "$app_dir/"
chmod +x "$app_dir/main.py"

echo "Configuring desktop file with absolute icon paths..."
# Point to the permanent assets folder instead of $PWD
sed "s|Icon=planetkde|Icon=$app_dir/assets/neuro.png|" neurokrunner.desktop > /tmp/neurokrunner.desktop

echo "Copying plugin files..."
cp /tmp/neurokrunner.desktop "$krunner_dbusdir/"
cp /tmp/neurokrunner.desktop "$prefix/applications/"

echo "Registering D-Bus service..."
# Point the D-Bus service file to the permanent location
printf "[D-BUS Service]\nName=org.kde.neurokrunner\nExec=$app_dir/main.py\n" > "$services_dir/org.kde.neurokrunner.service"

echo "Refreshing KDE system cache..."
pkill -f main.py || true
kbuildsycoca6 &> /dev/null || true
kquitapp6 krunner &> /dev/null || true

echo "Installation complete! Try opening KRunner and typing 'schedule' or 'neuro settings'."
