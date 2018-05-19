# DeviceDetector

DeviceDetector is a precise and fast user agent parser and device detector written in Python, backed by the largest and most up-to-date user agent database.

DeviceDetector will parse any user agent and detect the browser, operating system, device used (desktop, tablet, mobile, tv, cars, console, etc.), brand and model. DeviceDetector detects thousands of user agent strings, even from rare and obscure browsers and devices.

The DeviceDetector is optimized for speed of detection, by providing optimized code and in-memory caching.

This project originated as a Python port of the Universal Device Detection library.
You can find the original code https://github.com/matomo-org/device-detector.

## Disclaimer

This port is not an exact copy of the original code; some Pythonic adaptations were used.
However, it uses the original regex yaml files, to benefit from updates and pull request to both the original and the ported versions.

## Installation

`pip install device_detector`

## Performance Options

[CSafeLoader](http://pyyaml.org/wiki/PyYAMLDocumentation) is used if pyyaml is configured `--with-libyaml`.

The [mrab regex](https://pypi.org/project/regex/) module is preferred if installed.

## Usage
```python
from device_detector import DeviceDetector

ua = 'Mozilla/5.0 (Linux; Android 4.3; C5502 Build/10.4.1.B.0.101) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.136 Mobile Safari/537.36'

# Parse UA string and load data to dict of 'os', 'client', 'device' keys
device = DeviceDetector(ua).parse()

# Use helper methods to extract data by attribute

device.is_bot()      # >>> False

device.os_name()     # >>> Android
device.os_version()  # >>> 4.3
device.engine()      # >>> WebKit

device.device_brand_name()  # >>> Sony
device.device_brand()       # >>> SO
device.device_model()       # >>> Xperia ZR
device.device_type()        # >>> smartphone

```

## Device Detector for other languages

There are already a few ports of this tool to other languages:

- **.NET** https://github.com/totpero/DeviceDetector.NET
- **Ruby** https://github.com/podigee/device_detector
- **Node.JS** https://github.com/sanchezzzhak/node-device-detector
- **Python 3** https://github.com/thinkwelltwd/device_detector

## What Device Detector is able to detect

The lists below are auto generated and updated from time to time. Some of them might not be complete.

*Last update: 2018/05/07*

### List of detected operating systems:

AIX, Android, AmigaOS, Apple TV, Arch Linux, BackTrack, Bada, BeOS, BlackBerry OS, BlackBerry Tablet OS, Brew, CentOS, Chrome OS, CyanogenMod, Debian, DragonFly, Fedora, Firefox OS, FreeBSD, Gentoo, Google TV, HP-UX, Haiku OS, IRIX, Inferno, Knoppix, Kubuntu, GNU/Linux, Lubuntu, VectorLinux, Mac, Maemo, Mandriva, MeeGo, MocorDroid, Mint, MildWild, MorphOS, NetBSD, MTK / Nucleus, Nintendo, Nintendo Mobile, OS/2, OSF1, OpenBSD, PlayStation Portable, PlayStation, Red Hat, RISC OS, Remix OS, RazoDroiD, Sabayon, SUSE, Sailfish OS, Slackware, Solaris, Syllable, Symbian, Symbian OS, Symbian OS Series 40, Symbian OS Series 60, Symbian^3, ThreadX, Tizen, Ubuntu, WebTV, Windows, Windows CE, Windows IoT, Windows Mobile, Windows Phone, Windows RT, Xbox, Xubuntu, YunOs, iOS, palmOS, webOS

### List of detected browsers:

360 Phone Browser, 360 Browser, Avant Browser, ABrowse, ANT Fresco, ANTGalio, Aloha Browser, Amaya, Amigo, Android Browser, Arora, Amiga Voyager, Amiga Aweb, Atomic Web Browser, BlackBerry Browser, Baidu Browser, Baidu Spark, Beonex, Bunjalloo, B-Line, Brave, BriskBard, BrowseX, Camino, Coc Coc, Comodo Dragon, Coast, Charon, Chrome Frame, Chrome, Chrome Mobile iOS, Conkeror, Chrome Mobile, CoolNovo, CometBird, ChromePlus, Chromium, Cyberfox, Cheshire, dbrowser, Deepnet Explorer, Dolphin, Dorado, Dooble, Dillo, Epic, Elinks, Element Browser, GNOME Web, Espial TV Browser, Firebird, Fluid, Fennec, Firefox, Firefox Focus, Flock, Firefox Mobile, Fireweb, Fireweb Navigator, Galeon, Google Earth, HotJava, Iceape, IBrowse, iCab, iCab Mobile, Iridium, IceDragon, Isivioo, Iceweasel, Internet Explorer, IE Mobile, Iron, Jasmine, Jig Browser, Kindle Browser, K-meleon, Konqueror, Kapiko, Kylo, Kazehakase, Liebao, LG Browser, Links, LuaKit, Lunascape, Lynx, MicroB, NCSA Mosaic, Mercury, Mobile Safari, Midori, MIUI Browser, Mobile Silk, Maxthon, Nokia Browser, Nokia OSS Browser, Nokia Ovi Browser, NetSurf, NetFront, NetFront Life, NetPositive, Netscape, Obigo, Odyssey Web Browser, Off By One, ONE Browser, Opera Mini, Opera Mobile, Opera, Opera Next, Oregano, Openwave Mobile Browser, OmniWeb, Otter Browser, Palm Blazer, Pale Moon, Palm Pre, Puffin, Palm WebPro, Palmscape, Phoenix, Polaris, Polarity, Microsoft Edge, QQ Browser, Qutebrowser, QupZilla, Rekonq, RockMelt, Samsung Browser, Sailfish Browser, SEMC-Browser, Sogou Explorer, Safari, Shiira, Skyfire, Seraphic Sraf, Sleipnir, SeaMonkey, Snowshoe, Sunrise, SuperBird, Streamy, Swiftfox, Tizen Browser, TweakStyle, UC Browser, Vivaldi, Vision Mobile Browser, WebPositive, Waterfox, wOSBrowser, WeTab Browser, Yandex Browser, Xiino

### List of detected browser engines:

WebKit, Blink, Trident, Text-based, Dillo, iCab, Elektra, Presto, Gecko, KHTML, NetFront, Edge, NetSurf

### List of detected libraries:

aiohttp, curl, Faraday, Go-http-client, Google HTTP Java Client, Guzzle (PHP HTTP Client), HTTP_Request2, Java, Mechanize, OkHttp, Perl, Python Requests, Python urllib, Wget, WWW-Mechanize

### List of detected media players:

Banshee, Boxee, Clementine, FlyCast, Foobar2000, Instacast, iTunes, Kodi, MediaMonkey, Miro, NexPlayer, Nightingale, QuickTime, Songbird, Stagefright, SubStream, VLC, Winamp, Windows Media Player, XBMC

### List of detected mobile apps:

AndroidDownloadManager, AntennaPod, Apple News, BeyondPod, bPod, Castro, Castro 2, DoggCatcher, Facebook, Facebook Messenger, FeedR, Google Play Newsstand, Google Plus, iCatcher, Instacast, Line, Overcast, Pinterest, Player FM, Pocket Casts, Podcasts, Podcat, Podcatcher Deluxe, Podkicker, Sina Weibo, WeChat, WhatsApp, Yelp Mobile, YouTube  and *mobile apps using [AFNetworking](https://github.com/AFNetworking/AFNetworking)*

### List of detected PIMs (personal information manager):

Airmail, Barca, DAVdroid, Lotus Notes, MailBar, Microsoft Outlook, Outlook Express, Postbox, The Bat!, Thunderbird

### List of detected feed readers:

Akregator, Apple PubSub, BashPodder, Downcast, FeedDemon, Feeddler RSS Reader, gPodder, Instacast, JetBrains Omea Reader, Liferea, NetNewsWire, Newsbeuter, NewsBlur, NewsBlur Mobile App, PritTorrent, Pulp, ReadKit, Reeder, RSS Bandit, RSS Junkie, RSSOwl, Stringer

### List of brands with detected devices:

3Q, 4Good, Acer, Ainol, Airness, Airties, Alcatel, Allview, Altech UEC, Amazon, Amoi, Apple, Archos, Arnova, ARRIS, Asus, Audiovox, Avvio, Axxion, Azumi Mobile, BangOlufsen, Barnes & Noble, BBK, Becker, Beetel, BenQ, BenQ-Siemens, BGH, Bird, Bitel, Blackview, Blaupunkt, Blu, Bmobile, Boway, bq, Bravis, Brondi, Bush, Capitel, Captiva, Carrefour, Casio, Cat, Celkon, Changhong, Cherry Mobile, China Mobile, CnM, Coby Kyros, Compal, Compaq, ConCorde, Condor, Coolpad, Cowon, CreNova, Cricket, Crius Mea, Crosscall, Cube, CUBOT, Cyrus, Danew, Datang, Dbtel, Dell, Denver, Desay, DEXP, Dicam, Digma, DMM, DNS, DoCoMo, Doogee, Doov, Dopod, Doro, Dune HD, E-Boda, Easypix, EBEST, ECS, EKO, Elephone, Energy Sistem, Ericsson, Ericy, Eton, eTouch, Evertek, Evolveo, Explay, Ezio, Ezze, Fairphone, Fly, Foxconn, Freetel, Fujitsu, Garmin-Asus, Gateway, Gemini, Gigabyte, Gigaset, Gionee, GOCLEVER, Goly, Google, Gradiente, Grundig, Haier, HannSpree, Hasee, Hi-Level, Hisense, Homtom, Hosin, HP, HTC, Huawei, Humax, Hyrican, Hyundai, i-Joy, i-mate, i-mobile, iBall, iBerry, IconBIT, Ikea, iKoMo, iNew, Infinix, Inkti, Innostream, INQ, Intek, Intex, Inverto, iOcean, iTel, JAY-Tech, Jiayu, Jolla, K-Touch, Karbonn, Kazam, KDDI, Kiano, Kingsun, Komu, Konka, Konrow, Koobee, KOPO, Koridy, KT-Tech, Kumai, Kyocera, Landvo, Lanix, Lava, LCT, LeEco, Lenco, Lenovo, Le Pan, Lexand, Lexibook, LG, Lingwin, Loewe, Logicom, LYF, M.T.T., Majestic, Manta Multimedia, Mecer, Mediacom, MediaTek, Medion, MEEG, Meizu, Memup, Metz, MEU, MicroMax, Microsoft, Mio, Mitsubishi, MIXC, MLLED, Mobistel, Modecom, Mofut, Motorola, Mpman, MSI, MyPhone, NEC, Neffos, Netgear, Newgen, Nexian, NextBook, NGM, Nikon, Nintendo, Noain, Noblex, Nokia, Nomi, Nous, Nvidia, O2, Obi, Odys, Onda, OnePlus, OPPO, Opsson, Orange, Ouki, OUYA, Overmax, Oysters, Palm, Panasonic, Pantech, PEAQ, Pentagram, Philips, phoneOne, Pioneer, Ployer, Point of View, Polaroid, PolyPad, Pomp, Positivo, PPTV, Prestigio, ProScan, PULID, Qilive, QMobile, Qtek, Quechua, Ramos, RCA Tablets, Readboy, Rikomagic, RIM, Roku, Rover, Sagem, Samsung, Sanyo, Sega, Selevision, Sencor, Sendo, Senseit, SFR, Sharp, Siemens, Skyworth, Smart, Smartfren, Smartisan, Softbank, Sony, Sony Ericsson, Spice, Star, STK, Stonex, Storex, Sumvision, SunVan, SuperSonic, Supra, Symphony, T-Mobile, TB Touch, TCL, TechniSat, TechnoTrend, Teclast, Tecno Mobile, Telefunken, Telenor, Telit, Tesco, Tesla, teXet, ThL, Thomson, TIANYU, TiPhone, Tolino, Toplux, Toshiba, TrekStor, Trevi, Tunisie Telecom, Turbo-X, TVC, Ulefone, UMIDIGI, Uniscope, Unknown, Unowhy, UTStarcom, Vastking, Vertu, Verykool, Vestel, Videocon, Videoweb, ViewSonic, Vitelcom, Vivo, Vizio, VK Mobile, Vodafone, Voto, Voxtel, Walton, Web TV, WellcoM, Wexler, Wiko, Wileyfox, Wolder, Wolfgang, Wonu, Woxter, Xiaomi, Xolo, Yarvik, Ytone, Yuandao, Yusun, Zeemi, Zen, Zonda, Zopo, ZTE

### List of detected bots:

360Spider, Aboundexbot, Acoon, AddThis.com, ADMantX, aHrefs Bot, Alexa Crawler, Amorank Spider, Analytics SEO Crawler, ApacheBench, Applebot, archive.org bot, Ask Jeeves, Backlink-Check.de, BacklinkCrawler, Baidu Spider, BazQux Reader, BingBot, BitlyBot, Blekkobot, BLEXBot Crawler, Bloglovin, Blogtrottr, Bountii Bot, Browsershots, BUbiNG, Butterfly Robot, CareerBot, Castro 2, Catchpoint, ccBot crawler, Charlotte, Cliqzbot, CloudFlare Always Online, CloudFlare AMP Fetcher, Collectd, CommaFeed, CSS Certificate Spider, Cốc Cốc Bot, Datadog Agent, Dataprovider, Daum, Dazoobot, Discobot, Domain Re-Animator Bot, DotBot, DuckDuckGo Bot, Easou Spider, EMail Exractor, EmailWolf, evc-batch, ExaBot, ExactSeek Crawler, Ezooms, Facebook External Hit, Feedbin, FeedBurner, Feedly, Feedspot, Feed Wrangler, Fever, Findxbot, Flipboard, Generic Bot, Generic Bot, Genieo Web filter, Gigablast, Gigabot, Gluten Free Crawler, Gmail Image Proxy, Goo, Googlebot, Google PageSpeed Insights, Google Partner Monitoring, Google Structured Data Testing Tool, Grapeshot, Heritrix, Heureka Feed, HTTPMon, HubPages, HubSpot, ICC-Crawler, ichiro, IIS Site Analysis, Inktomi Slurp, IP-Guide Crawler, IPS Agent, Kouio, Larbin web crawler, Let's Encrypt Validation, Lighthouse, Linkdex Bot, LinkedIn Bot, LTX71, Lycos, Magpie-Crawler, MagpieRSS, Mail.Ru Bot, masscan, Meanpath Bot, MetaInspector, MetaJobBot, Mixrank Bot, MJ12 Bot, Mnogosearch, MojeekBot, Monitor.Us, Munin, Nagios check_http, NalezenCzBot, Netcraft Survey Bot, netEstate, NetLyzer FastProbe, NetResearchServer, Netvibes, NewsBlur, NewsGator, NLCrawler, Nmap, Nutch-based Bot, Octopus, Omgili bot, Openindex Spider, OpenLinkProfiler, OpenWebSpider, Orange Bot, Outbrain, PagePeeker, PaperLiBot, Phantomas, PHP Server Monitor, Picsearch bot, Pingdom Bot, Pinterest, PocketParser, Pompos, PritTorrent, QuerySeekerSpider, Qwantify, Rainmeter, RamblerMail Image Proxy, Reddit Bot, Riddler, Rogerbot, ROI Hunter, SafeDNSBot, Scooter, ScoutJet, Scrapy, Screaming Frog SEO Spider, ScreenerBot, Semrush Bot, Sensika Bot, Sentry Bot, SEOENGBot, SEOkicks-Robot, Seoscanners.net, Server Density, Seznam Bot, Seznam Email Proxy, Seznam Zbozi.cz, ShopAlike, ShopWiki, SilverReader, SimplePie, SISTRIX Crawler, Site24x7 Website Monitoring, SiteSucker, Sixy.ch, Skype URI Preview, Slackbot, Sogou Spider, Soso Spider, Sparkler, Speedy, Spinn3r, Sputnik Bot, sqlmap, SSL Labs, StatusCake, Superfeedr Bot, Survey Bot, Tarmot Gezgin, TelgramBot, TinEye Crawler, Tiny Tiny RSS, TLSProbe, Trendiction Bot, TurnitinBot, TweetedTimes Bot, Tweetmeme Bot, Twitterbot, UkrNet Mail Proxy, UniversalFeedParser, Uptimebot, Uptime Robot, URLAppendBot, Vagabondo, Visual Site Mapper Crawler, W3C CSS Validator, W3C I18N Checker, W3C Link Checker, W3C Markup Validation Service, W3C MobileOK Checker, W3C Unified Validator, Wappalyzer, WebbCrawler, WebSitePulse, WebThumbnail, WeSEE:Search, Willow Internet Crawler, WordPress, Wotbox, YaCy, Yahoo! Cache System, Yahoo! Link Preview, Yahoo! Slurp, Yahoo Gemini, Yandex Bot, Yeti/Naverbot, Yottaa Site Monitor, Youdao Bot, Yourls, Yunyun Bot, Zao, zgrab, Zookabot, ZumBot
