# NeuroKRunner

A native KDE Plasma KRunner plugin to quickly check the upcoming stream schedule for Neuro-sama, Evil Neuro, and Vedal, and easily set desktop reminders!

Written in Python using the KRunner DBus API, featuring a native QML Kirigami configuration module that perfectly blends with your Plasma desktop!

### Features:
- Instantly search the upcoming stream schedule directly from KRunner.
- Filter by specific streamers (Neuro, Evil, Twins, Vedal, or Collabs).
- Click on any scheduled stream to set a system desktop reminder (using KDE's `notify-send` and `systemd` timers).
- Auto-subscribe to get background notifications whenever the schedule updates.
- Fully customizable icons and behaviors through a native KDE settings window.

### Screenshots:
*(Coming soon)*

### Syntax Examples:

`schedule` or `next` Shows the full upcoming schedule for all streams.
`neuro schedule` Shows only upcoming streams featuring Neuro-sama.
`evil schedule` Shows only upcoming streams featuring Evil Neuro.
`twins schedule` Shows upcoming streams where both Neuro-sama and Evil Neuro are present.
`vedal schedule` Shows upcoming streams featuring Vedal.
`collab schedule` Shows upcoming collabs.
`neuro settings` Opens the configuration UI to customize behavior and icons.

#### Settings:

*Access settings by typing `neuro settings` into KRunner.*

* **Background Auto-Subscribe:** Automatically set system reminders for streams whenever the schedule updates. You can toggle auto-subscriptions individually for All Streams, Neuro, Evil, Twins, Vedal, and Collabs.
* **Custom Icons:** Select custom icons to appear in KRunner results and desktop notifications. You can use standard KDE icon names (like `view-calendar`) or upload your own images by browsing for `.png` files.
* **Twitch Integration:** Toggle whether clicking a stream result sets a reminder dialog, or immediately opens Twitch in your default browser.

### Installation

#### Method 1: Via the KDE Store (Easiest)
1. Open **System Settings** -> **Search** -> **KRunner Plugins**.
2. Click **Get New Plugins...** at the bottom.
3. Search for **NeuroKRunner** and click **Install**.

#### Method 2: Manual Installation (GitHub)
If you prefer to clone the repository manually, run the following commands:
```bash
git clone https://github.com/bw8686/NeuroKRunner.git
cd NeuroKRunner
chmod +x install.sh
./install.sh
```


```bash
git clone https://github.com/bw8686/NeuroKRunner.git
cd NeuroKRunner
./install.sh
```

**Dependencies:**
- `python3`
- `python3-pyqt6` (For the settings UI and popups)
- `curl` (To fetch the schedule)
- `notify-send` (For system notifications)
