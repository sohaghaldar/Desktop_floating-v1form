# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Core Modules
"""

from core.config import (
    APP_VERSION,
    IS_WINDOWS,
    IS_MACOS,
    IS_LINUX,
    ROOT_DIR,
    SETTINGS_FILE,
    LOCALES_DIR,
    THEMES,
    SPIDER_MODELS,
    DEFAULT_SETTINGS,
    load_config,
    save_config_value,
    save_full_settings,
    parse_hotkey_combo,
    get_vk_code,
)

from core.platform_helper import (
    PlatformHelper,
    is_hotkey_down,
    enforce_single_instance,
    play_audio,
)

from core.i18n import (
    I18n,
    I18nManager,
)

from core.updater import (
    GitHubAutoUpdater,
)

from core.ui_widgets import (
    ModernSlider,
)
