#!/usr/bin/env python3
"""
AllRecipes Crawler
A Selenium-based web crawler to collect and view recipe data from www.allrecipes.com
Collects: recipe name, ingredients, instructions, category, and an image
Version: 1.1
Author: Doug - TheAncientOne (TheAncientOneGH)
Github: https://github.com/TheAncientOneGH/All-Recipes-Crawler
Donate: https://www.paypal.com/donate/?hosted_button_id=JJ2KF3GDK9C38
"""
appname = "AllRecipes Crawler"
verstr = "1.1"
domhref = "https://"
domain = "www.allrecipes.com"
dbase = "allrec.db"

import os
import sys
import subprocess
import threading
import queue
import re
import time
import json
import signal
import argparse
import html
import sqlite3
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path

def inPack(pack):
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pack, "--upgrade", "--no-warn-script-location"])
        __import__(pack)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pack, "--no-warn-script-location"]
        )
    return

inPack("selenium")
inPack("urllib3")
inPack("Pillow")
inPack("webdriver-manager")
inPack("requests")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
BASE_URL = f"{domhref}{domain}"
DATA_DIR = Path("output")
DB_DIR = DATA_DIR / "db"
DB_FILE = DB_DIR / dbase
IMAGES_DIR = DATA_DIR / "images"
THUMBS_DIR = DATA_DIR / "thumbs"
RESUME_DIR = DATA_DIR / "resume"
COLLECTED_DIR = DATA_DIR / "resume/"
RESUME_FILE = RESUME_DIR / "resume.json"
COLLECTED_FILE = COLLECTED_DIR / "collected_recipes.json"
SKIP_DIR = Path("skip")
SKIP_FILE = SKIP_DIR / "skiplist.json"
IGNORE_FILE = SKIP_DIR / "ignore.json"
# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
THUMBS_DIR.mkdir(exist_ok=True)
RESUME_DIR.mkdir(exist_ok=True)
COLLECTED_DIR.mkdir(exist_ok=True)
SKIP_DIR.mkdir(exist_ok=True)
DEBUGEN = False

# Global variable for temporary image URL storage
_tempimage = None

# =============================================================================
# STEALTH ENGINE — Anti-detection module
# =============================================================================
class StealthEngine:
    """
    Comprehensive anti-detection engine that patches browser fingerprints
    and simulates human behavioral patterns to evade bot detection systems.
    Covers: CDP-level patches, JS runtime spoofing, behavioral randomness.
    """

    # Pre-generated pool of realistic user-agent strings (Chrome 120-130 range)
    UAS_POOL = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.49 Safari/537.36 Edg/127.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.55 Safari/537.36 Edg/126.0.0.0"
    ]

    # Realistic language preferences (weighted by global usage)
    LANG_POOL = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "de-DE,de;q=0.9,en-US;q=0.7",
        "fr-FR,fr;q=0.9,en-US;q=0.7",
        "es-ES,es;q=0.9,en-US;q=0.7",
        "pt-BR,pt;q=0.9,en-US;q=0.7",
        "ja-JP,ja;q=0.9,en-US;q=0.7",
        "zh-CN,zh;q=0.9,en-US;q=0.7",
        "ko-KR,ko;q=0.9,en;q=0.7",
        "it-IT,it;q=0.9,en-US;q=0.7",
        "nl-NL,nl;q=0.9,en-US;q=0.7",
        "ru-RU,ru;q=0.9,en-US;q=0.7",
    ]

    # Platform variations
    PLATFORMS = [
        "Win32", "Win64", "MacIntel", "Linux x86_64",
    ]

    # Hardware concurrency options
    HW_CONCURRENCY = [4, 8, 12, 16]

    # Device memory options (in GB, reported as integer)
    DEVICE_MEMORY = [4, 8, 16, 32]

    # Screen resolutions (common user configurations)
    SCREEN_RESOLUTIONS = [
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (2560, 1440), (1280, 720), (1600, 900), (1920, 1200),
    ]

    # Color depths
    COLOR_DEPTHS = [24, 30, 16]

    @staticmethod
    def random_ua():
        return random.choice(StealthEngine.UAS_POOL)

    @staticmethod
    def random_lang():
        return random.choice(StealthEngine.LANG_POOL)

    @staticmethod
    def random_platform():
        return random.choice(StealthEngine.PLATFORMS)

    @staticmethod
    def random_hw_concurrency():
        return random.choice(StealthEngine.HW_CONCURRENCY)

    @staticmethod
    def random_device_memory():
        return random.choice(StealthEngine.DEVICE_MEMORY)

    @staticmethod
    def random_resolution():
        return random.choice(StealthEngine.SCREEN_RESOLUTIONS)

    @staticmethod
    def random_color_depth():
        return random.choice(StealthEngine.COLOR_DEPTHS)

    @staticmethod
    def human_delay(min_sec=0.5, max_sec=2.0):
        """Simulate human reaction delay between actions"""
        time.sleep(random.uniform(min_sec, max_sec))

    @staticmethod
    def random_scroll_pause():
        """Random short pause to simulate reading"""
        time.sleep(random.uniform(0.3, 1.2))

    @staticmethod
    def jittered_sleep(base_sec=1.0, jitter=0.5):
        """Sleep with randomized jitter to avoid pattern detection"""
        time.sleep(base_sec + random.uniform(-jitter, jitter))

# Inject stealth scripts at the CDP/browser level
STEALTH_JS_AT_RUNTIME = r"""
(function() {
    // === PLUGINS SPOOFING ===
    var plugins = [];
    var pluginData = [
        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format'},
        {name: 'Native Client', filename: 'internal-nacl-plugin', description: 'NaCl plugin'}
    ];
    for (var i = 0; i < pluginData.length; i++) {
        var p = pluginData[i];
        plugins.push({
            name: p.name,
            filename: p.filename,
            description: p.description,
            length: 1,
            '__mimeTypes': [{
                type: 'application/x-google-chrome-pdf' || 'application/pdf',
                description: 'Portable Document Format',
                suffixes: 'pdf'
            }]
        });
    }
    // Spoof navigator.plugins
    try {
        Object.defineProperty(navigator, 'plugins', {
            get: function() { return plugins; },
            configurable: false,
            enumerable: false
        });
    } catch(e) {}

    // === LANGUAGES SPOOFING ===
    try {
        Object.defineProperty(navigator, 'languages', {
            get: function() { return ['en-US', 'en']; },
            configurable: false,
            enumerable: false
        });
    } catch(e) {}

    // === PLATFORM SPOOFING ===
    try {
        Object.defineProperty(navigator, 'platform', {
            get: function() { return 'Win32'; },
            configurable: false,
            enumerable: false
        });
    } catch(e) {}

    // === HARDWARE CONCURRENCY SPOOFING ===
    try {
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: function() { return 8; },
            configurable: false,
            enumerable: false
        });
    } catch(e) {}

    // === DEVICE MEMORY SPOOFING ===
    try {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: function() { return 8; },
            configurable: false,
            enumerable: false
        });
    } catch(e) {}

    // === COLOR DEPTH ===
    try {
        Object.defineProperty(window.screen, 'colorDepth', {
            get: function() { return 24; },
            configurable: false,
            enumerable: false
        });
    } catch(e) {}

    // === WEBGL VENDOR/RENDERER SPOOFING ===
    try {
        var getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';  // UNMASKED_VENDOR_WEBGL
            if (parameter === 37446) return 'Intel Iris OpenGL Engine';  // UNMASKED_RENDERER_WEBGL
            return getParameter.call(this, parameter);
        };
    } catch(e) {}

    try {
        var getParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter2.call(this, parameter);
        };
    } catch(e) {}

    // === CANVAS FINGERPRINT NOISE ===
    try {
        var originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            if (this.width === 0 && this.height === 0) {
                return originalToDataURL.call(this, type);
            }
            var context = this.getContext('2d');
            if (context) {
                var imageData = context.getImageData(0, 0, this.width, this.height);
                for (var i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] = imageData.data[i] ^ (Math.random() > 0.5 ? 1 : 0);
                    imageData.data[i+1] = imageData.data[i+1] ^ (Math.random() > 0.5 ? 1 : 0);
                    imageData.data[i+2] = imageData.data[i+2] ^ (Math.random() > 0.5 ? 1 : 0);
                }
                context.putImageData(imageData, 0, 0);
            }
            return originalToDataURL.call(this, type);
        };
    } catch(e) {}

    // === NOTIFICATION PERMISSION SPOOFING ===
    try {
        Object.defineProperty(Notification, 'permission', {
            get: function() { return 'default'; },
            configurable: false
        });
    } catch(e) {}

    // === CHROME RUNTIME SPOOFING ===
    try {
        window.chrome = {
            runtime: {
                connect: function() {},
                sendMessage: function() {},
                onMessage: { addListener: function() {}, removeListener: function() {} },
                id: undefined
            },
            loadTimes: function() { return {}; },
            csi: function() { return {}; },
            app: { isInstalled: false, InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' }, getDetails: function() {}, runningState: function() { return 'cannot_run'; } },
            webstore: { onInstallStageChanged: {}, onDownloadProgress: {} },
            management: { get: function() {}, getAll: function() {}, getSelf: function() {} },
            identity: { getAuthToken: function() {} },
            history: { visit: function() {}, deleteUrl: function() {}, getVisits: function() {} },
            cookies: { get: function() {}, getAll: function() {}, set: function() {}, remove: function() {}, getAllCookieStores: function() {} },
            downloads: { download: function() {}, erase: function() {}, search: function() {} },
            extension: { getURL: function() {}, getViews: function() {}, getBackgroundPage: function() {}, connect: function() {}, sendRequest: function() {}, onRequest: {}, onConnect: {} },
            i18n: { getMessage: function() {}, getUILanguage: function() {}, getAcceptLanguages: function() {} },
            permissions: { getAll: function() {}, contains: function() {}, request: function() {}, remove: function() {} }
        };
    } catch(e) {}

    // === WINDOW OUTER DIMENSIONS (headless detection) ===
    try {
        Object.defineProperty(window, 'outerWidth', {
            get: function() { return 1920; },
            configurable: false
        });
        Object.defineProperty(window, 'outerHeight', {
            get: function() { return 1080; },
            configurable: false
        });
    } catch(e) {}

    // === IFRAME CONTENTWINDOW DETECTION EVASION ===
    try {
        var originalContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
        if (!originalContentWindow) {
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    try { return this.contentWindow; } catch(e) { return null; }
                },
                configurable: true
            });
        }
    } catch(e) {}

    // === ERROR STACK TRACE CLEANUP ===
    try {
        var originalToString = Error.prototype.toString;
        Error.prototype.toString = function() {
            var str = originalToString.call(this);
            str = str.replace(/at .*?\\n/g, function(match) {
                if (match.includes('chrome-extension') || match.includes('puppeteer') || match.includes('selenium')) {
                    return '';
                }
                return match;
            });
            return str;
        };
    } catch(e) {}

    // === AUTOMATION CONTROLED FEATURE REMOVAL ===
    try {
        delete window.callPhantom;
        delete window._phantom;
    } catch(e) {}

    // === PERMISSIONS ENUMERATION DETECTION EVASION ===
    try {
        var originalQuery = navigator.permissions.query;
        navigator.permissions.query = function(params) {
            return originalQuery.call(this, params).then(function(permission) {
                if (permission.name === 'notifications') {
                    permission.state = 'default';
                }
                if (permission.name === 'push') {
                    permission.state = 'prompt';
                }
                return permission;
            });
        };
    } catch(e) {}

    // === MOUSE MOVEMENT SIMULATION (subtle, random) ===
    document.addEventListener('DOMContentLoaded', function() {
        var simulateMove = function() {
            var el = document.elementFromPoint(
                Math.floor(Math.random() * (window.innerWidth - 100)) + 50,
                Math.floor(Math.random() * (window.innerHeight - 100)) + 50
            );
            if (el) {
                var evt = new MouseEvent('mousemove', {
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: Math.random() * window.innerWidth,
                    clientY: Math.random() * window.innerHeight
                });
                el.dispatchEvent(evt);
            }
        };
        // Very subtle random movements
        setInterval(simulateMove, randomInterval(45000, 120000));
    });

    function randomInterval(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

})();
"""

# Second-stage stealth patch (executed after page load)
STEALTH_JS_POSTLOAD = r"""
(function() {
    // === PATCH ELEMENT COUNTING TECHNIQUES ===
    try {
        var origLength = Object.getOwnPropertyDescriptor(HTMLCollection.prototype, 'length');
        // No change needed, just ensure it works normally
    } catch(e) {}

    // === CANVAS RENDERING CONTEXT SPOOFING ===
    try {
        var origGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {
            if (contextType === 'webgl' || contextType === 'experimental-webgl' || contextType === 'webgl2') {
                var gl = origGetContext.call(this, contextType, contextAttributes);
                if (gl) {
                    var origGetExtension = gl.getExtension.bind(gl);
                    gl.getExtension = function(name) {
                        // Hide debugging extensions
                        if (name === 'WEBGL_debug_renderer_info') {
                            return null;
                        }
                        return origGetExtension(name);
                    };
                }
                return gl;
            }
            return origGetContext.call(this, contextType, contextAttributes);
        };
    } catch(e) {}

    // === BLOCK RESIZE OBSERVER (used to detect headless) ===
    try {
        var OrigResizeObserver = window.ResizeObserver;
        if (OrigResizeObserver) {
            window.ResizeObserver = function(callback) {
                var observer = new OrigResizeObserver(function() {
                    try { callback.apply(this, arguments); } catch(e) {}
                });
                observer.disconnect = OrigResizeObserver.prototype.disconnect;
                observer.observe = OrigResizeObserver.prototype.observe;
                observer.unobserve = OrigResizeObserver.prototype.unobserve;
                return observer;
            };
            window.ResizeObserver.prototype = OrigResizeObserver.prototype;
            Object.defineProperty(window.ResizeObserver, 'prototype', { value: OrigResizeObserver.prototype });
        }
    } catch(e) {}

    // === INTERSECTION OBSERVER PATCHING ===
    try {
        var OrigIntersectionObserver = window.IntersectionObserver;
        if (OrigIntersectionObserver) {
            window.IntersectionObserver = function(callback, options) {
                var wrappedCallback = function(entries) {
                    for (var i = 0; i < entries.length; i++) {
                        entries[i].isIntersecting = true;
                        entries[i].intersectionRatio = Math.random() * 0.3 + 0.7;
                    }
                    callback(entries);
                };
                return new OrigIntersectionObserver(wrappedCallback, options);
            };
            window.IntersectionObserver.prototype = OrigIntersectionObserver.prototype;
        }
    } catch(e) {}

    // === SMOOTH SCROLL SIMULATION ===
    try {
        var origScrollTo = window.scrollTo;
        window.scrollTo = function(options) {
            if (options && options.behavior === 'smooth') {
                return origScrollTo.call(window, {
                    top: options.top || 0,
                    left: options.left || 0,
                    behavior: 'auto'
                });
            }
            return origScrollTo.apply(this, arguments);
        };
    } catch(e) {}

    // === FULLSCREEN DETECTION EVASION ===
    try {
        Object.defineProperty(document, 'fullscreenElement', {
            get: function() { return undefined; },
            configurable: true
        });
    } catch(e) {}

})();
"""

class AntiDetectionPatches:
    """CDP-level anti-detection patches applied via Chrome DevTools Protocol"""

    @staticmethod
    def get_overrides(driver):
        """Apply CDP-level overrides to mask automation signals"""
        try:
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                'userAgent': StealthEngine.random_ua(),
                'acceptLanguage': StealthEngine.random_lang(),
                'platform': 'Win32',
            })
        except Exception:
            pass

        try:
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'mobile': False,
                'width': 1920,
                'height': 1080,
                'deviceScaleFactor': random.choice([1, 1.25, 1.5]),
            })
        except Exception:
            pass

        try:
            driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                'timezoneId': random.choice([
                    'America/New_York', 'America/Chicago', 'America/Los_Angeles',
                    'Europe/London', 'Europe/Paris', 'Europe/Berlin',
                    'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Seoul',
                    'Australia/Sydney', 'America/Toronto',
                ])
            })
        except Exception:
            pass

        try:
            driver.execute_cdp_cmd('Emulation.overrideGeolocation', {
                'latitude': random.uniform(30, 50),
                'longitude': random.uniform(-130, -70),
                'accuracy': random.uniform(10, 100),
            })
        except Exception:
            pass

        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': STEALTH_JS_AT_RUNTIME
            })
        except Exception:
            pass

        try:
            driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': StealthEngine.random_lang(),
                    'Sec-Ch-Ua': StealthEngine._build_sec_ch_ua(),
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'DNT': '1',
                    'Upgrade-Insecure-Requests': '1',
                }
            })
        except Exception:
            pass

    @staticmethod
    def _build_sec_ch_ua():
        """Build a realistic Sec-Ch-Ua header"""
        versions = [
            '"Chromium"; v="130", "Not?A_Brand"; v="8"',
            '"Chromium"; v="129", "Not?A_Brand"; v="8"',
            '"Chromium"; v="128", "Not?A_Brand"; v="8"',
            '"Chromium"; v="127", "Not?A_Brand"; v="8"',
            '"Chromium"; v="126", "Not?A_Brand"; v="8"',
        ]
        return random.choice(versions)

def random_delay(min_sec, max_sec):
    """Public helper for randomized delays between actions"""
    time.sleep(random.uniform(min_sec, max_sec))

def human_like_scroll(driver, page_height=None):
    """Simulate human-like scroll behavior with variable speed and pauses"""
    if driver is None:
        return
    try:
        if page_height is None:
            page_height = driver.execute_script("return document.body.scrollHeight")

        viewport_height = driver.execute_script("return window.innerHeight")
        current_pos = 0
        scroll_speed = random.uniform(80, 200)

        while current_pos < page_height - viewport_height:
            chunk = random.randint(100, 400)
            current_pos = min(current_pos + chunk, page_height - viewport_height)
            driver.execute_script(f"window.scrollTo(0, {current_pos})")
            time.sleep(random.uniform(0.02, 0.08))

        time.sleep(random.uniform(0.5, 1.5))
        driver.execute_script("window.scrollTo(0, 0)")
    except Exception:
        pass

class RecipeCrawler:
    def __init__(self, full_run=False):
        self.driver = None
        self.visited_urls = set()
        self.collected_recipes = {}
        self.full_run = full_run
        self.running = True
        self.progress = {"last_url": None, "total_collected": 0, "last_update": None}
        self.input_queue = queue.Queue()
        self.input_thread = None
        self.crawl_queue = []
        self.skipped_urls = set()
        self.ignore_patterns = []
        # Seconds
        self.page_load_timeout = 20
        self.max_retries = 2
        # Load saved state
        self.load_ignorelist()
        self.load_progress()
        self.load_collected()
        self.load_skiplist()
        self.init_database()
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\nShutdown signal received. Saving progress...")
        self.save_progress()
        self.running = False
        sys.exit(0)

    def _input_thread_func(self):
        """Thread function to read user input"""
        try:
            while self.running:
                try:
                    user_input = sys.stdin.readline()
                    if not user_input:
                        break
                    user_input = user_input.strip().lower()
                    self.input_queue.put(user_input)
                except (OSError, EOFError):
                    break
        except Exception:
            pass

    def check_user_input(self):
        """Check if user has requested shutdown or added URLs to queue (non-blocking)"""
        should_shutdown = False
        try:
            while True:
                user_input = self.input_queue.get_nowait()
                if user_input == "x":
                    should_shutdown = True
                elif user_input.startswith("get:"):
                    url = user_input[4:].strip()
                    if url:
                        parsed = urlparse(url)
                        if not parsed.scheme:
                            url = "https://" + url
                        if f"{domain}" in urlparse(url).netloc:
                            if (
                                url not in self.crawl_queue
                                and url not in self.visited_urls
                                and url not in self.skipped_urls
                                and not self.should_ignore(url)
                            ):
                                self.crawl_queue.insert(0, url)
                                print(f"\nQueue Size: {len(self.crawl_queue)}")
                                print(f"\nAdded to queue: {url}")
                            elif self.should_ignore(url):
                                print(f"\nIgnored (matches ignore pattern): {url}")
                        else:
                            print(f"\nOnly {domain} URLs are supported: {url}")
        except queue.Empty:
            pass
        return should_shutdown

    def setup_driver(self):
        """Initialize Selenium WebDriver with maximum anti-detection stealth"""
        options = webdriver.ChromeOptions()

        # === HEADLESS MODE ===
        options.add_argument("--headless=new")

        # === BASIC DISGUISE FLAGS ===
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        # === CRITICAL: Disable automation flags ===
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # === WINDOW SIZE (match common resolution) ===
        res_w, res_h = StealthEngine.random_resolution()
        dw = random.randint(320, 1600)
        dh = random.randint(600, 900)
        options.add_argument(f"--window-size={dw},{dh}")

        # === LANGUAGE AND LOCALE ===
        lang = StealthEngine.random_lang()
        options.add_argument(f"--lang={lang}")

        # === DISABLE NOTIFICATIONS & PERMISSIONS PROMPTS ===
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-translate")

        # === DISABLE EXTENSIONS & DISCOVERY ===
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")

        # === USER DATA DIR (simulate persistent profile) ===
        profile_dir = Path(os.getenv('TEMP', '/tmp')) / f"chrome_profile_{random.randint(10000, 99999)}"
        options.add_argument(f"--user-data-dir={profile_dir}")

        # === PREFETCH & NETWORK SETTINGS ===
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--force-color-profile=srgb")
        options.add_argument("--enable-features=NetworkServiceInProcess")

        # === PERFORMANCE FLAGS (avoid headless-specific flags) ===
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-component-update")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-offer-store-unmasked-wallets")
        options.add_argument("--disable-profiles-shortcut-manager")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-signin-scoped-device-id")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--mute-audio")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-first-run")
        options.add_argument("--password-store=basic")
        options.add_argument("--use-mock-keychain")

        # === USER AGENT (rotated per session) ===
        ua = StealthEngine.random_ua()
        options.add_argument(f"--user-agent={ua}")

        # === ADDITIONAL METADATA SPOOFING via experimental options ===
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.popups": 0,
            "profile.managed_default_content_settings.geolocation": 1,
            "profile.managed_default_content_settings.notifications": 1,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
            "intl.accept_languages": StealthEngine.random_lang().split(',')[0],
            "safebrowsing.enabled": True,
            "safebrowsing.malware_reporting.permissioned": False,
        })

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Warning: webdriver-manager failed ({e}), trying direct Chrome...")
            try:
                self.driver = webdriver.Chrome(options=options)
            except Exception as e2:
                print(f"Error initializing Chrome driver: {e2}")
                print("Please ensure Chrome browser is installed.")
                sys.exit(1)

        # ============================================
        # CDP-LEVEL ANTI-DETECTION PATCHES
        # ============================================
        try:
            AntiDetectionPatches.get_overrides(self.driver)
        except Exception:
            pass

        # === SECOND-STAGE JS PATCHES (execute after page context is ready) ===
        self._apply_stealth_patches()

        # === LEGACY WEBDRIVER PROPERTY HIDING (defense in depth) ===
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # Set page load timeout
        self.driver.set_page_load_timeout(self.page_load_timeout)

        # Set implicit wait (reduced to avoid suspicion)
        self.driver.implicitly_wait(3)

    def _apply_stealth_patches(self):
        """Apply stealth JS patches via CDP for every new document"""
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': STEALTH_JS_AT_RUNTIME
            })
        except Exception:
            self.driver.execute_script(STEALTH_JS_AT_RUNTIME)

    def _postload_stealth(self):
        """Apply post-load stealth patches after page is interactive"""
        try:
            self.driver.execute_script(STEALTH_JS_POSTLOAD)
        except Exception:
            pass

    def stripClean(self, text: str) -> str:
        if not text:
            return ""

        cleaned = re.sub(r'[^\x00-\x7F]+', '', text)

        cleaned = re.sub(
            r"\s*\(Video Recipe\)\s*|\s*VIDEO\s*", " ", cleaned, flags=re.IGNORECASE
        )
        cleaned = cleaned.replace(" ", "_")
        cleaned = re.sub(r"_+", "_", cleaned)
        cleaned = cleaned.replace("%", "--PCENT--")
        cleaned = cleaned.replace("&", "--AND--")
        cleaned = re.sub(r'[()“”’!\',"<>:/\\|?*\[\]]', "", cleaned)
        cleaned = cleaned.strip("_ \n")
        return cleaned

    def load_progress(self):
        if not self.full_run and RESUME_FILE.exists():
            try:
                with open(RESUME_FILE, "r") as f:
                    self.progress = json.load(f)
                print(f"Resuming from: {self.progress.get('last_url', 'start')}")
            except Exception as e:
                print(f"Error loading progress: {e}")

    def load_collected(self):
        if COLLECTED_FILE.exists():
            try:
                with open(COLLECTED_FILE, "r") as f:
                    self.collected_recipes = json.load(f)
                print(f"Loaded {self.clean_collected()} previously collected recipes")
            except Exception as e:
                print(f"Error loading collected recipes: {e}")
        else:
            with open(COLLECTED_FILE, "w") as f:
                json.dump({}, f, indent=2)

    def load_ignorelist(self):
        if IGNORE_FILE.exists():
            try:
                with open(IGNORE_FILE, "r") as f:
                    data = json.load(f)
                    self.ignore_patterns = data.get("ignore_links", [])
                if self.ignore_patterns:
                    print(f"Loaded {len(self.ignore_patterns)} ignore patterns")
            except Exception as e:
                print(f"Error loading ignore list: {e}")
                self.ignore_patterns = []
        else:
            self.ignore_patterns = []

    def load_skiplist(self):
        if SKIP_FILE.exists():
            try:
                with open(SKIP_FILE, "r") as f:
                    data = json.load(f)
                    self.skipped_urls = set(data.get("skipped_urls", []))
                if self.skipped_urls:
                    print(f"Loaded {len(self.skipped_urls)} URLs to skip")
            except Exception as e:
                print(f"Error loading skiplist: {e}")
                self.skipped_urls = set()

    def init_database(self):
        """Initialize SQLite database and import existing JSON files"""
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Create recipes table with name as primary key
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    name TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    added_at TEXT NOT NULL
                )
            """)

            # Create index on name for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name)
            """)

            conn.commit()
            print(f"This can take a long time depending on size of database rebuild.")
            print(f"Please, wait...")
            print(f"Database initialized: {DB_FILE}")

            # Import existing JSON files
            self.import_json_to_database(cursor, conn)

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    def import_json_to_database(self, cursor, conn):
        """Import JSON files from output directory into database"""
        json_files = list(DATA_DIR.glob("*.json"))
        imported_count = 0
        skipped_count = 0

        for json_file in json_files:

            print(f"Importing: {json_file}")

            # Skip files in subdirectories (resume, images, thumbs, db)
            if json_file.parent != DATA_DIR:
                continue

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    recipe_data = json.load(f)

                name = recipe_data.get("name")
                if not name:
                    skipped_count += 1
                    continue

                # Check if name already exists in database
                cursor.execute("SELECT name FROM recipes WHERE name = ?", (name,))
                if cursor.fetchone():
                    skipped_count += 1
                    continue

                # Insert new recipe
                cursor.execute(
                    "INSERT INTO recipes (name, data, added_at) VALUES (?, ?, ?)",
                    (name, json.dumps(recipe_data), datetime.now().isoformat()),
                )
                #print(f"Imported: {name}")
                imported_count += 1

            except Exception as e:
                print(f"Error importing {json_file.name}: {e}")

        conn.commit()
        print(
            f"Imported {imported_count} recipes to database ({skipped_count} already existed or skipped)"
        )

    def should_ignore(self, url):
        for pattern in self.ignore_patterns:
            if pattern in url:
                return True
        return False

    def add_to_skiplist(self, url, error_msg=""):
        self.skipped_urls.add(url)
        try:
            data = {"skipped_urls": sorted(list(self.skipped_urls))}
            with open(SKIP_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Added to skiplist: {url} (error: {error_msg})")
        except Exception as e:
            print(f"Error saving to skiplist: {e}")

    def save_progress(self):
        self.progress["last_update"] = datetime.now().isoformat()
        try:
            with open(RESUME_FILE, "w") as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def save_collected(self):
        try:
            with open(COLLECTED_FILE, "w") as f:
                json.dump(self.collected_recipes, f, indent=2)
        except Exception as e:
            print(f"Error saving collected recipes: {e}")

    def clean_collected(self):
        newlist = {}
        seen = set()
        with open(COLLECTED_FILE, "r") as f:
            data = json.load(f)
            for url, vals in data.items():
                if vals.get("file") and vals["file"] not in seen:
                    newlist[url] = vals
                seen.add(vals.get("file", ""))
        return len(newlist)

    def clean_filename(self, name):
        name = name.strip()
        cleaned = html.unescape(name)
        cleaned = self.stripClean(cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned[:200]

    def _clean_html_entities(self, text):
        if isinstance(text, str):
            return html.unescape(text)
        return text

    def _is_loader_image_url(self, url):
        """Check if an image URL appears to be a loader/placeholder image"""
        if not url:
            return True

        url_lower = url.lower()
        # Common patterns for loader/placeholder images
        loader_patterns = [
            "loader",
            "placeholder",
            "default",
            "blank",
            "transparent",
            "spinner",
            "loading",
            "pixel",
            "data:image",
            "no-image",
            "noimage",
            "missing"
        ]

        # Check for tiny size patterns (common in spacers)
        # Only flag as loader if URL is very short (actual pixel spacer, not a real image with "1x1" in path)
        if ("1x1" in url_lower or "2x2" in url_lower) and len(url) < 60:
            return True

        # Check for loader keywords
        if any(pattern in url_lower for pattern in loader_patterns):
            return True

        # Check if it's a data URI (inline placeholder)
        if url_lower.startswith("data:image"):
            return True

        # Very short URLs are suspect (often just a hash or ID)
        if len(url) < 30:
            return True

        return False

    def extract_image_from_dom(self):
        """Extract the actual recipe image URL from DOM lazy-loading attributes"""
        if self.driver is None:
            return None

        try:
            # Selectors (updated for current site structure)
            selectors = [
                "img[data-src]",
                "img[data-srcset]",
                "img[data-original]",
                "img[data-lazyload]",
                "img[data-image]",
                'img[data-sizes="auto"]',
                "img.rec-image",
                "img.rec-photo",
                "img.photo",
                "img.schema-org-image",
                'img[itemprop="image"]',
                "img.details__image",
                "img.lead-image",
                "img.primary-image",
                "img.kr-image",
                "img.unstyled-image",
                "img.multimedia-image",
                f'img[src*="{domain}"]',
                f'img[src*="images.{domain}"]',
                'img[src*="recipe-images"]',
                "div.rec-photo img",
                "figure.rec-photo img",
                ".image-container img",
                ".hero-image img",
                ".recipe-image img"
            ]
            candidate_urls = []

            for selector in selectors:
                try:
                    images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for img in images:
                        # Try different attributes in order of preference
                        for attr in [
                            "data-src",
                            "data-srcset",
                            "data-original",
                            "data-lazyload",
                            "data-image",
                            "data-sizes",
                            "src"
                        ]:
                            url = img.get_attribute(attr)
                            if url and isinstance(url, str) and url.strip():
                                url = url.strip()

                                # For srcset, extract first URL
                                if "srcset" in attr:
                                    parts = url.split(",")[0].strip().split(" ")[0]
                                    url = parts

                                # Make absolute URL
                                if url.startswith("//"):
                                    url = "https:" + url
                                elif url.startswith("/"):
                                    url = urljoin(BASE_URL, url)

                                # Only add if it looks like a valid image URL
                                if len(url) > 30 and any(
                                    ext in url.lower()
                                    for ext in [
                                        ".bmp",
                                        ".jpg",
                                        ".jpeg",
                                        ".png",
                                        ".webp",
                                        ".gif"
                                    ]
                                ):
                                    candidate_urls.append(url)
                except Exception:
                    continue

            # Fallback: scan all img tags for plausible images
            if not candidate_urls:
                try:
                    all_imgs = self.driver.find_elements(By.TAG_NAME, "img")
                    for img in all_imgs[:20]:
                        src = img.get_attribute("src")
                        if src and isinstance(src, str) and len(src) > 30:
                            src_lower = src.lower()
                            # Must be same domain and not be an icon/logo
                            if (
                                f"{domain}" in src_lower
                                or f"images.{domain}" in src_lower
                            ):
                                if not any(
                                    skip in src_lower
                                    for skip in [
                                        "icon",
                                        "logo",
                                        "button",
                                        "badge",
                                        "sprite",
                                        "svg",
                                        "pixel"
                                    ]
                                ):
                                    candidate_urls.append(src)
                except Exception:
                    pass

            # Return first non-loader URL
            for url in candidate_urls:
                if not self._is_loader_image_url(url):
                    print(f"  Found image URL from DOM: {url[:80]}...")
                    return url

            # If all candidates are loaders, nothing good found
            if candidate_urls:
                print(
                    f"  All {len(candidate_urls)} candidate images were loader/placeholder images"
                )

        except Exception as e:
            if DEBUGEN:
                print(f"  Debug: Error extracting image from DOM: {e}")
            else:
                pass

        return None

    def extract_jsonld_data(self):
        """Extract recipe data from JSON-LD script tags with multiple fallbacks"""
        recipes = []
        if self.driver is None:
            return recipes

        try:
            # First try: standard JSON-LD
            scripts = self.driver.find_elements(
                By.XPATH, '//script[@type="application/ld+json"]'
            )

            # If no JSON-LD found, also check for other script tags that might contain recipe data
            if not scripts:
                scripts = self.driver.find_elements(By.XPATH, '//script[contains(text(), "recipeIngredient")]')
        except Exception as e:
            if DEBUGEN:
                print(f"  Debug: Error finding script tags: {e}")
            else:
                pass
            return recipes

        for idx, script in enumerate(scripts):
            try:
                json_text = script.get_attribute("innerHTML")
                if not json_text or not isinstance(json_text, str):
                    continue

                # Clean up the JSON text
                json_text = json_text.strip()
                json_text = re.sub(r"<!--.*?-->", "", json_text, flags=re.DOTALL)
                json_text = re.sub(
                    r"<!\[CDATA\[(.*?)\]\]>", r"\1", json_text, flags=re.DOTALL
                )

                try:
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    if DEBUGEN:
                        print(f"  Debug: JSON parse error in script {idx}: {e}")
                    continue

                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = [data]
                else:
                    continue

                for item in items:
                    if isinstance(item, dict):
                        item_type = item.get("@type", "")
                        if isinstance(item_type, list):
                            is_recipe = "Recipe" in item_type or "recipe" in item_type
                        else:
                            is_recipe = item_type in ["Recipe", "recipe", "HowTo"]

                        if not is_recipe and "recipeIngredient" in item:
                            is_recipe = True

                        if is_recipe:
                            recipes.append(item)
            except Exception as e:
                if DEBUGEN:
                    print(f"  Debug: Error processing script {idx}: {e}")
                continue

        return recipes

    def download_image(self, image_url, filename):
        """Download and save recipe image (only if 250x250 or larger)"""
        try:
            if not image_url or not isinstance(image_url, str):
                return None

            if image_url.startswith("//"):
                image_url = "https:" + image_url
            elif image_url.startswith("/"):
                image_url = urljoin(BASE_URL, image_url)

            session = requests.Session()
            retry_strategy = Retry(
                total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            # Use rotated user-agent for image downloads too
            image_ua = StealthEngine.random_ua()
            headers = {
                "User-Agent": image_ua,
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": StealthEngine.random_lang(),
                "Referer": BASE_URL,
            }
            response = session.get(image_url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()

            try:
                from PIL import Image as PILImage
            except ImportError:
                PILImage = None

            if PILImage:
                from io import BytesIO

                img_data = BytesIO()
                for chunk in response.iter_content(chunk_size=8192):
                    img_data.write(chunk)
                img_data.seek(0)

                img = PILImage.open(img_data)
                width, height = img.size

                if width < 250 or height < 250:
                    print(f"Skipping image - too small: {width}x{height}")
                    return None

                # Convert to webp and resize to 785x301 for main image
                img = img.convert("RGB")
                # Use LANCZOS resampling (best quality for downscaling)
                resample = (
                    PILImage.Resampling.LANCZOS
                    if hasattr(PILImage, "Resampling")
                    else 1
                )
                img_resized = img.resize((785, 301), resample)
                # Generate webp filename
                safe_name = os.path.splitext(filename)[0]
                safe_name = self.stripClean(safe_name)
                webp_filename = f"{safe_name}.webp"
                image_path = IMAGES_DIR / webp_filename

                # Save resized webp image
                img_resized.save(image_path, format="WEBP", quality=85)
                print(f"Saved webp image to: {image_path}")
                thumb = img.resize((267, 200), resample)

                thumb_filename = f"{safe_name}.webp"
                thumb_path = THUMBS_DIR / thumb_filename
                thumb.save(thumb_path, format="WEBP", quality=85)
                print(f"Saved thumbnail to: {thumb_path}")

                return str(image_path)
            else:
                print("Warning: PIL not installed, skipping conversion")
                image_path = IMAGES_DIR / filename
                with open(image_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return str(image_path)

        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return None

    def extract_recipe_info(self, recipe_data, page_url):
        """Extract structured recipe information from JSON-LD data"""
        name = recipe_data.get("name")
        if name is None:
            name = ""

        category = recipe_data.get("recipeCategory") or recipe_data.get("recipeCuisine")
        if category is None:
            category = []
        elif isinstance(category, str):
            category = [category]

        name = self._clean_html_entities(name)
        name = self.stripClean(name)

        recipe = {
            "name": name,
            "origin": [],
            "category": category,
            "ingredients": [],
            "instructions": [],
            "href": f"{domhref}",
            "site": f"{domain}",
            "url": page_url,
            "image": True,
            "v": f"{verstr}",
            "extracted_at": datetime.now().isoformat()
        }

        # Extract image URL - try JSON-LD first, then fall back to DOM extraction
        image_url_from_json = None
        image_data = recipe_data.get("image")
        if image_data is None:
            image_data = ""
        if isinstance(image_data, list) and len(image_data) > 0:
            image_data = image_data[0]

        if isinstance(image_data, dict):
            image_url_from_json = image_data.get("url", "")
        else:
            image_url_from_json = str(image_data) if image_data else ""

        # Clean up the URL
        if image_url_from_json:
            image_url_from_json = image_url_from_json.strip()
            if image_url_from_json.startswith("//"):
                image_url_from_json = "https:" + image_url_from_json
            elif image_url_from_json.startswith("/"):
                image_url_from_json = urljoin(BASE_URL, image_url_from_json)

        global _tempimage
        _tempimage = image_url_from_json

        # If JSON-LD image looks like a loader/placeholder, try DOM extraction
        if not image_url_from_json or self._is_loader_image_url(image_url_from_json):
            dom_image_url = self.extract_image_from_dom()
            if dom_image_url:
                _tempimage = dom_image_url
                # recipe["image_url"] = dom_image_url
                print(
                    f"  Using image URL from DOM (JSON-LD image was loader/missing): {dom_image_url[:80]}..."
                )

        ingredients = recipe_data.get("recipeIngredient")
        if ingredients is None:
            ingredients = []
        if isinstance(ingredients, list):
            for ingredient in ingredients:
                if ingredient:
                    recipe["ingredients"].append(self._clean_html_entities(ingredient))

        instructions = recipe_data.get("recipeInstructions")
        if instructions is None:
            instructions = []
        if isinstance(instructions, list):
            for inst in instructions:
                if isinstance(inst, dict):
                    text = inst.get("text", "")
                    if text:
                        recipe["instructions"].append(self._clean_html_entities(text))
                elif isinstance(inst, str):
                    recipe["instructions"].append(self._clean_html_entities(inst))

        return recipe

    def add_recipe_to_database(self, recipe_data):
        """Add a single recipe to the SQLite database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            name = recipe_data.get("name")
            if not name:
                return False

            # Check if recipe already exists
            cursor.execute("SELECT name FROM recipes WHERE name = ?", (name,))
            if cursor.fetchone():
                print(f"  Recipe already in database: {name}")
                conn.close()
                return False

            # Insert recipe
            cursor.execute(
                "INSERT INTO recipes (name, data, added_at) VALUES (?, ?, ?)",
                (name, json.dumps(recipe_data), datetime.now().isoformat()),
            )
            conn.commit()
            conn.close()
            print(f"  Added to database: {name}")
            return True

        except sqlite3.Error as e:
            print(f"  Database error adding recipe: {e}")
            return False

    def recipe_exists_in_database(self, name):
        """Check if a recipe already exists in the database by name"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM recipes WHERE name = ?", (name,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except sqlite3.Error:
            return False

    def save_recipe(self, recipe_data, page_url):
        """Save recipe to JSON file"""
        recipe_name = recipe_data.get("name")
        recipe_name = self._clean_html_entities(recipe_name)
        recipe_name = self.stripClean(recipe_name)

        if not recipe_name:
            print("Warning: Recipe has no name, skipping")
            return False

        display_name = self._clean_html_entities(recipe_name)

        # Check if recipe already exists in database by name
        if self.recipe_exists_in_database(recipe_name):
            print(f"Skipping already collected: {recipe_name}")
            return False

        if page_url in self.collected_recipes:
            print(f"Skipping already collected URL: {page_url}")
            return False

        safe_name = self.clean_filename(recipe_name)
        safe_name = self.stripClean(safe_name)

        if not safe_name:
            safe_name = f"recipe_{int(time.time())}"

        json_filename = f"{safe_name}.json"
        json_path = DATA_DIR / json_filename
        recipe_info = self.extract_recipe_info(recipe_data, page_url)

        global _tempimage

        if _tempimage:
            image_filename = f"{safe_name}.webp"
            recipe_info["origin"] = recipe_data.get("recipeCuisine")
            print(f"Downloading image: {_tempimage}")
            saved_path = self.download_image(_tempimage, image_filename)

            if saved_path:
                print(f"Saved image to: {saved_path}")

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(recipe_info, f, indent=2, ensure_ascii=False)

            self.collected_recipes[page_url] = {
                "name": display_name,
                "file": json_filename,
                "collected_at": datetime.now().isoformat(),
            }
            self.save_collected()
            print(f"Saved recipe: {display_name} -> {json_filename}")
            print(f"Total Recipes: {self.clean_collected()}")

            # Add to database immediately after saving
            self.add_recipe_to_database(recipe_info)

        except Exception as e:
            print(f"Error saving recipe {display_name}: {e}")
            return False

        return True

    def is_valid_url(self, url):
        if not url or not isinstance(url, str):
            return False
        parsed = urlparse(url)
        if not parsed.netloc:
            return False
        return f"{domain}" in parsed.netloc

    def find_links(self):
        """Find all internal links on current page"""
        links = []
        if self.driver is None:
            return links

        try:
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            if DEBUGEN:
                print(f"  Debug: Found {len(all_links)} total links on page")
            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    if href and isinstance(href, str):
                        href = href.strip()
                        if self.is_valid_url(href):
                            links.append(href)
                except Exception:
                    continue
        except Exception as e:
            print(f"  Debug: Error finding links: {e}")

        unique_links = list(set(links))
        if DEBUGEN:
            print(f"  Debug: Found {len(unique_links)} unique valid {domain} links")
        return unique_links

    def wait_for_page_load(self, url):
        """Wait for page to be fully loaded with multiple strategies"""
        if self.driver is None:
            return False

        try:
            # Use explicit wait for document ready state
            WebDriverWait(self.driver, self.page_load_timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Also wait for body to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Give extra time for JavaScript to render
            time.sleep(2)
            return True

        except TimeoutException:
            print(f"  Warning: Page load timeout for {url}")
            return False
        except Exception as e:
            print(f"  Warning: Error waiting for page load: {e}")
            return False

    def updateCrawl(self):
        print("=" * 60)
        print(f"{appname} v{verstr}")
        print("=" * 60)
        if self.full_run:
            print("Mode: Full Run")
        else:
            print("Mode: Resume Run")
        print(f"Starting URL: {BASE_URL}")
        print("Press 'x' + Enter to stop crawling")
        print("Or type 'get:<url>' to add a specific URL to the queue")
        print(f"Currently collected: {self.clean_collected()} recipes")
        print("=" * 60)
        return

    def crawl_page(self, url):
        """Crawl a single page with robust error handling and stealth behavior"""
        if not self.running:
            return []

        if url in self.visited_urls:
            return []

        if url in self.skipped_urls:
            print(f"Skipping URL (in skiplist): {url}")
            return []

        if self.driver is None:
            print("Error: WebDriver not initialized")
            return []

        print(f"\nCrawling: {url}")
        self.visited_urls.add(url)

        # Random delay before navigating (human-like hesitation)
        StealthEngine.human_delay(0.8, 2.5)

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    print(f"  Retry attempt {attempt}/{self.max_retries}")
                    StealthEngine.jittered_sleep(3, 1.5)

                # Navigate to URL with timeout handling
                try:
                    self.driver.get(url)
                except Exception as e:
                    if attempt < self.max_retries:
                        print(f"  Page load failed: {e}, retrying...")
                        StealthEngine.jittered_sleep(4, 2.0)
                        continue
                    else:
                        print(
                            f"  Page load failed after {self.max_retries} retries: {e}"
                        )
                        self.add_to_skiplist(url, str(e))
                        return []

                # Wait for page to load properly
                if not self.wait_for_page_load(url):
                    if attempt < self.max_retries:
                        continue

                # Apply post-load stealth patches
                self._postload_stealth()

                # Simulate human scrolling behavior before extracting data
                human_like_scroll(self.driver)

                # Random pause (simulating reading time)
                StealthEngine.random_scroll_pause()

                # Debug: Print page title
                try:
                    title = self.driver.title
                    if DEBUGEN:
                        print(f"  Page title: {title}")
                except:
                    pass

                # Extract recipe data from JSON-LD
                recipe_data_list = self.extract_jsonld_data()
                if DEBUGEN:
                    print(f"  Debug: Found {len(recipe_data_list)} recipe objects")

                new_recipes_found = 0
                for recipe_data in recipe_data_list:
                    if self.save_recipe(recipe_data, url):
                        new_recipes_found += 1

                if new_recipes_found > 0:
                    print(f"Found {new_recipes_found} recipe(s) on this page")
                else:
                    print(f"  No recipes found on this page")

                # Save progress
                self.progress["last_url"] = url
                self.progress["total_collected"] = len(self.collected_recipes)
                self.save_progress()

                # Return all links found on page for further crawling
                return self.find_links()

            except WebDriverException as e:
                error_msg = str(e)
                print(f"WebDriver error: {error_msg}")
                if (
                    "ERR_NAME_NOT_RESOLVED" in error_msg
                    or "ERR_CONNECTION" in error_msg
                ):
                    self.add_to_skiplist(url, error_msg)
                    return []
                if attempt >= self.max_retries:
                    return []
                StealthEngine.jittered_sleep(4, 2.0)
            except Exception as e:
                print(f"Unexpected error crawling {url}: {e}")
                if attempt >= self.max_retries:
                    return []
                StealthEngine.jittered_sleep(4, 2.0)

        return []

    def start_crawl(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 60)
        print(f"{appname} v{verstr}")
        print("=" * 60)
        if self.full_run:
            print("Mode: Full Run")
        else:
            print("Mode: Resume Run")
        print(f"Starting URL: {BASE_URL}")
        print("Press 'x' + Enter to stop crawling")
        print("Or type 'get:<url>' to add a specific URL to the queue")
        print(f"Currently collected: {self.clean_collected()} recipes")
        print("=" * 60)

        self.input_thread = threading.Thread(
            target=self._input_thread_func, daemon=True
        )
        self.input_thread.start()

        try:
            self.setup_driver()
        except Exception as e:
            print(f"Failed to initialize driver: {e}")
            return

        if self.full_run:
            self.crawl_queue = [BASE_URL]
        else:
            resume_url = self.progress.get("last_url")
            self.crawl_queue = [resume_url] if resume_url else [BASE_URL]

        self.crawl_queue = [
            url
            for url in self.crawl_queue
            if url not in self.skipped_urls and not self.should_ignore(url)
        ]

        if not self.crawl_queue:
            print("Warning: Resume URL was skipped/ignored. Starting from BASE_URL.")
            self.crawl_queue = [BASE_URL]

        visited_this_session = set()
        pages_crawled = 0

        try:
            while self.crawl_queue and self.running:
                current_url = self.crawl_queue.pop(0)

                if self.check_user_input():
                    print("User requested shutdown. Saving progress...")
                    self.save_progress()
                    break

                if (
                    current_url in visited_this_session
                    or current_url in self.visited_urls
                ):
                    continue

                visited_this_session.add(current_url)
                pages_crawled += 1
                self.updateCrawl()
                print(f"\n--- Page {pages_crawled} ---")
                new_links = self.crawl_page(current_url)

                for link in new_links:
                    if (
                        link not in visited_this_session
                        and link not in self.visited_urls
                        and link not in self.crawl_queue
                        and link not in self.skipped_urls
                        and not self.should_ignore(link)
                    ):
                        self.crawl_queue.append(link)

                print(f"Queue size: {len(self.crawl_queue)} | Visited: {len(self.visited_urls)} | Collected: {self.clean_collected()}")
                # Randomize inter-page delay to avoid timing pattern detection
                StealthEngine.jittered_sleep(2.0, 1.5)

        except KeyboardInterrupt:
                print("\nShutdown requested. Saving progress...")
        finally:
            self.save_progress()
            self.shutdown()

        print(f"\nCrawl complete. Visited {len(self.visited_urls)} pages, collected {self.clean_collected()} recipes total.")

    def shutdown(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.save_progress()
        print("Crawler stopped.")

def main():
    parser = argparse.ArgumentParser(description="Crawl for recipes")
    parser.add_argument("--fullrun", action="store_true", help="Start from beginning instead of resuming")
    args = parser.parse_args()
    checkResume = Path("output/resume/resume.json")

    if not args.fullrun and not checkResume.is_file():
        args.fullrun = True

    crawler = RecipeCrawler(full_run=args.fullrun)

    try:
        crawler.start_crawl()
    except Exception as e:
        print(f"Crawler error: {e}")
        import traceback
        traceback.print_exc()
        crawler.shutdown()

if __name__ == "__main__":
    main()
