from enum import StrEnum


class AppType(StrEnum):
    Antivirus = 'Antivirus'
    Browser = 'browser'
    FeedReader = 'feed reader'
    Game = 'game'
    Library = 'library'
    MediaPlayer = 'mediaplayer'
    Messaging = 'messaging'
    Navigation = 'navigation'
    OsUtility = 'osutility'
    P2P = 'p2p'
    PIM = 'pim'
    VpnProxy = 'vpnproxy'

    # Generic types
    DesktopApp = 'desktop app'
    MobileApp = 'mobile app'
    Generic = 'generic'
    Unknown = ''


class DeviceType(StrEnum):
    Desktop = 'desktop'
    Smartphone = 'smartphone'
    Tablet = 'tablet'
    FeaturePhone = 'feature phone'
    Console = 'console'
    TV = 'tv'  # including set-top boxes, Blu-ray players
    CarBrowser = 'car browser'
    SmartDisplay = 'smart display'
    Camera = 'camera'
    PortableMediaPlayer = 'portable media player'
    Phablet = 'phablet'
    SmartSpeaker = 'smart speaker'
    Wearable = 'wearable'  # including set watches, headsets
    Peripheral = 'peripheral'  # including portable terminal, portable projector
    Unknown = ''
