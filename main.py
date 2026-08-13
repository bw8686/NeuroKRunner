#!/usr/bin/python3

import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import urllib.request
import json
from datetime import datetime, timezone
import webbrowser
import subprocess
import threading
import sys
import os
import config

DBusGMainLoop(set_as_default=True)

objpath = "/runner"
iface = "org.kde.krunner1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def fetch_schedule():
    try:
        req = urllib.request.Request("https://schedule-api.nwero.net/schedule", headers={'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})
        with urllib.request.urlopen(req, timeout=3) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print("Error fetching schedule:", e)
        return []

def get_streams(query):
    schedule = fetch_schedule()
    now = datetime.now(timezone.utc)
    results = []
    
    q = query.lower().strip()
    
    target = None
    if "twins" in q:
        target = "twins"
    elif "neuro" in q:
        target = "neuro"
    elif "evil" in q:
        target = "evil"
    elif "vedal" in q:
        target = "vedal"
    elif "collab" in q:
        target = "collab"
    elif "schedule" in q or "next" in q or "any" in q:
        target = "any"

    if target is None:
        return results, None
        
    for item in schedule:
        if not item.get("live"):
            continue
            
        timestamp_str = item.get("timestamp", "")
        if not timestamp_str:
            continue
            
        try:
            ts_str = timestamp_str.replace("Z", "+0000")
            stream_time = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            continue
            
        if stream_time.timestamp() < now.timestamp() - 4 * 3600:
            continue
            
        streamers = [s.lower() for s in item.get("streamers", [])]
        
        match = False
        if target == "neuro":
            match = "neuro" in streamers
        elif target == "evil":
            match = "evil" in streamers
        elif target == "vedal":
            match = "vedal" in streamers
        elif target == "twins":
            match = "neuro" in streamers and "evil" in streamers
        elif target == "any":
            match = True
        elif target == "collab":
            match = any(s not in ["neuro", "evil", "vedal"] for s in streamers)
            
        if match:
            results.append((item, stream_time))
            
    return results, target

def poll_schedule():
    cfg = config.load_config()
    auto = cfg.get('auto_sub', {})
    if not any(auto.values()):
        return True # Continue polling later
        
    streams, _ = get_streams("any")
    for item, stream_time in streams:
        title = item.get("title", "Stream")
        streamers = [s.lower() for s in item.get("streamers", [])]
        
        should_sub = False
        if auto.get("all"):
            should_sub = True
        elif auto.get("twins") and "neuro" in streamers and "evil" in streamers:
            should_sub = True
        elif auto.get("neuro") and "neuro" in streamers:
            should_sub = True
        elif auto.get("evil") and "evil" in streamers:
            should_sub = True
        elif auto.get("vedal") and "vedal" in streamers:
            should_sub = True
        elif auto.get("collab") and any(s not in ["neuro", "evil", "vedal"] for s in streamers):
            should_sub = True
            
        sys_time = stream_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        time_str = stream_time.astimezone().strftime("%a %I:%M %p")
        sys_time_safe = sys_time.replace(" ", "_").replace(":", "-")
        auto_unit_name = f"neurokrunner-auto-{sys_time_safe}.timer"
        manual_unit_name = f"neurokrunner-{sys_time_safe}.timer"
        
        if should_sub:
            res_manual = subprocess.run(['systemctl', '--user', 'is-active', manual_unit_name], capture_output=True)
            if res_manual.returncode != 0:
                res_auto = subprocess.run(['systemctl', '--user', 'is-active', auto_unit_name], capture_output=True)
                if res_auto.returncode != 0 and sys_time_safe not in cfg.get("ignored_streams", []):
                    icon_name = cfg['icons']['schedule']
                    bash_script = f'''
res=$(notify-send -a 'NeuroKRunner' -i '{icon_name}' -A 'default=Watch Now' 'NeuroKRunner' '{title} is starting now!')
if [ "$res" = "default" ]; then xdg-open "https://twitch.tv/vedal987"; fi
'''
                    subprocess.call(['systemd-run', '--user', f'--unit={auto_unit_name}', f'--on-calendar={sys_time}', 'bash', '-c', bash_script])
        else:
            res_auto = subprocess.run(['systemctl', '--user', 'is-active', auto_unit_name], capture_output=True)
            if res_auto.returncode == 0:
                subprocess.call(['systemctl', '--user', 'stop', auto_unit_name])
                
    return True # Keep loop running

def handle_run(details):
    import sys
    cfg = config.load_config()
    title = details.get('title')
    streamers = details.get('streamers')
    time_str = details.get('time')
    sys_time = details.get('sys_time')
    target = details.get('target', 'any')
    
    if cfg['behavior']['direct_to_twitch']:
        webbrowser.open("https://twitch.tv/vedal987")
        return
    
    msg = f"Title: {title}\nStreamers: {streamers}\nTime: {time_str}"
    
    sys_time_safe = sys_time.replace(" ", "_").replace(":", "-")
    auto_unit_name = f"neurokrunner-auto-{sys_time_safe}.timer"
    manual_unit_name = f"neurokrunner-{sys_time_safe}.timer"
    
    res_auto = subprocess.run(['systemctl', '--user', 'is-active', auto_unit_name], capture_output=True)
    res_manual = subprocess.run(['systemctl', '--user', 'is-active', manual_unit_name], capture_output=True)
    is_active = str(res_auto.returncode == 0 or res_manual.returncode == 0)
    icon_name = details.get('icon', cfg['icons']['schedule'])
    
    UI_SCRIPT = """
import sys
title = sys.argv[1]
msg = sys.argv[2]
is_active = sys.argv[3] == "True"
icon_name = sys.argv[4]
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox, QCheckBox
    from PyQt6.QtGui import QIcon
    app = QApplication(sys.argv)
    app.setDesktopFileName('neurokrunner')
    app.setWindowIcon(QIcon.fromTheme(icon_name))
    
    msgBox = QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setWindowIcon(QIcon.fromTheme(icon_name))
    msgBox.setText(msg)
    pixmap = QIcon.fromTheme(icon_name).pixmap(64, 64)
    if not pixmap.isNull():
        msgBox.setIconPixmap(pixmap)
    else:
        msgBox.setIcon(QMessageBox.Icon.Information)
    cb = QCheckBox("Notify me")
    cb.setChecked(is_active)
    msgBox.setCheckBox(cb)
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    btn_twitch = msgBox.addButton("Watch on Twitch", QMessageBox.ButtonRole.ActionRole)
    msgBox.exec()
    if msgBox.clickedButton() == btn_twitch:
        print("twitch")
    if cb.isChecked():
        print("notify")
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    root = tk.Tk()
    root.title(title)
    root.geometry("500x250")
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)
    label = ttk.Label(frame, text=msg)
    label.pack(side=tk.TOP, anchor=tk.W)
    bottom_frame = ttk.Frame(frame)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
    var = tk.BooleanVar(value=is_active)
    chk = ttk.Checkbutton(bottom_frame, text="Notify me", variable=var)
    chk.pack(side=tk.LEFT)
    def on_ok():
        if var.get():
            print("notify")
        root.destroy()
    def on_twitch():
        print("twitch")
        root.destroy()
    btn = ttk.Button(bottom_frame, text="OK", command=on_ok)
    btn.pack(side=tk.RIGHT)
    btn2 = ttk.Button(bottom_frame, text="Watch on Twitch", command=on_twitch)
    btn2.pack(side=tk.RIGHT)
    root.mainloop()
"""
    try:
        result = subprocess.run([sys.executable, '-c', UI_SCRIPT, 'Stream Details', msg, is_active, icon_name], capture_output=True, text=True)
        checked = 'notify' in result.stdout
        twitch = 'twitch' in result.stdout
        ret = result.returncode
    except Exception:
        return
        
    if twitch:
        webbrowser.open("https://twitch.tv/vedal987")
            
    if ret == 0 and sys_time:
        if checked and is_active == "False":
            try:
                # Remove from ignored streams if present
                ignored = cfg.get("ignored_streams", [])
                if sys_time_safe in ignored:
                    ignored.remove(sys_time_safe)
                    cfg["ignored_streams"] = ignored
                    config.save_config(cfg)
                    
                bash_script = f'''
res=$(notify-send -a 'NeuroKRunner' -i '{icon_name}' -A 'default=Watch Now' 'NeuroKRunner' '{title} is starting now!')
if [ "$res" = "default" ]; then xdg-open "https://twitch.tv/vedal987"; fi
'''
                subprocess.call(['systemd-run', '--user', f'--unit={manual_unit_name}', f'--on-calendar={sys_time}', 'bash', '-c', bash_script])
                confirm_script = f'''
res=$(notify-send -a 'NeuroKRunner' -i '{icon_name}' -A 'default=Watch Now' 'NeuroKRunner' 'Reminder set! You will be notified for {title} at {time_str}')
if [ "$res" = "default" ]; then xdg-open "https://twitch.tv/vedal987"; fi
'''
                subprocess.Popen(['bash', '-c', confirm_script])
            except Exception as e:
                print(e)
        elif not checked and is_active == "True":
            try:
                # Add to ignored streams so it doesn't get auto-added again
                ignored = cfg.get("ignored_streams", [])
                if sys_time_safe not in ignored:
                    ignored.append(sys_time_safe)
                    # Keep list small to avoid endless growth, e.g. last 100
                    cfg["ignored_streams"] = ignored[-100:]
                    config.save_config(cfg)
                    
                if res_auto.returncode == 0:
                    subprocess.call(['systemctl', '--user', 'stop', auto_unit_name])
                if res_manual.returncode == 0:
                    subprocess.call(['systemctl', '--user', 'stop', manual_unit_name])
                subprocess.Popen(['notify-send', '-a', 'NeuroKRunner', '-i', icon_name, 'NeuroKRunner', f'Reminder canceled for {title}'])
            except Exception as e:
                print(e)

class Runner(dbus.service.Object):
    def __init__(self):
        dbus.service.Object.__init__(self, dbus.service.BusName("org.kde.neurokrunner", dbus.SessionBus()), objpath)
        
        # Trigger initial poll
        GLib.timeout_add(3000, poll_schedule)
        GLib.timeout_add_seconds(3600, poll_schedule)

    @dbus.service.method(iface, in_signature='s', out_signature='a(sssida{sv})')
    def Match(self, query: str):
        q = query.lower().strip()
        cfg = config.load_config()
        
        if "settings" in q:
            return [("settings", "Configure NeuroKRunner", "preferences-system", 100, 1.0, {'subtext': 'Open Settings UI'})]
        
        if "schedule" not in q and "next" not in q:
            return []
            
        streams, target = get_streams(q)
        if not streams:
            # Fallback icon for 'no streams found' message
            fb_icon = cfg['icons'].get('schedule', '')
            if target == "neuro": fb_icon = cfg['icons'].get('neuro', '')
            elif target == "evil": fb_icon = cfg['icons'].get('evil', '')
            elif target == "twins": fb_icon = cfg['icons'].get('twins', '')
            elif target == "vedal": fb_icon = cfg['icons'].get('vedal', '')
            return [("schedule", "No upcoming stream found", fb_icon, 100, 1.0, {'subtext': f'For query: {query}'})]
            
        results = []
        relevance = 1.0
        for i, (item, stream_time) in enumerate(streams):
            title = item.get("title", "Stream")
            time_str = stream_time.astimezone().strftime("%a %I:%M %p")
            sys_time = stream_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
            streamers_list = [s.lower() for s in item.get("streamers", [])]
            streamers = ", ".join(item.get("streamers", []))
            
            # Determine icon based on THIS specific stream's participants
            icon = cfg['icons'].get('schedule', '')
            if "neuro" in streamers_list and "evil" in streamers_list:
                icon = cfg['icons'].get('twins', '')
            elif "neuro" in streamers_list:
                icon = cfg['icons'].get('neuro', '')
            elif "evil" in streamers_list:
                icon = cfg['icons'].get('evil', '')
            elif "vedal" in streamers_list:
                icon = cfg['icons'].get('vedal', '')
            
            if target in ["neuro", "evil", "vedal", "twins"]:
                text = title
            else:
                text = f"{title} ({streamers})"
                
            subtext = time_str
            
            details = {
                "title": title,
                "streamers": streamers,
                "time": time_str,
                "sys_time": sys_time,
                "target": target,
                "icon": icon
            }
            data_str = "schedule:" + json.dumps(details)
            
            results.append((data_str, text, icon, 100, relevance, {'subtext': subtext}))
            relevance -= 0.01
            
        return results

    @dbus.service.method(iface, out_signature='a(sss)')
    def Actions(self):
        return []

    @dbus.service.method(iface, in_signature='ss')
    def Run(self, data: str, action_id: str):
        if data == "settings":
            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'settings_ui.py')])
            return
            
        if data.startswith("schedule:"):
            try:
                details = json.loads(data.split(":", 1)[1])
                threading.Thread(target=handle_run, args=(details,)).start()
            except Exception as e:
                print(e)


runner = Runner()
loop = GLib.MainLoop()
loop.run()
