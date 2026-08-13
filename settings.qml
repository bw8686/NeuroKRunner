import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.ApplicationWindow {
    id: root
    width: 600
    height: 650
    title: "NeuroKRunner Settings"

    property var cfg: backend.getConfig()

    pageStack.initialPage: Kirigami.ScrollablePage {
        title: "Configuration"
        
        Kirigami.FormLayout {
            id: formLayout
            width: parent.width

            // --- Notifications Section ---
            Item {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: "Background Auto-Subscribe"
            }
            
            Controls.Label {
                text: "Automatically schedule system reminders when the schedule updates:"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Flow {
                Kirigami.FormData.label: "Streams"
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing
                
                Controls.CheckBox {
                    id: chkAll
                    text: "All Streams"
                    checked: cfg.auto_sub.all
                }
                Controls.CheckBox {
                    id: chkNeuro
                    text: "Neuro"
                    checked: cfg.auto_sub.neuro
                }
                Controls.CheckBox {
                    id: chkEvil
                    text: "Evil"
                    checked: cfg.auto_sub.evil
                }
                Controls.CheckBox {
                    id: chkTwins
                    text: "Twins"
                    checked: cfg.auto_sub.twins || false
                }
                Controls.CheckBox {
                    id: chkVedal
                    text: "Vedal"
                    checked: cfg.auto_sub.vedal
                }
                Controls.CheckBox {
                    id: chkCollab
                    text: "Collab"
                    checked: cfg.auto_sub.collab || false
                }
            }
            
            // --- Custom Icons Section ---
            Item {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: "Custom Icons"
            }
            
            Controls.Label {
                text: "Select custom icons for KRunner results and notifications. You can use standard KDE icon names or upload an image file."
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            RowLayout {
                Kirigami.FormData.label: "Schedule Icon:"
                Controls.TextField {
                    id: inSchedule
                    text: cfg.icons.schedule
                    Layout.fillWidth: true
                }
                Controls.Button {
                    text: "Browse..."
                    onClicked: {
                        let path = backend.browseIcon()
                        if (path !== "") inSchedule.text = path
                    }
                }
            }
            
            RowLayout {
                Kirigami.FormData.label: "Vedal Icon:"
                Controls.TextField {
                    id: inVedal
                    text: cfg.icons.vedal
                    Layout.fillWidth: true
                }
                Controls.Button {
                    text: "Browse..."
                    onClicked: {
                        let path = backend.browseIcon()
                        if (path !== "") inVedal.text = path
                    }
                }
            }
            
            RowLayout {
                Kirigami.FormData.label: "Neuro Icon:"
                Controls.TextField {
                    id: inNeuro
                    text: cfg.icons.neuro
                    Layout.fillWidth: true
                }
                Controls.Button {
                    text: "Browse..."
                    onClicked: {
                        let path = backend.browseIcon()
                        if (path !== "") inNeuro.text = path
                    }
                }
            }
            
            RowLayout {
                Kirigami.FormData.label: "Evil Icon:"
                Controls.TextField {
                    id: inEvil
                    text: cfg.icons.evil
                    Layout.fillWidth: true
                }
                Controls.Button {
                    text: "Browse..."
                    onClicked: {
                        let path = backend.browseIcon()
                        if (path !== "") inEvil.text = path
                    }
                }
            }
            
            RowLayout {
                Kirigami.FormData.label: "Twins Icon:"
                Controls.TextField {
                    id: inTwins
                    text: cfg.icons.twins
                    Layout.fillWidth: true
                }
                Controls.Button {
                    text: "Browse..."
                    onClicked: {
                        let path = backend.browseIcon()
                        if (path !== "") inTwins.text = path
                    }
                }
            }
            
            // --- Behavior Section ---
            Item {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: "Behavior"
            }
            
            Controls.CheckBox {
                id: chkTwitch
                Kirigami.FormData.label: "Twitch Integration:"
                text: "Clicking results bypasses dialog"
                checked: cfg.behavior.direct_to_twitch
            }
        }
        
        footer: Controls.ToolBar {
            RowLayout {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.smallSpacing
                Item { Layout.fillWidth: true }
                Controls.Button {
                    text: "Cancel"
                    onClicked: root.close()
                }
                Controls.Button {
                    text: "Save Settings"
                    onClicked: {
                        var newCfg = {
                            "auto_sub": {
                                "all": chkAll.checked,
                                "neuro": chkNeuro.checked,
                                "evil": chkEvil.checked,
                                "vedal": chkVedal.checked,
                                "twins": chkTwins.checked,
                                "collab": chkCollab.checked
                            },
                            "icons": {
                                "schedule": inSchedule.text,
                                "vedal": inVedal.text,
                                "neuro": inNeuro.text,
                                "evil": inEvil.text,
                                "twins": inTwins.text
                            },
                            "behavior": {
                                "direct_to_twitch": chkTwitch.checked
                            }
                        }
                        backend.saveConfig(newCfg)
                        root.close()
                    }
                }
            }
        }
    }
}
