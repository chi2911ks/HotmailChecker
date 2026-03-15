import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class AppConfig:
    APP_NAME = "Hotmail Checker - By: CB Tool"
    APP_VERSION = "1.0.0"
    ORG_NAME = "CB Tool"

    # Paths
    RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
    DARK_THEME_PATH = os.path.join(RESOURCES_DIR, "styles", "dark_theme.qss")
    LIGHT_THEME_PATH = os.path.join(RESOURCES_DIR, "styles", "light_theme.qss")
    DEFAULT_THEME_PATH = LIGHT_THEME_PATH
    APP_ICON_PATH = os.path.join(RESOURCES_DIR, "icons", "app_icon.ico")

    # Microsoft API
    MS_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    # UI
    WINDOW_MIN_WIDTH = 900
    WINDOW_MIN_HEIGHT = 600
