from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from qt_material import apply_stylesheet
from pathlib import Path
import multiprocessing
import threading
import requests
import pymem
import pymem.process
import win32api
import win32con
import win32gui
from pynput.mouse import Controller, Button
import json
import os
import sys
import time
import PySide6.QtGui
from PySide6.QtCore import Qt
import ctypes
import math
import struct
import vischeck

CONFIG_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'temp', 'Mortal cheat')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
DEFAULT_SETTINGS = {
    "esp_rendering": 1,
    "esp_mode": 1,
    "line_rendering": 1,
    "hp_bar_rendering": 1,
    "head_hitbox_rendering": 1,
    "bons": 1,
    "nickname": 1,
    "radius": 50,
    "keyboard": 0x43,
    "aim_active": 0,
    "aim_mode": 1,
    "aim_mode_distance": 1,
    "trigger_bot_active": 0,
    "keyboards": 0x58,
    "weapon": 1,
    "bomb_esp": 1,
    "trigger_mode": 0,
    "aim_legit": 0,
    "bomb_timer": 1,
    "defuse_timer": 1,
    "minimap": 1,
    "fov": 90,
    "no_flash": 0,
    "sniper_crosshair": 1,
    "enemy_visible_color": [255, 0, 0],
    "enemy_hidden_color": [255, 100, 100],
    "friendly_visible_color": [0, 0, 255],
    "friendly_hidden_color": [100, 100, 255]
}
BombPlantedTime = 0
BombDefusedTime = 0

VK_CODE_TO_NAME = {
    0x01: 'MOUSE1', 0x02: 'MOUSE2', 0x04: 'MOUSE3', 0x05: 'MOUSE4', 0x06: 'MOUSE5', 0x07: 'MOUSE6',
    0x08: 'Backspace', 0x09: 'Tab', 0x0D: 'Enter', 0x10: 'Shift', 0x11: 'Ctrl', 0x12: 'Alt',
    0x20: 'Space', 0x1B: 'Esc', 
    0x30: '0', 0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4', 0x35: '5', 0x36: '6', 0x37: '7', 0x38: '8', 0x39: '9',
    0x41: 'A', 0x42: 'B', 0x43: 'C', 0x44: 'D', 0x45: 'E', 0x46: 'F', 0x47: 'G', 0x48: 'H', 0x49: 'I',
    0x4A: 'J', 0x4B: 'K', 0x4C: 'L', 0x4D: 'M', 0x4E: 'N', 0x4F: 'O', 0x50: 'P', 0x51: 'Q', 0x52: 'R',
    0x53: 'S', 0x54: 'T', 0x55: 'U', 0x56: 'V', 0x57: 'W', 0x58: 'X', 0x59: 'Y', 0x5A: 'Z',
    0x13: 'Pause', 0x14: 'CapsLock', 0x1B: 'Esc', 0x20: 'Space', 0x21: 'PageUp', 0x22: 'PageDown',
    0x23: 'End', 0x24: 'Home', 0x25: 'Left', 0x26: 'Up', 0x27: 'Right', 0x28: 'Down',
    0x2C: 'PrintScreen', 0x2D: 'Insert', 0x2E: 'Delete',
    0x30: '0', 0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4', 0x35: '5', 0x36: '6', 0x37: '7', 0x38: '8', 0x39: '9',
    0x41: 'A', 0x42: 'B', 0x43: 'C', 0x44: 'D', 0x45: 'E', 0x46: 'F', 0x47: 'G', 0x48: 'H', 0x49: 'I', 0x4A: 'J', 0x4B: 'K', 0x4C: 'L', 0x4D: 'M', 0x4E: 'N', 0x4F: 'O', 0x50: 'P', 0x51: 'Q', 0x52: 'R', 0x53: 'S', 0x54: 'T', 0x55: 'U', 0x56: 'V', 0x57: 'W', 0x58: 'X', 0x59: 'Y', 0x5A: 'Z',
    0x5B: 'LWin', 0x5C: 'RWin', 0x5D: 'Apps',
    0x60: 'Num0', 0x61: 'Num1', 0x62: 'Num2', 0x63: 'Num3', 0x64: 'Num4', 0x65: 'Num5', 0x66: 'Num6', 0x67: 'Num7', 0x68: 'Num8', 0x69: 'Num9',
    0x6A: 'Num*', 0x6B: 'Num+', 0x6C: 'NumEnter', 0x6D: 'Num-', 0x6E: 'Num.', 0x6F: 'Num/',
    0x70: 'F1', 0x71: 'F2', 0x72: 'F3', 0x73: 'F4', 0x74: 'F5', 0x75: 'F6', 0x76: 'F7', 0x77: 'F8', 0x78: 'F9', 0x79: 'F10', 0x7A: 'F11', 0x7B: 'F12',
    0x90: 'NumLock', 0x91: 'ScrollLock',
    0xA0: 'LShift', 0xA1: 'RShift', 0xA2: 'LCtrl', 0xA3: 'RCtrl', 0xA4: 'LAlt', 0xA5: 'RAlt',
}

def load_settings():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE) or os.path.getsize(CONFIG_FILE) == 0:
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

def get_offsets_and_client_dll():
    offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
    client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
    engine2_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/engine2_dll.json').json()
    return offsets, client_dll

def get_window_size(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        rect = win32gui.GetClientRect(hwnd)
        return rect[2], rect[3]
    return None, None

def w2s(mtx, posx, posy, posz, width, height):
    screenW = (mtx[12] * posx) + (mtx[13] * posy) + (mtx[14] * posz) + mtx[15]
    if screenW > 0.001:
        screenX = (mtx[0] * posx) + (mtx[1] * posy) + (mtx[2] * posz) + mtx[3]
        screenY = (mtx[4] * posx) + (mtx[5] * posy) + (mtx[6] * posz) + mtx[7]
        camX = width / 2
        camY = height / 2
        x = camX + (camX * screenX / screenW)
        y = camY - (camY * screenY / screenW)
        return [int(x), int(y)]
    return [-999, -999]

class VisibilitySystem:
    def __init__(self, pm, client_dll):
        self.pm = pm
        self.client_dll = client_dll
        self.checker = None
        self.initialized = False
        self.map_load_failed = False  # Флаг, что загрузка карты не удалась
        
        self.offsets = self._load_offsets()
        print(f"Загружены оффсеты: {self.offsets}")
        
        self.maps_path = Path(__file__).parent / "vischeck_maps"
        self.maps_path.mkdir(exist_ok=True)
        
        # Список карт, для которых не удалась загрузка
        self.failed_maps = set()
    
    def _load_offsets(self):
        try:
            offsets = {
                'm_pGameSceneNode': self.client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode'],
                'm_modelState': self.client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
            }
            print(f"Успешно загружены оффсеты: {offsets}")
            return offsets
            
        except Exception as e:
            print(f"Ошибка при загрузке оффсетов: {e}")
            return {
                'm_pGameSceneNode': 80,
                'm_modelState': 36
            }
    
    def _get_current_map(self):
        try:
            module = pymem.process.module_from_name(self.pm.process_handle, "server.dll")
            base_address = module.lpBaseOfDll

            offset = 0x14F5CB0
            target_address = base_address + offset

            map_name = self.pm.read_string(target_address, 100)

            print(f"Map name: {map_name}")
            return map_name
            
        except Exception as e:
            print(f"Ошибка при получении карты: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _initialize_checker(self):
        try:
            current_map = self._get_current_map()
            if not current_map:
                print("❌ Не удалось определить текущую карту")
                return False
                
            print(f"\n======================================")
            print(f"Инициализация проверки видимости для карты: {current_map}")
            print("======================================")
            
            map_file = self.maps_path / f"{current_map}.opt"
            if not map_file.exists():
                print(f"⚠️ Файл карты не найден: {map_file}")
                print(f"⚠️ Проверка видимости будет отключена для карты: {current_map}")
                self.map_load_failed = True
                return False
                
            try:
                import vischeck
                print(f"Загружаем данные карты: {map_file.name}")
                self.checker = vischeck.VisCheck(str(map_file))
                self.initialized = True
                
                print(f"✅ Успешно инициализирована проверка видимости для карты: {current_map}")
                print("======================================\n")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка при загрузке данных карты: {e}")
                self.map_load_failed = True
                return False
            
        except Exception as e:
            print(f"❌ Критическая ошибка при инициализации проверки видимости: {e}")
            import traceback
            traceback.print_exc()
            self.map_load_failed = True
            return False

    def is_visible(self, local_player_addr, entity_addr, client_dll):
        try:
            # Если уже пробовали загрузить карту и не удалось, возвращаем True
            if self.map_load_failed:
                return True
                
            # Если проверка видимости не инициализирована, пробуем инициализировать
            if not self.initialized:
                current_map = self._get_current_map()
                # Если уже пробовали загрузить эту карту и не удалось, возвращаем True
                if current_map in self.failed_maps:
                    return True
                    
                if not self._initialize_checker():
                    self.failed_maps.add(current_map)
                    print(f"⚠️ Не удалось загрузить данные карты {current_map}. Проверка видимости отключена для этой карты.")
                    return True
            try:
                game_scene = self.pm.read_longlong(entity_addr + self.offsets['m_pGameSceneNode'])
                if not game_scene:
                    return False
                    
                bone_matrix = self.pm.read_longlong(game_scene + self.offsets['m_modelState'] + 0x80)
                if not bone_matrix:
                    return False
                    
                data = self.pm.read_bytes(bone_matrix + 6 * 0x20, 3 * 4)
                
                local_game_scene = self.pm.read_longlong(local_player_addr + self.offsets['m_pGameSceneNode'])
                if not local_game_scene:
                    return False
                    
                local_bone_matrix = self.pm.read_longlong(local_game_scene + self.offsets['m_modelState'] + 0x80)
                if not local_bone_matrix:
                    return False
                    
                local_data = self.pm.read_bytes(local_bone_matrix + 6 * 0x20, 3 * 4)
                
                me = struct.unpack('fff', local_data)
                enemy = struct.unpack('fff', data)
                
                return self.checker.is_visible(me, enemy)
                
            except Exception as e:
                print(f"Ошибка при проверке видимости: {e}")
                return False
            
        except Exception as e:
            print(f"Ошибка в is_visible: {e}")
            return False

visibility_system = None

def is_visible(pm, local_player_addr, entity_addr, client_dll):     
    global visibility_system
    if visibility_system is None:
        visibility_system = VisibilitySystem(pm, client_dll)
    return visibility_system.is_visible(local_player_addr, entity_addr, client_dll)

class ConfigWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        save_settings(DEFAULT_SETTINGS.copy())
        self.settings = load_settings()
        
        # Initialize default values for new settings if they don't exist
        if "bunny_hop_key" not in self.settings:
            self.settings["bunny_hop_key"] = 0x06  # Default to right mouse button
        if "visibility_colors" not in self.settings:
            self.settings["visibility_colors"] = 1  # Default enabled
            
        self._pm = None
        self._offsets = None
        self._client_dll = None
        self._client = None
        self._last_fov_update = 0
        self._fov_update_interval = 0.05
        self._bunny_hop_enabled = False
        self._bunny_hop_thread = None
        self._bunny_hop_running = False
        
        # Key mapping for display
        self.qt_to_vk = {
            QtCore.Qt.Key_Space: 0x20,
            QtCore.Qt.Key_Control: 0x11,
            QtCore.Qt.Key_Shift: 0x10,
            QtCore.Qt.Key_Alt: 0x12,
            QtCore.Qt.Key_CapsLock: 0x14,
            QtCore.Qt.Key_Tab: 0x09,
            QtCore.Qt.Key_Backspace: 0x08,
            QtCore.Qt.Key_Return: 0x0D,
            QtCore.Qt.Key_Escape: 0x1B,
            QtCore.Qt.Key_PageUp: 0x21,
            QtCore.Qt.Key_PageDown: 0x22,
            QtCore.Qt.Key_End: 0x23,
            QtCore.Qt.Key_Home: 0x24,
            QtCore.Qt.Key_Left: 0x25,
            QtCore.Qt.Key_Up: 0x26,
            QtCore.Qt.Key_Right: 0x27,
            QtCore.Qt.Key_Down: 0x28,
            QtCore.Qt.Key_Insert: 0x2D,
            QtCore.Qt.Key_Delete: 0x2E,
            QtCore.Qt.Key_0: 0x30,
            QtCore.Qt.Key_1: 0x31,
            QtCore.Qt.Key_2: 0x32,
            QtCore.Qt.Key_3: 0x33,
            QtCore.Qt.Key_4: 0x34,
            QtCore.Qt.Key_5: 0x35,
            QtCore.Qt.Key_6: 0x36,
            QtCore.Qt.Key_7: 0x37,
            QtCore.Qt.Key_8: 0x38,
            QtCore.Qt.Key_9: 0x39,
            QtCore.Qt.Key_A: 0x41,
            QtCore.Qt.Key_B: 0x42,
            QtCore.Qt.Key_C: 0x43,
            QtCore.Qt.Key_D: 0x44,
            QtCore.Qt.Key_E: 0x45,
            QtCore.Qt.Key_F: 0x46,
            QtCore.Qt.Key_G: 0x47,
            QtCore.Qt.Key_H: 0x48,
            QtCore.Qt.Key_I: 0x49,
            QtCore.Qt.Key_J: 0x4A,
            QtCore.Qt.Key_K: 0x4B,
            QtCore.Qt.Key_L: 0x4C,
            QtCore.Qt.Key_M: 0x4D,
            QtCore.Qt.Key_N: 0x4E,
            QtCore.Qt.Key_O: 0x4F,
            QtCore.Qt.Key_P: 0x50,
            QtCore.Qt.Key_Q: 0x51,
            QtCore.Qt.Key_R: 0x52,
            QtCore.Qt.Key_S: 0x53,
            QtCore.Qt.Key_T: 0x54,
            QtCore.Qt.Key_U: 0x55,
            QtCore.Qt.Key_V: 0x56,
            QtCore.Qt.Key_W: 0x57,
            QtCore.Qt.Key_X: 0x58,
            QtCore.Qt.Key_Y: 0x59,
            QtCore.Qt.Key_Z: 0x5A,
            QtCore.Qt.Key_F1: 0x70,
            QtCore.Qt.Key_F2: 0x71,
            QtCore.Qt.Key_F3: 0x72,
            QtCore.Qt.Key_F4: 0x73,
            QtCore.Qt.Key_F5: 0x74,
            QtCore.Qt.Key_F6: 0x75,
            QtCore.Qt.Key_F7: 0x76,
            QtCore.Qt.Key_F8: 0x77,
            QtCore.Qt.Key_F9: 0x78,
            QtCore.Qt.Key_F10: 0x79,
            QtCore.Qt.Key_F11: 0x7A,
            QtCore.Qt.Key_F12: 0x7B,
        }

        
        if not hasattr(self, 'trigger_bot') or self.trigger_bot is None:
            try:
                from triggerbot import TriggerBot
            except ImportError:
                class TriggerBot:
                    def __init__(self):
                        self.enabled = False
                        self.enemies_only = False
                    def set_mode(self, mode): pass
                    def set_key(self, key): pass
                pass
            self.trigger_bot = TriggerBot()
        if not hasattr(self, 'aim_bot') or self.aim_bot is None:
            try:
                from aim import AimBot
            except ImportError:
                class AimBot:
                    def __init__(self):
                        self.enabled = False
                        self.enemies_only = False
                    def set_mode(self, mode): pass
                    def set_distance_mode(self, mode): pass
                    def set_smooth(self, smooth): pass
                    def set_radius(self, radius): pass
                    def set_key(self, key): pass
                pass
            self.aim_bot = AimBot()
        if not hasattr(self, 'esp') or self.esp is None:
            try:
                from esp import ESP
            except ImportError:
                class ESP:
                    def __init__(self):
                        self.rendering = False
                        self.mode = 0
                        self.line_rendering = False
                        self.hp_bar = False
                        self.head_hitbox = False
                        self.bones = False
                        self.nickname = False
                        self.weapon = False
                        self.bomb_esp = False
                        self.bomb_timer = False
                        self.defuse_timer = False
                        self.minimap = False
                pass
            self.esp = ESP()

        self.is_dragging = False
        self.drag_start_position = None
        self.setStyleSheet("background-color: #020203;")

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.initUI()

    def initUI(self):
        self.setFixedSize(950, 650) 
        
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        left_column = QtWidgets.QVBoxLayout()
        left_column.setContentsMargins(10, 10, 10, 10)
        left_column.setSpacing(15)
        
        # Header with animated gradient and effects
        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(70)
        header_widget.setObjectName("headerWidget")
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        # Animated gradient for the header
        self.gradient_animation = QtCore.QVariantAnimation()
        self.gradient_animation.setDuration(3000)
        self.gradient_animation.setStartValue(0)
        self.gradient_animation.setEndValue(100)
        self.gradient_animation.valueChanged.connect(lambda: header_widget.update())
        self.gradient_animation.setLoopCount(-1)  # Infinite loop
        
        # Logo with glow effect
        logo_label = QtWidgets.QLabel("Mortal Hack")
        logo_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #ffffff;
            padding: 5px;
            background: transparent;
        """)
        
        # Add glow effect to logo
        glow_effect = QtWidgets.QGraphicsDropShadowEffect()
        glow_effect.setBlurRadius(20)
        glow_effect.setColor(QtGui.QColor(156, 39, 176, 150))
        glow_effect.setOffset(0, 0)
        logo_label.setGraphicsEffect(glow_effect)
        
        # Simple glow animation
        self.glow_animation = QtCore.QPropertyAnimation(glow_effect, b"blurRadius")
        self.glow_animation.setDuration(2000)
        self.glow_animation.setStartValue(10)
        self.glow_animation.setEndValue(25)
        self.glow_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.glow_animation.setLoopCount(-1)  # Infinite loop
        self.glow_animation.start()  # Start the animation
        
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        
        # Apply custom paint event for gradient background
        def paintEvent(event):
            painter = QtGui.QPainter(header_widget)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            # Animated gradient
            gradient = QtGui.QLinearGradient(0, 0, header_widget.width(), 0)
            pos = self.gradient_animation.currentValue() / 100.0
            
            gradient.setColorAt(max(0, pos - 0.3), QtGui.QColor(26, 9, 51, 200))  # Dark purple
            gradient.setColorAt(pos, QtGui.QColor(74, 20, 140, 200))  # Purple
            gradient.setColorAt(min(1, pos + 0.3), QtGui.QColor(26, 9, 51, 200))  # Dark purple
            
            # Draw rounded rect with gradient
            path = QtGui.QPainterPath()
            path.addRoundedRect(0, 0, header_widget.width(), header_widget.height(), 15, 15)
            painter.fillPath(path, gradient)
            
            # Draw subtle border
            border_path = QtGui.QPainterPath()
            border_path.addRoundedRect(0.5, 0.5, header_widget.width()-1, header_widget.height()-1, 14.5, 14.5)
            painter.setPen(QtGui.QPen(QtGui.QColor(156, 39, 176, 100), 1))
            painter.drawPath(border_path)
            
            painter.end()
        
        header_widget.paintEvent = paintEvent
        
        # Start animations
        self.gradient_animation.start()
        self.glow_animation.start()
        
        # Add subtle shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QtGui.QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        header_widget.setGraphicsEffect(shadow)
        
        left_column.addWidget(header_widget)
        
        # Create animated category list
        self.category_list = QtWidgets.QListWidget()
        self.category_list.setFixedWidth(200)
        self.category_list.setSpacing(3)
        
        # Add categories with icons and animations
        categories = [
            ("Визуалы", "ESP"),
            ("Аим-бот", "Aimbot"),
            ("Триггер-бот", "Triggerbot"),
            ("Разное", "Other"),
            ("Конфигурации", "Config")
        ]
        
        for text, icon in categories:
            item = QtWidgets.QListWidgetItem(f"  {icon}  {text}")
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.category_list.addItem(item)
        
        # Apply styles with animations
        self.category_list.setStyleSheet("""
            QListWidget {
                background-color: #0a0a0a;
                color: #b0b0b0;
                border: 1px solid #2a2a2a;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 8px;
                margin: 2px 0;
                border-radius: 8px;
                background: transparent;
                border: 1px solid transparent;
            }
            QListWidget::item:hover {
                background: rgba(156, 39, 176, 0.2);
                border: 1px solid rgba(156, 39, 176, 0.4);
                color: #e0e0e0;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a0933, stop:1 #4a148c);
                border: 1px solid #9c27b0;
                color: white;
                font-weight: bold;
            }
            QScrollBar:vertical {
                border: none;
                background: #0a0a0a;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a148c;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.category_list.setCurrentRow(0)
        left_column.addWidget(self.category_list)
        left_column.addStretch() 
        
        left_wrapper = QtWidgets.QWidget()
        left_wrapper.setLayout(left_column)
        left_wrapper.setStyleSheet("background-color: #0a0a0a;")
        left_wrapper.setFixedWidth(220)
        
        right_wrapper = QtWidgets.QWidget()
        right_wrapper.setStyleSheet("background-color: #080809; border-radius: 10px;")
        right_layout = QtWidgets.QVBoxLayout(right_wrapper)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a container widget for the stacked widget to apply effects
        self.stack_container = QtWidgets.QWidget()
        self.stack_layout = QtWidgets.QVBoxLayout(self.stack_container)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the stacked widget with fade effect
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        
        # Create all widgets
        self.esp_widget = self.create_esp_widget()
        self.aim_widget = self.create_aim_widget()
        self.trigger_widget = self.create_trigger_widget()
        self.misc_widget = self.create_misc_widget()
        self.config_widget = self.create_config_widget()
        
        # Add widgets to stack
        self.stack.addWidget(self.esp_widget)
        self.stack.addWidget(self.aim_widget)
        self.stack.addWidget(self.trigger_widget)
        self.stack.addWidget(self.misc_widget)
        self.stack.addWidget(self.config_widget)
        
        # Apply opacity effect to the stack
        self.stack_opacity = QtWidgets.QGraphicsOpacityEffect()
        self.stack.setGraphicsEffect(self.stack_opacity)
        
        # Create animation for fade in/out
        self.fade_animation = QtCore.QPropertyAnimation(self.stack_opacity, b"opacity")
        self.fade_animation.setDuration(200)  # 200ms fade duration
        
        # Connect category change to animated switch
        self.category_list.currentRowChanged.connect(self.animate_stack_change)
        
        self.stack_layout.addWidget(self.stack)
        right_layout.addWidget(self.stack_container)
        
        # Set initial opacity
        self.stack_opacity.setOpacity(1.0)
        
        # Initialize current index
        self.current_stack_index = 0
        
        main_layout.addWidget(left_wrapper)
        main_layout.addWidget(right_wrapper)
        
        self.setLayout(main_layout)
        
    def animate_stack_change(self, index):
        """Animate the transition between menu tabs with a fade effect"""
        if index == self.current_stack_index or index < 0 or index >= self.stack.count():
            return
            
        # Disable category list during animation to prevent rapid switching
        self.category_list.setEnabled(False)
        
        # Set up fade out animation
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        
        # When fade out is complete, switch the widget and fade back in
        def on_fade_out_finished():
            # Change the current widget
            self.stack.setCurrentIndex(index)
            self.current_stack_index = index
            
            # Set up fade in animation
            self.fade_animation.finished.disconnect()
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            
            def on_fade_in_finished():
                self.fade_animation.finished.disconnect()
                self.category_list.setEnabled(True)
                
            self.fade_animation.finished.connect(on_fade_in_finished)
            self.fade_animation.start()
            
        self.fade_animation.finished.connect(on_fade_out_finished)
        self.fade_animation.start()
        
        # The connection is now handled by animate_stack_change
        # self.category_list.currentRowChanged.connect(self.stack.setCurrentIndex)  # Removed duplicate connection

    def create_misc_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.no_flash_checkbox = QtWidgets.QCheckBox("No Flash (анти-ослепление)")
        self.no_flash_checkbox.setChecked(self.settings.get("no_flash", 0) == 1)
        self.no_flash_checkbox.stateChanged.connect(self.toggle_no_flash)
        layout.addWidget(self.no_flash_checkbox)
        
        bh_group = QtWidgets.QGroupBox("Bunny Hop")
        bh_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        bh_layout = QtWidgets.QVBoxLayout()
        
        self.bunny_hop_checkbox = QtWidgets.QCheckBox("Включить Bunny Hop")
        self.bunny_hop_checkbox.setChecked(self.settings.get("bunny_hop", 0) == 1)
        self.bunny_hop_checkbox.stateChanged.connect(self.toggle_bunny_hop)
        bh_layout.addWidget(self.bunny_hop_checkbox)
        
        bh_key_layout = QtWidgets.QHBoxLayout()
        bh_key_layout.addWidget(QtWidgets.QLabel("Клавиша активации:"))
        
        self.bunny_hop_key_btn = QtWidgets.QPushButton(self.get_key_text(self.settings.get("bunny_hop_key", 0x06)))
        self.bunny_hop_key_btn.setFixedWidth(100)
        self.bunny_hop_key_btn.clicked.connect(lambda: self.start_rebind('bunny_hop'))
        
        bh_key_layout.addWidget(self.bunny_hop_key_btn)
        bh_key_layout.addStretch()
        bh_layout.addLayout(bh_key_layout)
        
        bh_group.setLayout(bh_layout)
        layout.addWidget(bh_group)
        
        self.sniper_crosshair_cb = QtWidgets.QCheckBox("Прицел для снайперских винтовок")
        self.sniper_crosshair_cb.setChecked(self.settings.get("sniper_crosshair", 1) == 1)
        self.sniper_crosshair_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.sniper_crosshair_cb)

        fov_group = QtWidgets.QGroupBox("FOV Changer")
        fov_group = QtWidgets.QGroupBox("FOV Changer")
        fov_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        fov_layout = QtWidgets.QVBoxLayout()
        
        self.fov_value_label = QtWidgets.QLabel(f"Текущий FOV: {self.settings.get('fov', 90)}")
        self.fov_value_label.setStyleSheet("color: white;")
        fov_layout.addWidget(self.fov_value_label)
        
        self.fov_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fov_slider.setMinimum(30)
        self.fov_slider.setMaximum(150)
        
        saved_fov = self.settings.get('fov', 90)
        self.fov_slider.setValue(int(saved_fov))  
        
        self.fov_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.fov_slider.setTickInterval(10)
        self.fov_slider.valueChanged.connect(self.on_fov_changed)
        fov_layout.addWidget(self.fov_slider)
        
        labels_layout = QtWidgets.QHBoxLayout()
        min_label = QtWidgets.QLabel("30")
        min_label.setStyleSheet("color: gray;")
        max_label = QtWidgets.QLabel("150")
        max_label.setStyleSheet("color: gray;")
        labels_layout.addWidget(min_label)
        labels_layout.addStretch()
        labels_layout.addWidget(max_label)
        fov_layout.addLayout(labels_layout)
        
        fov_group.setLayout(fov_layout)
        layout.addWidget(fov_group)

        layout.addStretch(1)
        widget.setLayout(layout)
        widget.setStyleSheet("""
            QWidget {
                background-color: #080809;
                color: white;
                border-radius: 10px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #333;
                border-radius: 4px;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #9c27b0;
                border: 2px solid #7b1fa2;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #9c27b0;
                border-radius: 4px;
            }
        """)
        
        # Apply initial FOV value
        QtCore.QTimer.singleShot(1000, lambda: self.apply_fov(force_apply=True))
        
        return widget

    def on_fov_changed(self, value):
        self.settings["fov"] = value
        self.fov_value_label.setText(f"Текущий FOV: {value}")
        save_settings(self.settings)
        self.apply_fov()
        
    def toggle_no_flash(self, state):
        enabled = state == 2  # Qt.Checked is 2, Unchecked is 0
        self.settings["no_flash"] = 1 if enabled else 0
        self._save_settings_delayed()
        self.apply_no_flash(False)  # Не форсируем применение при переключении чекбокса
        print(f"[No Flash] {'Enabled' if enabled else 'Disabled'}")
        
    def apply_no_flash(self, force_apply=False):
        # Попытка найти и изменить m_flFlashMaxAlpha для local player
        try:
            if not hasattr(self, 'no_flash_checkbox') or not self.no_flash_checkbox:
                print("[No Flash] Checkbox not initialized")
                if force_apply:
                    QtCore.QTimer.singleShot(1000, lambda: self.apply_no_flash(True))
                return
                
            pm = self._get_pm()
            if not pm:
                print("[No Flash] Process not found")
                if force_apply:
                    QtCore.QTimer.singleShot(1000, lambda: self.apply_no_flash(True))
                return
                
            if not hasattr(self, '_m_flFlashMaxAlpha'):
                # Cache the offset on first use
                try:
                    self._m_flFlashMaxAlpha = self._client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashMaxAlpha']
                    print(f"[No Flash] Offset loaded: {self._m_flFlashMaxAlpha}")
                except Exception as e:
                    print(f"[No Flash] Error getting offset: {e}")
                    if force_apply:
                        QtCore.QTimer.singleShot(1000, lambda: self.apply_no_flash(True))
                    return
                
            dwLocalPlayerPawn = self._offsets['client.dll']['dwLocalPlayerPawn']
            local_player_pawn_addr = pm.read_longlong(self._client + dwLocalPlayerPawn)
            
            if local_player_pawn_addr and local_player_pawn_addr > 0x10000:
                value = 0.0 if self.no_flash_checkbox.isChecked() else 255.0
                try:
                    pm.write_float(local_player_pawn_addr + self._m_flFlashMaxAlpha, value)
                    print(f"[No Flash] Successfully set to {value}")
                    # Обновляем настройку в конфиге
                    self.settings["no_flash"] = 1 if self.no_flash_checkbox.isChecked() else 0
                    
                    # Also set flash duration to 0
                    m_flFlashDuration = self._client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashDuration']
                    pm.write_float(local_player_pawn_addr + m_flFlashDuration, 0.0)
                    
                except Exception as e:
                    print(f"[No Flash] Error writing value: {e}")
                    if force_apply:
                        QtCore.QTimer.singleShot(1000, lambda: self.apply_no_flash(True))
            
        except Exception as e:
            print(f"[No Flash] General error: {e}")
            if force_apply:
                QtCore.QTimer.singleShot(1000, lambda: self.apply_no_flash(True))
    def toggle_bunny_hop(self, state):
        enabled = state == 2
        self.settings["bunny_hop"] = 1 if enabled else 0
        self._save_settings_delayed()
        
        print(f"[Bunny Hop] Toggled to: {enabled}")
        
        # Останавливаем предыдущий поток, если он был
        if hasattr(self, '_bunny_hop_running') and self._bunny_hop_running:
            print("[Bunny Hop] Stopping existing thread...")
            self._bunny_hop_running = False
            if hasattr(self, '_bunny_hop_thread') and self._bunny_hop_thread.is_alive():
                self._bunny_hop_thread.join(timeout=0.5)
        
        # Запускаем новый поток, если нужно
        if enabled:
            print("[Bunny Hop] Starting new thread...")
            self._bunny_hop_running = True
            self._bunny_hop_thread = threading.Thread(target=self._bunny_hop_loop, daemon=True)
            self._bunny_hop_thread.start()
            print("[Bunny Hop] New thread started")

    def _get_pm(self):
        if not hasattr(self, '_pm') or self._pm is None or not self._pm.process_handle:
            try:
                self._pm = pymem.Pymem("cs2.exe")
                # Загружаем оффсеты при первом подключении
                if self._offsets is None:
                    self._offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
                if self._client_dll is None:
                    self._client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
                print("[Bunny Hop] Успешно подключились к игре")
            except Exception as e:
                print(f"[Bunny Hop] Ошибка подключения к игре: {e}")
                return None
        return self._pm

    def _stop_bunny_hop(self):
        self._bunny_hop_running = False
        if hasattr(self, '_bunny_hop_thread') and self._bunny_hop_thread.is_alive():
            self._bunny_hop_thread.join(timeout=1.0)

    def _bunny_hop_loop(self):
        print("[Bunny Hop] Thread started")
        try:
            # Apply no flash when the loop starts if enabled
            if hasattr(self, 'no_flash_checkbox') and self.no_flash_checkbox.isChecked():
                self.apply_no_flash(True)
            # Получаем объект pymem
            pm = self._get_pm()
            if not pm:
                print("[Bunny Hop] Failed to get process handle")
                return
                
            print("[Bunny Hop] Got process handle")
            
            # Получаем базовый адрес client.dll
            try:
                client_module = pymem.process.module_from_name(pm.process_handle, "client.dll")
                if not client_module:
                    print("[Bunny Hop] Failed to find client.dll module")
                    return
                    
                client = client_module.lpBaseOfDll
                print(f"[Bunny Hop] Client base: {hex(client)}")
            except Exception as e:
                print(f"[Bunny Hop] Failed to get client.dll base: {e}")
                return
            
            # Получаем оффсеты
            try:
                if not hasattr(self, '_offsets') or not self._offsets:
                    print("[Bunny Hop] Offsets not loaded, trying to load...")
                    self._offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
                    
                if not hasattr(self, '_client_dll') or not self._client_dll:
                    print("[Bunny Hop] Client DLL info not loaded, trying to load...")
                    self._client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
                
                dwLocalPlayer = self._offsets['client.dll']['dwLocalPlayerPawn']
                m_fFlags = self._client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_fFlags']
                print(f"[Bunny Hop] Offsets - dwLocalPlayer: {hex(dwLocalPlayer)}, m_fFlags: {hex(m_fFlags)}")
            except Exception as e:
                print(f"[Bunny Hop] Failed to get offsets: {e}")
                import traceback
                traceback.print_exc()
                return
            
            while hasattr(self, '_bunny_hop_running') and self._bunny_hop_running:
                try:
                    # Пропускаем итерацию, если активно окно ребинда или чекбокс выключен
                    if (not hasattr(self, 'bunny_hop_checkbox') or 
                        not self.bunny_hop_checkbox.isChecked() or 
                        hasattr(self, 'rebind_mode')):
                        time.sleep(0.1)
                        continue
                        
                    # Получаем текущую клавишу из настроек
                    bh_key = self.settings.get("bunny_hop_key", 0x06)  # По умолчанию правая кнопка мыши (0x06)
                    
                    # Проверяем, нажата ли клавиша активации
                    key_state = win32api.GetAsyncKeyState(bh_key)
                    if key_state < 0:  # Если клавиша нажата
                        # Получаем указатель на локального игрока
                        player = pm.read_ulonglong(client + dwLocalPlayer)
                        if not player:
                            time.sleep(0.01)
                            continue
                            
                        # Проверяем, находится ли игрок на земле
                        flags = pm.read_uint(player + m_fFlags)
                        on_ground = flags & (1 << 0)  # Флаг нахождения на земле
                        
                        if on_ground:  # Если игрок на земле
                            # Симулируем нажатие пробела
                            win32api.keybd_event(0x20, 0, 0, 0)  # 0x20 - VK_SPACE
                            time.sleep(0.01)  # Короткая задержка
                            win32api.keybd_event(0x20, 0, win32con.KEYEVENTF_KEYUP, 0)  # Отпускаем пробел
                            print("[Bunny Hop] Jump!")
                        
                        time.sleep(0.01)  # Небольшая задержка для снижения нагрузки на процессор
                    
                    time.sleep(0.01)  # Общая задержка между проверками
                            
                except Exception as e:
                    print(f"[Bunny Hop] Error in main loop: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"[Bunny Hop] Critical error: {e}")
        finally:
            print("[Bunny Hop] Thread stopped")
            self._bunny_hop_running = False
        
    def closeEvent(self, event):
        self._stop_bunny_hop()
        event.accept()
        
    def _get_pm(self):
        if self._pm is None:
            try:
                self._pm = pymem.Pymem("cs2.exe")
                self._offsets, self._client_dll = get_offsets_and_client_dll()
                self._client = pymem.process.module_from_name(
                    self._pm.process_handle, "client.dll").lpBaseOfDll
            except Exception as e:
                print(f"[Error] Failed to initialize Pymem: {e}")
                return None
        return self._pm

    def _save_settings_delayed(self):
        # Save settings with a small delay to reduce disk I/O
        if hasattr(self, '_save_timer'):
            self._save_timer.stop()
        
        self._save_timer = QtCore.QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(lambda: save_settings(self.settings))
        self._save_timer.start(500)  # Save after 500ms of inactivity

    def on_fov_changed(self, value):
        current_time = time.time()
        if current_time - self._last_fov_update < self._fov_update_interval and value != self.settings.get('fov', 90):
            return
            
        self._last_fov_update = current_time
        self.settings["fov"] = value
        self.fov_value_label.setText(f"Текущий FOV: {value}")
        save_settings(self.settings)  # Save immediately when FOV changes
        self.apply_fov()
        
    def apply_fov(self, force_apply=False):
        if not force_apply and not hasattr(self, '_fov_initialized'):
            self._fov_initialized = True
            return
            
        try:
            pm = self._get_pm()
            if not pm:
                return
                
            # Get LocalPlayerController
            dwLocalPlayerController = self._offsets['client.dll']['dwLocalPlayerController']
            local_controller = pm.read_longlong(self._client + dwLocalPlayerController)
            
            if local_controller:
                # Try to get m_iDesiredFOV offset from client_dll structure
                try:
                    m_iDesiredFOV = self._client_dll['client.dll']['classes']['C_CSPlayerController']['fields']['m_iDesiredFOV']
                except KeyError:
                    # Fallback to hardcoded offset if not found in the structure
                    m_iDesiredFOV = 0x6F4
                
                # Write the new FOV value
                pm.write_int(local_controller + m_iDesiredFOV, self.settings.get("fov", 90))
                
        except Exception as e:
            print(f"[FOV Changer] Error applying FOV: {e}")

    def create_config_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        config_label = QtWidgets.QLabel("Настройки конфигурации")
        config_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(config_label)

        # Список конфигураций
        self.config_list = QtWidgets.QListWidget()
        self.update_config_list()
        self.config_list.itemClicked.connect(self.select_config)
        layout.addWidget(self.config_list)

        # Поле для ввода названия конфигурации
        self.config_name_input = QtWidgets.QLineEdit()
        self.config_name_input.setPlaceholderText("Введите название конфигурации")
        layout.addWidget(self.config_name_input)

        # Кнопка для сохранения конфигурации
        save_button = QtWidgets.QPushButton("Сохранить конфигурацию")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

        # Кнопка для загрузки конфигурации
        load_button = QtWidgets.QPushButton("Загрузить конфигурацию")
        load_button.clicked.connect(self.load_config)
        layout.addWidget(load_button)

        # Кнопка для удаления конфигурации
        delete_button = QtWidgets.QPushButton("Удалить конфигурацию")
        delete_button.clicked.connect(self.delete_config)
        layout.addWidget(delete_button)

        # Кнопка для обновления списка конфигов
        refresh_button = QtWidgets.QPushButton("Обновить список")
        refresh_button.clicked.connect(self.update_config_list)
        layout.addWidget(refresh_button)

        # Добавить пустое пространство
        layout.addStretch(1)

        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #080809; border-radius: 10px;")
        return widget

    def update_config_list(self):
        config_dir = os.path.join("C:\\", "MortalConfigs")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        self.config_list.clear()
        for file in os.listdir(config_dir):
            if file.endswith(".cfg"):
                self.config_list.addItem(file.replace(".cfg", ""))

    def select_config(self, item):
        self.config_name_input.setText(item.text().replace(".cfg", ""))

    def save_config(self):
        config_name = self.config_name_input.text()
        if not config_name:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите название конфигурации.")
            return

        config_dir = os.path.join("C:\\", "MortalConfigs")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        config_path = os.path.join(config_dir, f"{config_name}.cfg")

        # Save all settings, including key bindings and other configurations
        with open(config_path, "w") as f:
            json.dump(self.settings, f, indent=4)

        self.update_config_list()
        QtWidgets.QMessageBox.information(self, "Успех", f"Конфигурация '{config_name}' сохранена.")

    def load_config(self):
        config_name = self.config_name_input.text()
        if not config_name:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите название конфигурации.")
            return

        config_path = os.path.join("C:\\", "MortalConfigs", f"{config_name}.cfg")
        if not os.path.exists(config_path):
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Конфигурация '{config_name}' не найдена.")
            return

        # Load all settings, including key bindings and other configurations
        with open(config_path, "r") as f:
            self.settings = json.load(f)

        # Синхронизируем UI с новыми настройками
        self.update_ui_from_settings()

        # Apply all settings in a synchronized manner
        self.apply_all_settings()
        # Сохраняем настройки в файл, чтобы процессы подхватили изменения
        self.save_settings()

        QtWidgets.QMessageBox.information(self, "Успех", f"Конфигурация '{config_name}' загружена.")

    def delete_config(self):
        config_name = self.config_name_input.text()
        if not config_name:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите название конфигурации.")
            return

        config_path = os.path.join("C:\\", "MortalConfigs", f"{config_name}.cfg")
        if not os.path.exists(config_path):
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Конфигурация '{config_name}' не найдена.")
            return

        os.remove(config_path)
        self.update_config_list()
        QtWidgets.QMessageBox.information(self, "Успех", f"Конфигурация '{config_name}' удалена.")

    def update_ui_from_settings(self):
        # Флаг массового обновления
        self.massive_update = True
        # Отключаем сигналы, чтобы не было лишних вызовов save_settings
        for cb in [self.esp_rendering_cb, self.line_rendering_cb, self.hp_bar_rendering_cb, self.head_hitbox_rendering_cb, self.bons_cb, self.nickname_cb, self.weapon_cb, self.bomb_esp_cb, self.bomb_timer_cb, self.defuse_timer_cb, self.minimap_cb, self.aim_active_cb, self.aim_enemies_only_cb, self.trigger_bot_active_cb, self.trigger_enemies_only_cb, self.sniper_crosshair_cb]:
            cb.blockSignals(True)
        self.esp_mode_cb.blockSignals(True)
        self.aim_mode_cb.blockSignals(True)
        self.aim_mode_distance_cb.blockSignals(True)
        if hasattr(self, 'trigger_mode_cb'):
            self.trigger_mode_cb.blockSignals(True)

        # Update all UI elements based on the current settings
        self.esp_rendering_cb.setChecked(self.settings.get("esp_rendering", 0) == 1)
        self.esp_mode_cb.setCurrentIndex(self.settings.get("esp_mode", 0))
        self.line_rendering_cb.setChecked(self.settings.get("line_rendering", 0) == 1)
        self.hp_bar_rendering_cb.setChecked(self.settings.get("hp_bar_rendering", 0) == 1)
        self.head_hitbox_rendering_cb.setChecked(self.settings.get("head_hitbox_rendering", 0) == 1)
        self.bons_cb.setChecked(self.settings.get("bons", 0) == 1)
        self.nickname_cb.setChecked(self.settings.get("nickname", 0) == 1)
        self.weapon_cb.setChecked(self.settings.get("weapon", 0) == 1)
        self.bomb_esp_cb.setChecked(self.settings.get("bomb_esp", 0) == 1)
        self.bomb_timer_cb.setChecked(self.settings.get("bomb_timer", 0) == 1)
        self.defuse_timer_cb.setChecked(self.settings.get("defuse_timer", 0) == 1)
        self.minimap_cb.setChecked(self.settings.get("minimap", 0) == 1)
        self.aim_active_cb.setChecked(self.settings.get("aim_active", 0) == 1)
        self.radius_slider.setValue(self.settings.get("radius", 0))
        self.aim_mode_cb.setCurrentIndex(self.settings.get("aim_mode", 0))
        self.aim_mode_distance_cb.setCurrentIndex(self.settings.get("aim_mode_distance", 0))
        self.smooth_slider.setValue(self.settings.get("aim_smooth", 10))
        self.aim_enemies_only_cb.setChecked(self.settings.get("aim_enemies_only", 0) == 1)
        self.trigger_bot_active_cb.setChecked(self.settings.get("trigger_bot_active", 0) == 1)
        self.trigger_enemies_only_cb.setChecked(self.settings.get("trigger_enemies_only", 0) == 1)
        if hasattr(self, 'trigger_mode_cb'):
            self.trigger_mode_cb.setCurrentIndex(self.settings.get("trigger_mode", 0))
        if "keyboard" in self.settings:
            self.aim_rebind_btn.setText(self.get_key_text(self.settings["keyboard"]))
        if "keyboards" in self.settings:
            self.trigger_rebind_btn.setText(self.get_key_text(self.settings["keyboards"]))
        if hasattr(self, 'bunny_hop_key_btn'):
            self.bunny_hop_key_btn.setText("Клавиша: " + self.get_key_text(self.settings.get("bunny_hop_key", 0x06)))

        # Update color buttons
        self.update_color_buttons()

        # Включаем сигналы обратно
        for cb in [self.esp_rendering_cb, self.line_rendering_cb, self.hp_bar_rendering_cb, self.head_hitbox_rendering_cb, self.bons_cb, self.nickname_cb, self.weapon_cb, self.bomb_esp_cb, self.bomb_timer_cb, self.defuse_timer_cb, self.minimap_cb, self.aim_active_cb, self.aim_enemies_only_cb, self.trigger_bot_active_cb, self.trigger_enemies_only_cb, self.sniper_crosshair_cb]:
            cb.blockSignals(False)
        self.esp_mode_cb.blockSignals(False)
        self.aim_mode_cb.blockSignals(False)
        self.aim_mode_distance_cb.blockSignals(False)
        if hasattr(self, 'trigger_mode_cb'):
            self.trigger_mode_cb.blockSignals(False)
        # Снимаем флаг массового обновления
        self.massive_update = False

    def update_color_buttons(self):
        if not hasattr(self, 'color_buttons'):
            return
            
        for color_key, button in self.color_buttons.items():
            if color_key in self.settings:
                color = self.settings[color_key]
                if isinstance(color, list) and len(color) >= 3:
                    self._update_button_color(button, color)

    def apply_all_settings(self):
        # Update UI elements for all tabs
        self.update_ui_from_settings()

        # Force update for all widgets in the stack
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if hasattr(widget, 'update'):  # If the widget has an update method
                widget.update()

        # Apply settings to the program logic
        self.apply_settings_to_logic()

    def apply_settings_to_logic(self):
        # Sniper crosshair setting
        if hasattr(self, 'sniper_crosshair_cb'):
            self.sniper_crosshair_cb.setChecked(self.settings.get("sniper_crosshair", 1) == 1)
            
        # Применение настроек ESP (рендеринг, режимы и т.д.)
        if hasattr(self, 'esp_window') and self.esp_window:
            self.esp_window.settings = self.settings
            self.esp_window.update_scene()

        # Применение настроек Trigger Bot
        if hasattr(self, 'trigger_bot'):
            self.trigger_bot.enabled = self.settings.get("trigger_bot_active", 0) == 1
            self.trigger_bot.enemies_only = self.settings.get("trigger_enemies_only", 1) == 1
            
        # Применение настроек Aim Bot
        if hasattr(self, 'aim_bot'):
            self.aim_bot.enabled = self.settings.get("aim_active", 0) == 1
            self.aim_bot.enemies_only = self.settings.get("aim_enemies_only", 1) == 1
            
        # Применение настроек Bunny Hop
        if hasattr(self, 'bunny_hop_checkbox'):
            bh_enabled = self.settings.get("bunny_hop", 0) == 1
            self.bunny_hop_checkbox.setChecked(bh_enabled)
            # Force update the Bunny Hop state
            if bh_enabled:
                if not hasattr(self, '_bunny_hop_running') or not self._bunny_hop_running:
                    self.toggle_bunny_hop(2)  # 2 = Qt.Checked
            else:
                if hasattr(self, '_bunny_hop_running') and self._bunny_hop_running:
                    self.toggle_bunny_hop(0)  # 0 = Qt.Unchecked
            
        # Применение настроек No Flash
        if hasattr(self, 'no_flash_checkbox'):
            nf_enabled = self.settings.get("no_flash", 0) == 1
            self.no_flash_checkbox.setChecked(nf_enabled)
            # Force update the No Flash state
            if nf_enabled:
                self.apply_no_flash(True)
            
        # Apply Legit AIM setting
        if hasattr(self, 'aim_legit_checkbox'):
            self.aim_legit_checkbox.setChecked(self.settings.get("aim_legit", 0) == 1)
        
        # Apply FOV setting after loading config
        if hasattr(self, 'fov_slider'):
            fov_value = self.settings.get("fov", 90)
            self.fov_slider.setValue(int(fov_value))
            self.fov_value_label.setText(f"Текущий FOV: {fov_value}")
            self.apply_fov(force_apply=True)

        if hasattr(self, 'trigger_bot') and self.trigger_bot:
            self.trigger_bot.enabled = self.settings.get("trigger_bot_active", 0) == 1
            self.trigger_bot.enemies_only = self.settings.get("trigger_enemies_only", 0) == 1
            if hasattr(self.trigger_bot, "set_mode"):
                self.trigger_bot.set_mode(self.settings.get("trigger_mode", 0))
            if hasattr(self.trigger_bot, "set_key"):
                self.trigger_bot.set_key(self.settings["keyboards"])

        # Aim Bot (аимбот)
        if hasattr(self, 'aim_bot') and self.aim_bot:
            self.aim_bot.enabled = self.settings.get("aim_active", 0) == 1
            self.aim_bot.enemies_only = self.settings.get("aim_enemies_only", 0) == 1
            if hasattr(self.aim_bot, "set_mode"):
                self.aim_bot.set_mode(self.settings.get("aim_mode", 0))
            if hasattr(self.aim_bot, "set_distance_mode"):
                self.aim_bot.set_distance_mode(self.settings.get("aim_mode_distance", 0))
            if hasattr(self.aim_bot, "set_smooth"):
                self.aim_bot.set_smooth(self.settings.get("aim_smooth", 10))
            if hasattr(self.aim_bot, "set_radius"):
                self.aim_bot.set_radius(self.settings.get("radius", 0))
            if hasattr(self.aim_bot, "set_key"):
                self.aim_bot.set_key(self.settings["keyboard"])

        # Прочие ESP-настройки (если есть отдельный объект esp)
        if hasattr(self, 'esp') and self.esp:
            self.esp.rendering = self.settings.get("esp_rendering", 0) == 1
            self.esp.mode = self.settings.get("esp_mode", 0)
            self.esp.line_rendering = self.settings.get("line_rendering", 0) == 1
            self.esp.hp_bar = self.settings.get("hp_bar_rendering", 0) == 1
            self.esp.head_hitbox = self.settings.get("head_hitbox_rendering", 0) == 1
            self.esp.bones = self.settings.get("bons", 0) == 1
            self.esp.nickname = self.settings.get("nickname", 0) == 1
            self.esp.weapon = self.settings.get("weapon", 0) == 1
            self.esp.bomb_esp = self.settings.get("bomb_esp", 0) == 1
            self.esp.bomb_timer = self.settings.get("bomb_timer", 0) == 1
            self.esp.defuse_timer = self.settings.get("defuse_timer", 0) == 1
            self.esp.minimap = self.settings.get("minimap", 0) == 1

        # Если есть какие-то потоки или процессы, обнови их параметры
        if hasattr(self, 'update_threads'):
            self.update_threads(self.settings)

        # Если есть другие модули, добавь их применение аналогично

        # Для отладки
        print("Все настройки успешно применены из конфига.")

    def update_ui_from_settings(self):
        # Флаг массового обновления
        self.massive_update = True
        # Отключаем сигналы, чтобы не было лишних вызовов save_settings
        checkboxes = [
            self.esp_rendering_cb, self.line_rendering_cb, self.hp_bar_rendering_cb, 
            self.head_hitbox_rendering_cb, self.bons_cb, self.nickname_cb, 
            self.weapon_cb, self.bomb_esp_cb, self.bomb_timer_cb, 
            self.defuse_timer_cb, self.minimap_cb, self.aim_active_cb, 
            self.aim_enemies_only_cb, self.trigger_bot_active_cb, 
            self.trigger_enemies_only_cb, self.no_flash_checkbox,
            self.bunny_hop_checkbox
        ]
        for cb in checkboxes:
            if hasattr(self, cb.objectName()):
                cb.blockSignals(True)
        self.esp_mode_cb.blockSignals(True)
        self.aim_mode_cb.blockSignals(True)
        self.aim_mode_distance_cb.blockSignals(True)
        if hasattr(self, 'trigger_mode_cb'):
            self.trigger_mode_cb.blockSignals(True)

        # Update all UI elements based on the current settings
        self.esp_rendering_cb.setChecked(self.settings.get("esp_rendering", 0) == 1)
        self.esp_mode_cb.setCurrentIndex(self.settings.get("esp_mode", 0))
        self.line_rendering_cb.setChecked(self.settings.get("line_rendering", 0) == 1)
        self.hp_bar_rendering_cb.setChecked(self.settings.get("hp_bar_rendering", 0) == 1)
        self.head_hitbox_rendering_cb.setChecked(self.settings.get("head_hitbox_rendering", 0) == 1)
        self.bons_cb.setChecked(self.settings.get("bons", 0) == 1)
        self.nickname_cb.setChecked(self.settings.get("nickname", 0) == 1)
        self.weapon_cb.setChecked(self.settings.get("weapon", 0) == 1)
        self.bomb_esp_cb.setChecked(self.settings.get("bomb_esp", 0) == 1)
        self.bomb_timer_cb.setChecked(self.settings.get("bomb_timer", 0) == 1)
        self.defuse_timer_cb.setChecked(self.settings.get("defuse_timer", 0) == 1)
        self.minimap_cb.setChecked(self.settings.get("minimap", 0) == 1)
        self.aim_active_cb.setChecked(self.settings.get("aim_active", 0) == 1)
        self.radius_slider.setValue(self.settings.get("radius", 0))
        self.aim_mode_cb.setCurrentIndex(self.settings.get("aim_mode", 0))
        self.aim_mode_distance_cb.setCurrentIndex(self.settings.get("aim_mode_distance", 0))
        self.smooth_slider.setValue(self.settings.get("aim_smooth", 10))
        self.aim_enemies_only_cb.setChecked(self.settings.get("aim_enemies_only", 0) == 1)
        self.trigger_bot_active_cb.setChecked(self.settings.get("trigger_bot_active", 0) == 1)
        self.trigger_enemies_only_cb.setChecked(self.settings.get("trigger_enemies_only", 0) == 1)
        if hasattr(self, 'trigger_mode_cb'):
            self.trigger_mode_cb.setCurrentIndex(self.settings.get("trigger_mode", 0))
        if "keyboard" in self.settings:
            self.aim_rebind_btn.setText(self.get_key_text(self.settings["keyboard"]))
        if "keyboards" in self.settings:
            self.trigger_rebind_btn.setText(self.get_key_text(self.settings["keyboards"]))
        if hasattr(self, 'bunny_hop_key_btn'):
            self.bunny_hop_key_btn.setText("Клавиша: " + self.get_key_text(self.settings.get("bunny_hop_key", 0x06)))

        # Update color buttons
        self.update_color_buttons()

        # Включаем сигналы обратно
        for cb in [self.esp_rendering_cb, self.line_rendering_cb, self.hp_bar_rendering_cb, self.head_hitbox_rendering_cb, self.bons_cb, self.nickname_cb, self.weapon_cb, self.bomb_esp_cb, self.bomb_timer_cb, self.defuse_timer_cb, self.minimap_cb, self.aim_active_cb, self.aim_enemies_only_cb, self.trigger_bot_active_cb, self.trigger_enemies_only_cb]:
            cb.blockSignals(False)
        self.esp_mode_cb.blockSignals(False)
        self.aim_mode_cb.blockSignals(False)
        self.aim_mode_distance_cb.blockSignals(False)
        if hasattr(self, 'trigger_mode_cb'):
            self.trigger_mode_cb.blockSignals(False)
        # Снимаем флаг массового обновления
        self.massive_update = False

    def create_color_button(self, color_key, label):
        """Create a color button with the current color from settings"""
        # Get the current color from settings or use default
        default_colors = {
            'enemy_visible_color': [255, 0, 0],
            'enemy_hidden_color': [255, 100, 100],
            'friendly_visible_color': [0, 0, 255],
            'friendly_hidden_color': [100, 100, 255]
        }
        
        # Ensure the color setting exists in settings, if not, add it from defaults
        if color_key not in self.settings and color_key in default_colors:
            self.settings[color_key] = default_colors[color_key]
            save_settings(self.settings)
        
        color = self.settings.get(color_key, default_colors.get(color_key, [255, 255, 255]))
        
        # Create a button with colored rectangle
        btn = QtWidgets.QPushButton()
        btn.setFixedSize(60, 20)
        
        # Store the color key as a property for later use
        btn.color_key = color_key
        
        # Set button style with the current color
        self._update_button_color(btn, color)
        
        # Connect the button click to color picker
        btn.clicked.connect(lambda checked, k=color_key, b=btn: self.pick_color(k, b))
        return btn
        
    def _update_button_color(self, button, color):
        """Update the button's color and tooltip"""
        if not hasattr(button, 'color_key'):
            return
            
        # Update the button style
        button.setStyleSheet(f'''
            QPushButton {{
                background-color: rgb({color[0]}, {color[1]}, {color[2]});
                border: 1px solid #555;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 1px solid #888;
            }}
        ''')
        
        # Update tooltip with RGB values
        button.setToolTip(f"RGB: {color[0]}, {color[1]}, {color[2]}")

    def pick_color(self, color_key, button):

        current_color = self.settings.get(color_key, [255, 255, 255])
        

        qcolor = QtGui.QColor(*current_color)
        

        color = QtWidgets.QColorDialog.getColor(
            qcolor, 
            self, 
            "Выберите цвет",
            options=QtWidgets.QColorDialog.ShowAlphaChannel
        )
        
        if color.isValid():

            self._update_button_color(button, [color.red(), color.green(), color.blue()])
            

            self.settings[color_key] = [color.red(), color.green(), color.blue()]
            save_settings(self.settings)
            
            # Force UI update
            QtWidgets.QApplication.processEvents()

    def create_esp_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        esp_label = QtWidgets.QLabel("Настройки визуалов")
        esp_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(esp_label)
        
        # Initialize color buttons dictionary if it doesn't exist
        if not hasattr(self, 'color_buttons'):
            self.color_buttons = {}
        # --- ESP настройки ---
        self.esp_rendering_cb = QtWidgets.QCheckBox("Включить ESP")
        self.esp_rendering_cb.setChecked(self.settings["esp_rendering"] == 1)
        self.esp_rendering_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.esp_rendering_cb)

        self.esp_mode_cb = QtWidgets.QComboBox()
        self.esp_mode_cb.addItems(["Только враги", "Все игроки"])
        self.esp_mode_cb.setCurrentIndex(self.settings["esp_mode"])
        self.esp_mode_cb.setStyleSheet("background-color: #020203; border-radius: 5px;")
        self.esp_mode_cb.currentIndexChanged.connect(self.save_settings)
        layout.addWidget(self.esp_mode_cb)

        self.line_rendering_cb = QtWidgets.QCheckBox("Линии")
        self.line_rendering_cb.setChecked(self.settings["line_rendering"] == 1)
        self.line_rendering_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.line_rendering_cb)

        self.hp_bar_rendering_cb = QtWidgets.QCheckBox("HP Бар")
        self.hp_bar_rendering_cb.setChecked(self.settings["hp_bar_rendering"] == 1)
        self.hp_bar_rendering_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.hp_bar_rendering_cb)

        self.head_hitbox_rendering_cb = QtWidgets.QCheckBox("Хитбокс головы")
        self.head_hitbox_rendering_cb.setChecked(self.settings["head_hitbox_rendering"] == 1)
        self.head_hitbox_rendering_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.head_hitbox_rendering_cb)

        self.bons_cb = QtWidgets.QCheckBox("Кости")
        self.bons_cb.setChecked(self.settings["bons"] == 1)
        self.bons_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.bons_cb)

        self.nickname_cb = QtWidgets.QCheckBox("Никнейм")
        self.nickname_cb.setChecked(self.settings["nickname"] == 1)
        self.nickname_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.nickname_cb)

        self.weapon_cb = QtWidgets.QCheckBox("Оружие")
        self.weapon_cb.setChecked(self.settings["weapon"] == 1)
        self.weapon_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.weapon_cb)

        self.bomb_esp_cb = QtWidgets.QCheckBox("Бомба ESP")
        self.bomb_esp_cb.setChecked(self.settings["bomb_esp"] == 1)
        self.bomb_esp_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.bomb_esp_cb)

        self.bomb_timer_cb = QtWidgets.QCheckBox("Показывать таймер взрыва бомбы")
        self.bomb_timer_cb.setChecked(self.settings.get("bomb_timer", 1) == 1)
        self.bomb_timer_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.bomb_timer_cb)

        self.defuse_timer_cb = QtWidgets.QCheckBox("Показывать таймер разминирования")
        self.defuse_timer_cb.setChecked(self.settings.get("defuse_timer", 1) == 1)
        self.defuse_timer_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.defuse_timer_cb)

        self.minimap_cb = QtWidgets.QCheckBox("Показывать мини-карту с игроками")
        self.minimap_cb.setChecked(self.settings.get("minimap", 1) == 1)
        self.minimap_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.minimap_cb)

        # Add separator line
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setStyleSheet("background-color: #333;")
        layout.addWidget(separator)

        # Visibility-based colors toggle
        self.visibility_colors_cb = QtWidgets.QCheckBox("Цвет по видимости")
        self.visibility_colors_cb.setChecked(self.settings.get("visibility_colors", 1) == 1)
        self.visibility_colors_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.visibility_colors_cb)

        # Color pickers in a grid layout
        colors_layout = QtWidgets.QGridLayout()
        colors_layout.setSpacing(5)
        colors_layout.setContentsMargins(0, 5, 0, 5)

        # Enemy visible color
        self.enemy_visible_btn = self.create_color_button("enemy_visible_color", "Враг видимый")
        colors_layout.addWidget(QtWidgets.QLabel("Враг видимый:"), 0, 0)
        colors_layout.addWidget(self.enemy_visible_btn, 0, 1)
        self.color_buttons["enemy_visible_color"] = self.enemy_visible_btn
        
        # Enemy hidden color
        self.enemy_hidden_btn = self.create_color_button("enemy_hidden_color", "Враг скрытый")
        colors_layout.addWidget(QtWidgets.QLabel("Враг скрытый:"), 0, 2)
        colors_layout.addWidget(self.enemy_hidden_btn, 0, 3)
        self.color_buttons["enemy_hidden_color"] = self.enemy_hidden_btn
        
        # Friendly visible color
        self.friendly_visible_btn = self.create_color_button("friendly_visible_color", "Союзник видимый")
        colors_layout.addWidget(QtWidgets.QLabel("Союзник видимый:"), 1, 0)
        colors_layout.addWidget(self.friendly_visible_btn, 1, 1)
        self.color_buttons["friendly_visible_color"] = self.friendly_visible_btn
        
        # Friendly hidden color
        self.friendly_hidden_btn = self.create_color_button("friendly_hidden_color", "Союзник скрытый")
        colors_layout.addWidget(QtWidgets.QLabel("Союзник скрытый:"), 1, 2)
        colors_layout.addWidget(self.friendly_hidden_btn, 1, 3)
        self.color_buttons["friendly_hidden_color"] = self.friendly_hidden_btn

        layout.addLayout(colors_layout)
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #080809; border-radius: 10px;")
        return widget

    def create_aim_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)
        aim_label = QtWidgets.QLabel("Настройки аим-бота")
        aim_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(aim_label)
        self.aim_active_cb = QtWidgets.QCheckBox("Включить аим-бот")
        self.aim_active_cb.setChecked(self.settings["aim_active"] == 1)
        self.aim_active_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.aim_active_cb)
        layout.addSpacing(2)
        self.radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radius_slider.setMinimum(0)
        self.radius_slider.setMaximum(100)
        self.radius_slider.setValue(self.settings["radius"])
        self.radius_slider.valueChanged.connect(self.save_settings)
        layout.addWidget(QtWidgets.QLabel("Радиус аима:"))
        layout.addWidget(self.radius_slider)
        layout.addSpacing(2)
        aim_key = self.settings.get("keyboard", {"type": "key", "code": 0x43})
        aim_key_text = self.get_key_text(aim_key)
        self.aim_rebind_btn = QtWidgets.QPushButton(aim_key_text)
        self.aim_rebind_btn.setCheckable(True)
        self.aim_rebind_btn.clicked.connect(lambda: self.start_rebind('aim'))
        layout.addWidget(QtWidgets.QLabel("Клавиша аима:"))
        layout.addWidget(self.aim_rebind_btn)
        self.aim_rebind_btn.setStyleSheet("background-color: #020203; border-radius: 5px; color: white;")
        layout.addSpacing(2)
        self.aim_mode_cb = QtWidgets.QComboBox()
        self.aim_mode_cb.addItems(["Тело", "Голова"])
        self.aim_mode_cb.setCurrentIndex(self.settings["aim_mode"])
        self.aim_mode_cb.setStyleSheet("background-color: #020203; border-radius: 5px;")
        self.aim_mode_cb.currentIndexChanged.connect(self.save_settings)
        layout.addWidget(QtWidgets.QLabel("Режим аима:"))
        layout.addWidget(self.aim_mode_cb)
        layout.addSpacing(2)
        self.aim_mode_distance_cb = QtWidgets.QComboBox()
        self.aim_mode_distance_cb.addItems(["Ближайший к прицелу", "Ближайший в 3D"])
        self.aim_mode_distance_cb.setCurrentIndex(self.settings["aim_mode_distance"])
        self.aim_mode_distance_cb.setStyleSheet("background-color: #020203; border-radius: 5px;")
        self.aim_mode_distance_cb.currentIndexChanged.connect(self.save_settings)
        layout.addWidget(QtWidgets.QLabel("Режим дистанции аима:"))
        layout.addWidget(self.aim_mode_distance_cb)
        layout.addSpacing(2)
        self.smooth_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.smooth_slider.setMinimum(1)
        self.smooth_slider.setMaximum(20)
        self.smooth_slider.setValue(self.settings.get("aim_smooth", 10))
        self.smooth_slider.valueChanged.connect(self.save_settings)
        layout.addWidget(QtWidgets.QLabel("Плавность аима:"))
        layout.addWidget(self.smooth_slider)
        layout.addSpacing(2)
        self.aim_enemies_only_cb = QtWidgets.QCheckBox("Только враги")
        self.aim_enemies_only_cb.setChecked(self.settings.get("aim_enemies_only", 1) == 1)
        self.aim_enemies_only_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.aim_enemies_only_cb)
        # Новый чекбокс для легитного аима
        self.aim_legit_cb = QtWidgets.QCheckBox("Легит аим(Наводится только на видимых игроков)")
        self.aim_legit_cb.setChecked(self.settings.get("aim_legit", 0) == 1)
        self.aim_legit_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.aim_legit_cb)
        layout.addStretch(1)
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #080809; border-radius: 10px;")
        return widget

    def create_trigger_widget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)
        trigger_label = QtWidgets.QLabel("Настройки триггер-бота")
        trigger_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(trigger_label)
        self.trigger_bot_active_cb = QtWidgets.QCheckBox("Включить триггер-бот")
        self.trigger_bot_active_cb.setChecked(self.settings["trigger_bot_active"] == 1)
        self.trigger_bot_active_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.trigger_bot_active_cb)
        layout.addSpacing(2)
        # Новый режим работы триггер-бота
        self.trigger_mode_cb = QtWidgets.QComboBox()
        self.trigger_mode_cb.addItems(["По кнопке", "Автоматически"])
        self.trigger_mode_cb.setCurrentIndex(self.settings.get("trigger_mode", 0))
        self.trigger_mode_cb.currentIndexChanged.connect(self.save_settings)
        layout.addWidget(QtWidgets.QLabel("Режим работы:"))
        layout.addWidget(self.trigger_mode_cb)
        layout.addSpacing(2)
        trigger_key = self.settings.get("keyboards", {"type": "key", "code": 0x58})
        trigger_key_text = self.get_key_text(trigger_key)
        self.trigger_rebind_btn = QtWidgets.QPushButton(trigger_key_text)
        self.trigger_rebind_btn.setCheckable(True)
        self.trigger_rebind_btn.clicked.connect(lambda: self.start_rebind('trigger'))
        layout.addWidget(QtWidgets.QLabel("Клавиша триггера:"))
        layout.addWidget(self.trigger_rebind_btn)
        self.trigger_rebind_btn.setStyleSheet("background-color: #020203; border-radius: 5px; color: white;")
        layout.addSpacing(2)
        self.trigger_enemies_only_cb = QtWidgets.QCheckBox("Только враги")
        self.trigger_enemies_only_cb.setChecked(self.settings.get("trigger_enemies_only", 1) == 1)
        self.trigger_enemies_only_cb.stateChanged.connect(self.save_settings)
        layout.addWidget(self.trigger_enemies_only_cb)
        layout.addStretch(1)
        widget.setLayout(layout)
        widget.setStyleSheet("background-color: #080809; border-radius: 10px;")
        return widget

    def get_key_text(self, vk_code):
        key_names = {
            0x01: "ЛКМ",
            0x02: "ПКМ",
            0x04: "СКМ",
            0x05: "Кнопка 4",
            0x06: "Кнопка 5",
            0x08: "Backspace",
            0x09: "Tab",
            0x0D: "Enter",
            0x10: "Shift",
            0x11: "Ctrl",
            0x12: "Alt",
            0x13: "Pause",
            0x14: "Caps Lock",
            0x1B: "Esc",
            0x20: "Пробел",
            0x21: "Page Up",
            0x22: "Page Down",
            0x23: "End",
            0x24: "Home",
            0x25: "←",
            0x26: "↑",
            0x27: "→",
            0x28: "↓",
            0x29: "Select",
            0x2C: "Print Screen",
            0x2D: "Insert",
            0x2E: "Delete",
            0x30: "0", 0x31: "1", 0x32: "2", 0x33: "3", 0x34: "4",
            0x35: "5", 0x36: "6", 0x37: "7", 0x38: "8", 0x39: "9",
            0x41: "A", 0x42: "B", 0x43: "C", 0x44: "D", 0x45: "E",
            0x46: "F", 0x47: "G", 0x48: "H", 0x49: "I", 0x4A: "J",
            0x4B: "K", 0x4C: "L", 0x4D: "M", 0x4E: "N", 0x4F: "O",
            0x50: "P", 0x51: "Q", 0x52: "R", 0x53: "S", 0x54: "T",
            0x55: "U", 0x56: "V", 0x57: "W", 0x58: "X", 0x59: "Y", 0x5A: "Z",
            0x60: "Numpad 0", 0x61: "Numpad 1", 0x62: "Numpad 2", 0x63: "Numpad 3",
            0x64: "Numpad 4", 0x65: "Numpad 5", 0x66: "Numpad 6", 0x67: "Numpad 7",
            0x68: "Numpad 8", 0x69: "Numpad 9",
            0x6A: "Numpad *", 0x6B: "Numpad +", 0x6D: "Numpad -", 
            0x6E: "Numpad .", 0x6F: "Numpad /",
            0x70: "F1", 0x71: "F2", 0x72: "F3", 0x73: "F4", 0x74: "F5", 0x75: "F6",
            0x76: "F7", 0x77: "F8", 0x78: "F9", 0x79: "F10", 0x7A: "F11", 0x7B: "F12",
            0x90: "Num Lock", 0x91: "Scroll Lock",
            0xA0: "LShift", 0xA1: "RShift", 0xA2: "LCtrl", 0xA3: "RCtrl",
            0xA4: "LAlt", 0xA5: "RAlt",
            0xBA: ";", 0xBB: "=", 0xBC: ",", 0xBD: "-", 0xBE: ".", 0xBF: "/",
            0xC0: "`", 0xDB: "[", 0xDC: "\\", 0xDD: "]", 0xDE: "'", 0xE2: "\\",
            0x1A: "[", 0x1B: "]", 0x27: ";", 0x28: "'", 0x29: "`", 0x2B: "\\",
            0x33: ",", 0x34: ".", 0x35: "/"
        }
        return key_names.get(vk_code, f"0x{vk_code:02X}")

    def _finish_rebind(self):
        """Завершает процесс ребинда и сохраняет настройки"""
        if hasattr(self, 'rebind_label'):
            self.rebind_label.deleteLater()
            del self.rebind_label
            
        self.releaseKeyboard()
        self.releaseMouse()
        
        # Сбрасываем состояние кнопки ребинда
        if hasattr(self, 'current_rebind_btn'):
            self.current_rebind_btn.setChecked(False)
            del self.current_rebind_btn
        
        # Сбрасываем режим ребинда
        if hasattr(self, 'rebind_mode'):
            del self.rebind_mode
            
        self.save_settings()
        self.setFocus()

    def start_rebind(self, mode):
        self.rebind_mode = mode
        
        if mode == 'aim':
            self.aim_rebind_btn.setText("Нажмите клавишу...")
            self.aim_rebind_btn.setChecked(True)
            self.current_rebind_btn = self.aim_rebind_btn
        elif mode == 'trigger':
            self.trigger_rebind_btn.setText("Нажмите клавишу...")
            self.trigger_rebind_btn.setChecked(True)
            self.current_rebind_btn = self.trigger_rebind_btn
        elif mode == 'bunny_hop':
            self.bunny_hop_key_btn.setText("Нажмите клавишу...")
            self.bunny_hop_key_btn.setChecked(True)
            self.current_rebind_btn = self.bunny_hop_key_btn
            
        self.grabKeyboard()
        self.grabMouse()
        self.setFocus()

    def keyPressEvent(self, event):
        if hasattr(self, 'rebind_mode') and self.rebind_mode:
            event.accept()  # Принимаем событие, чтобы не обрабатывалось дальше
            
            if event.key() == QtCore.Qt.Key_Escape:
                self._finish_rebind()
                return
            
            if event.key() == QtCore.Qt.Key_unknown:
                return
                
            # Обрабатываем нажатие клавиши
            if event.key() == QtCore.Qt.Key_Space:
                vk_code = 0x20
                keytext = "Пробел"
            else:
                vk_code = self.qt_to_vk.get(event.key(), event.key())
                keytext = self.get_key_text(vk_code)
            
            if vk_code is not None and keytext:
                if self.rebind_mode == 'aim':
                    self.aim_bot.set_key(vk_code)
                    self.settings["keyboard"] = {"type": "key", "code": vk_code}
                    self.aim_rebind_btn.setText(keytext)
                    print(f"[Aim] Клавиша переназначена на: {keytext} (код: {hex(vk_code)})")
                elif self.rebind_mode == 'trigger':
                    self.trigger_bot.set_key(vk_code)
                    self.settings["keyboards"] = {"type": "key", "code": vk_code}
                    self.trigger_rebind_btn.setText(keytext)
                    print(f"[Trigger] Клавиша переназначена на: {keytext} (код: {hex(vk_code)})")
                elif self.rebind_mode == 'bunny_hop':
                    self.settings["bunny_hop_key"] = vk_code
                    self.bunny_hop_key_btn.setText(keytext)
                    print(f"[Bunny Hop] Клавиша переназначена на: {keytext} (код: {hex(vk_code)})")
                
                self._finish_rebind()
                return
        
        super().keyPressEvent(event)  # Пропускаем событие дальше, если это не ребинд
        
    def mousePressEvent(self, event):
        if hasattr(self, 'rebind_mode') and self.rebind_mode:
            # Обработка кнопок мыши
            button = event.button()
            mouse_buttons = {
                QtCore.Qt.LeftButton: 0x01,    # VK_LBUTTON
                QtCore.Qt.RightButton: 0x02,   # VK_RBUTTON
                QtCore.Qt.MiddleButton: 0x04,  # VK_MBUTTON
                QtCore.Qt.BackButton: 0x05,    # VK_XBUTTON1
                QtCore.Qt.ForwardButton: 0x06  # VK_XBUTTON2
            }
            
            if button in mouse_buttons:
                vk_code = mouse_buttons[button]
                keytext = self.get_key_text(vk_code)
                
                if self.rebind_mode == 'aim':
                    self.aim_bot.set_key(vk_code)
                    self.settings["keyboard"] = vk_code
                    self.aim_rebind_btn.setText(keytext)
                elif self.rebind_mode == 'trigger':
                    self.trigger_bot.set_key(vk_code)
                    self.settings["keyboards"] = vk_code
                    self.trigger_rebind_btn.setText(keytext)
                elif self.rebind_mode == 'bunny_hop':
                    self.settings["bunny_hop_key"] = vk_code
                    self.bunny_hop_key_btn.setText(keytext)  # Убираем префикс "Клавиша: "
                
                self._finish_rebind()
                event.accept()
                return
            
            # Обработка перетаскивания окна
            if event.button() == QtCore.Qt.LeftButton:
                self.is_dragging = True
                self.drag_start_position = event.globalPosition().toPoint()
                
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if hasattr(self, 'is_dragging') and self.is_dragging:
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False

    def save_settings(self):
        # Не сохраняем настройки, если идёт массовое обновление
        if getattr(self, 'massive_update', False):
            return
        self.settings["esp_rendering"] = 1 if self.esp_rendering_cb.isChecked() else 0
        self.settings["esp_mode"] = self.esp_mode_cb.currentIndex()
        self.settings["line_rendering"] = 1 if self.line_rendering_cb.isChecked() else 0
        self.settings["hp_bar_rendering"] = 1 if self.hp_bar_rendering_cb.isChecked() else 0
        self.settings["head_hitbox_rendering"] = 1 if self.head_hitbox_rendering_cb.isChecked() else 0
        self.settings["bons"] = 1 if self.bons_cb.isChecked() else 0
        self.settings["nickname"] = 1 if self.nickname_cb.isChecked() else 0
        self.settings["weapon"] = 1 if self.weapon_cb.isChecked() else 0
        self.settings["bomb_esp"] = 1 if self.bomb_esp_cb.isChecked() else 0
        self.settings["aim_active"] = 1 if self.aim_active_cb.isChecked() else 0
        self.settings["radius"] = self.radius_slider.value()
        self.settings["aim_mode"] = self.aim_mode_cb.currentIndex()
        self.settings["aim_mode_distance"] = self.aim_mode_distance_cb.currentIndex()
        self.settings["aim_smooth"] = self.smooth_slider.value()
        self.settings["trigger_bot_active"] = 1 if self.trigger_bot_active_cb.isChecked() else 0
        self.settings["trigger_enemies_only"] = 1 if self.trigger_enemies_only_cb.isChecked() else 0
        self.settings["trigger_mode"] = self.trigger_mode_cb.currentIndex() if hasattr(self, 'trigger_mode_cb') else self.settings.get("trigger_mode", 0)
        self.settings["aim_enemies_only"] = 1 if self.aim_enemies_only_cb.isChecked() else 0
        self.settings["aim_legit"] = 1 if hasattr(self, 'aim_legit_cb') and self.aim_legit_cb.isChecked() else 0
        self.settings["bomb_timer"] = 1 if self.bomb_timer_cb.isChecked() else 0
        self.settings["defuse_timer"] = 1 if self.defuse_timer_cb.isChecked() else 0
        self.settings["minimap"] = 1 if self.minimap_cb.isChecked() else 0
        self.settings["sniper_crosshair"] = 1 if hasattr(self, 'sniper_crosshair_cb') and self.sniper_crosshair_cb.isChecked() else 0
        self.settings["visibility_colors"] = 1 if hasattr(self, 'visibility_colors_cb') and self.visibility_colors_cb.isChecked() else 0
        save_settings(self.settings)

def configurator():
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_purple.xml')
    window = ConfigWindow()
    window.show()

    from pynput import keyboard

    def on_press(key):
        try:
            if key == keyboard.Key.insert or key == keyboard.Key.delete:
                if window.isVisible():
                    window.hide()
                else:
                    window.show()
                    window.raise_()
                    window.activateWindow()
        except Exception:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()

    sys.exit(app.exec())

# ESP
class ESPWindow(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle('ESP Overlay')
        self.window_width, self.window_height = get_window_size("Counter-Strike 2")
        if self.window_width is None or self.window_height is None:
            print("Ошибка: окно игры не найдено.")
            sys.exit(1)
        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        hwnd = self.winId()
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        self.file_watcher = QFileSystemWatcher([CONFIG_FILE])
        self.file_watcher.fileChanged.connect(self.reload_settings)

        self.offsets, self.client_dll = get_offsets_and_client_dll()
        self.pm = pymem.Pymem("cs2.exe")
        self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll").lpBaseOfDll

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, self.window_width, self.window_height)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing, False)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: transparent;")
        self.view.setSceneRect(0, 0, self.window_width, self.window_height)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(0)

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

    def reload_settings(self):
        self.settings = load_settings()
        self.window_width, self.window_height = get_window_size("Counter-Strike 2")
        if self.window_width is None or self.window_height is None:
            print("Ошибка: окно игры не найдено.")
            sys.exit(1)
        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.update_scene()

    def update_scene(self):
        if not self.is_game_window_active():
            self.scene.clear()
            return

        self.scene.clear()
        try:
            esp(self.scene, self.pm, self.client, self.offsets, self.client_dll, self.window_width, self.window_height, self.settings)
            current_time = time.time()
            self.frame_count += 1
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
            fps_text = self.scene.addText(f"Mortal cheat | FPS: {self.fps}", QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold))
            fps_text.setPos(5, 5)
            fps_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))
        except Exception:
            # Не выводим ошибку, просто ничего не рисуем
            pass

    def is_game_window_active(self):
        hwnd = win32gui.FindWindow(None, "Counter-Strike 2")
        if hwnd:
            foreground_hwnd = win32gui.GetForegroundWindow()
            return hwnd == foreground_hwnd
        return False

def get_local_player_weapon(pm, client, client_dll, offsets):
    try:
        dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
        m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
        m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
        m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
        m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
        
        local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
        if not local_player_pawn_addr or local_player_pawn_addr < 0x10000:
            return None
            
        weapon_pointer = pm.read_longlong(local_player_pawn_addr + m_pClippingWeapon)
        if not weapon_pointer or weapon_pointer < 0x10000:
            return None
            
        weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
        weapon_name = get_weapon_name_by_index(weapon_index)
        return weapon_name
    except Exception as e:
        print(f"Error getting local player weapon: {e}")
        return None

def draw_crosshair(scene, window_width, window_height, color=QtGui.QColor(255, 0, 0), size=8, thickness=2):
    """Draw a simple crosshair in the center of the screen"""
    center_x = window_width // 2
    center_y = window_height // 2
    
    # Horizontal line
    scene.addLine(center_x - size, center_y, center_x + size, center_y, 
                 QtGui.QPen(color, thickness, QtCore.Qt.SolidLine))
    # Vertical line
    scene.addLine(center_x, center_y - size, center_x, center_y + size, 
                 QtGui.QPen(color, thickness, QtCore.Qt.SolidLine))

def is_sniper_rifle(weapon_name):
    """Check if the weapon is a sniper rifle without built-in crosshair"""
    if not weapon_name:
        return False
    sniper_rifles = ["AWP", "SSG 08", "SCAR-20", "G3SG1"]
    return weapon_name in sniper_rifles

def esp(scene, pm, client, offsets, client_dll, window_width, window_height, settings):
    if settings.get('esp_rendering', 1) == 0:
        return
    
    # Get current weapon and draw crosshair if enabled and using a sniper
    if settings.get('sniper_crosshair', 1) == 1:
        try:
            weapon = get_local_player_weapon(pm, client, client_dll, offsets)
            if weapon and is_sniper_rifle(weapon):
                draw_crosshair(scene, window_width, window_height)
                
            # Debug: Print local player's weapon (once per second)
            if 'last_weapon_print' not in esp.__dict__:
                esp.last_weapon_print = 0
            
            current_time = time.time()
            if current_time - esp.last_weapon_print > 1.0:  # Update every 1 second
                if weapon:
                    print(f"Current weapon: {weapon}")
                esp.last_weapon_print = current_time
                
        except Exception as e:
            print(f"Error in crosshair: {e}")

    player_points = []
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    dwViewMatrix = offsets['client.dll']['dwViewMatrix']
    dwPlantedC4 = offsets['client.dll']['dwPlantedC4']
    
    # Get weapon names for debugging
    m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
    m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
    m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
    m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
    m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
    m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
    m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
    m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
    m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
    m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
    m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
    m_flTimerLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flTimerLength']
    m_flDefuseLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flDefuseLength']
    m_bBeingDefused = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBeingDefused']

    view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]

    local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    if not local_player_pawn_addr or local_player_pawn_addr < 0x10000:
        return
    try:
        local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
    except Exception:
        return

    no_center_x = window_width / 2
    no_center_y = window_height * 0.9
    entity_list = pm.read_longlong(client + dwEntityList)
    if not entity_list or entity_list < 0x10000:
        return
    entity_ptr = pm.read_longlong(entity_list + 0x10)
    if not entity_ptr or entity_ptr < 0x10000:
        return

    def bombisplant():
        global BombPlantedTime
        bombisplant = pm.read_bool(client + dwPlantedC4 - 0x8)
        if bombisplant:
            if (BombPlantedTime == 0):
                BombPlantedTime = time.time()
        else:
            BombPlantedTime = 0
        return bombisplant
    
    def getC4BaseClass():
        plantedc4 = pm.read_longlong(client + dwPlantedC4)
        plantedc4class = pm.read_longlong(plantedc4)
        return plantedc4class
    
    def getPositionWTS():
        c4node = pm.read_longlong(getC4BaseClass() + m_pGameSceneNode)
        c4posX = pm.read_float(c4node + m_vecAbsOrigin)
        c4posY = pm.read_float(c4node + m_vecAbsOrigin + 0x4)
        c4posZ = pm.read_float(c4node + m_vecAbsOrigin + 0x8)
        bomb_pos = w2s(view_matrix, c4posX, c4posY, c4posZ, window_width, window_height)
        return bomb_pos
    
    def getBombTime():
        BombTime = pm.read_float(getC4BaseClass() + m_flTimerLength) - (time.time() - BombPlantedTime)
        return BombTime if (BombTime >= 0) else 0
    
    def isBeingDefused():
        global BombDefusedTime
        BombIsDefused = pm.read_bool(getC4BaseClass() + m_bBeingDefused)
        if (BombIsDefused):
            if (BombDefusedTime == 0):
                BombDefusedTime = time.time() 
        else:
            BombDefusedTime = 0
        return BombIsDefused
    
    def getDefuseTime():
        DefuseTime = pm.read_float(getC4BaseClass() + m_flDefuseLength) - (time.time() - BombDefusedTime)
        return DefuseTime if (isBeingDefused() and DefuseTime >= 0) else 0

    bfont = QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold)

    if settings.get('bomb_esp', 0) == 1:
        if bombisplant():
            BombPosition = getPositionWTS()
            BombTime = getBombTime()
            DefuseTime = getDefuseTime()
        
            if (BombPosition[0] > 0 and BombPosition[1] > 0):
                if DefuseTime > 0:
                    c4_name_text = scene.addText(f'BOMB {round(BombTime, 2)} | DIF {round(DefuseTime, 2)}', bfont)
                else:
                    c4_name_text = scene.addText(f'BOMB {round(BombTime, 2)}', bfont)
                c4_name_x = BombPosition[0]
                c4_name_y = BombPosition[1]
                c4_name_text.setPos(c4_name_x, c4_name_y)
                c4_name_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))

    if settings.get('bomb_timer', 1) == 1 and bombisplant():
        BombTime = getBombTime()
        timer_text = scene.addText(f"До взрыва: {round(BombTime, 1)}", QtGui.QFont('DejaVu Sans', 18, QtGui.QFont.Bold))
        timer_text.setPos(window_width/2-80, 40)
        timer_text.setDefaultTextColor(QtGui.QColor(255, 80, 80))

    if settings.get('defuse_timer', 1) == 1 and bombisplant() and isBeingDefused():
        DefuseTime = getDefuseTime()
        # Показываем только если время разминирования в разумных пределах
        if 0 < DefuseTime < 20:
            defuse_text = scene.addText(f"До конца разминирования: {round(DefuseTime, 1)}", QtGui.QFont('DejaVu Sans', 18, QtGui.QFont.Bold))
            defuse_text.setPos(window_width/2-120, 70)
            defuse_text.setDefaultTextColor(QtGui.QColor(80, 180, 255))
        try:
            m_angEyeAngles = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_angEyeAngles']
            local_yaw = pm.read_float(local_player_pawn_addr + m_angEyeAngles + 0x4)  # <-- используем yaw, а не pitch
        except:
            local_yaw = 0.0
        import math
        rad = -math.radians(local_yaw)
        cos_yaw = math.cos(rad)
        sin_yaw = math.sin(rad)
        for px, py, team, addr in player_points:
            dx = (px - local_x) / scale
            dy = (py - local_y) / scale
            # Поворачиваем так, чтобы вперёд было вверх
            rot_x = dx * sin_yaw + dy * cos_yaw
            rot_y = -dx * cos_yaw + dy * sin_yaw
            dot_x = map_x + map_size/2 + rot_x
            dot_y = map_y + map_size/2 + rot_y
            color = QtGui.QColor(80,180,255) if team == local_player_team else QtGui.QColor(255,80,80)
            if addr == local_player_pawn_addr:
                color = QtGui.QColor(255,255,255)
            if (map_x <= dot_x <= map_x + map_size) and (map_y <= dot_y <= map_y + map_size):
                scene.addEllipse(dot_x-4, dot_y-4, 8, 8, QtGui.QPen(QtCore.Qt.NoPen), color)

    # --- Мини-карта с учётом yaw ---
    if settings.get('minimap', 1) == 1:
        map_size = 200
        map_x = window_width - map_size - 20
        map_y = 20
        player_points = []
        for i in range(1, 64):
            try:
                if entity_ptr == 0:
                    break
                entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
                if entity_controller == 0:
                    continue
                entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
                if entity_controller_pawn == 0:
                    continue
                entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
                if entity_list_pawn == 0:
                    continue
                entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
                if entity_pawn_addr == 0:
                    continue
                entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
                entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
                if entity_alive != 256:
                    continue  # Только живые!
                node = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                pos_x = pm.read_float(node + m_vecAbsOrigin)
                pos_y = pm.read_float(node + m_vecAbsOrigin + 0x4)
                player_points.append((pos_x, pos_y, entity_team, entity_pawn_addr))
            except: continue
        local_node = pm.read_longlong(local_player_pawn_addr + m_pGameSceneNode)
        local_x = pm.read_float(local_node + m_vecAbsOrigin)
        local_y = pm.read_float(local_node + m_vecAbsOrigin + 0x4)
        scale = 11.0
        try:
            m_angEyeAngles = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_angEyeAngles']
            local_yaw = pm.read_float(local_player_pawn_addr + m_angEyeAngles + 0x4)  # <-- используем yaw, а не pitch
        except:
            local_yaw = 0.0
        import math
        rad = -math.radians(local_yaw)
        cos_yaw = math.cos(rad)
        sin_yaw = math.sin(rad)
        minimap = scene.addRect(map_x, map_y, map_size, map_size, QtGui.QPen(QtGui.QColor(80, 80, 80)), QtGui.QColor(20, 20, 20, 180))
        for px, py, team, addr in player_points:
            dx = (px - local_x) / scale
            dy = (py - local_y) / scale
            # Поворачиваем так, чтобы вперёд было вверх
            rot_x = -(dx * sin_yaw + dy * cos_yaw)
            rot_y = -dx * cos_yaw + dy * sin_yaw
            dot_x = map_x + map_size/2 + rot_x
            dot_y = map_y + map_size/2 + rot_y
            color = QtGui.QColor(80, 180, 255) if team == local_player_team else QtGui.QColor(255, 80, 80)
            if addr == local_player_pawn_addr:
                color = QtGui.QColor(255, 255, 255)
            if (map_x <= dot_x <= map_x + map_size) and (map_y <= dot_y <= map_y + map_size):
                scene.addEllipse(dot_x-4, dot_y-4, 8, 8, QtGui.QPen(QtCore.Qt.NoPen), color)
        # Рисуем стрелку направления в центре мини-карты
        center_x = map_x + map_size/2
        center_y = map_y + map_size/2
        arrow = scene.addPolygon(
            QtGui.QPolygonF([
                QtCore.QPointF(center_x, center_y-12),
                QtCore.QPointF(center_x-6, center_y+8),
                QtCore.QPointF(center_x+6, center_y+8)
            ]),
            QtGui.QPen(QtCore.Qt.NoPen),
            QtGui.QColor(255, 255, 255)
        )

    for i in range(1, 64):
        try:
            if entity_ptr == 0:
                print(f"entity_ptr is 0 at i={i}")
                continue

            entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
            #print(f"entity_controller[{i}]: {hex(entity_controller) if entity_controller else entity_controller}")
            if entity_controller == 0:
                continue

            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            #print(f"entity_controller_pawn[{i}]: {hex(entity_controller_pawn) if entity_controller_pawn else entity_controller_pawn}")
            if entity_controller_pawn == 0:
                continue

            entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
           # print(f"entity_list_pawn[{i}]: {hex(entity_list_pawn) if entity_list_pawn else entity_list_pawn}")
            if entity_list_pawn == 0:
                continue

            entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
           # print(f"entity_pawn_addr[{i}]: {hex(entity_pawn_addr) if entity_pawn_addr else entity_pawn_addr}")
            if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                continue

            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
            if entity_team == local_player_team and settings['esp_mode'] == 0:
                continue

            entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
            armor_hp = pm.read_int(entity_pawn_addr + m_ArmorValue)
            if entity_hp <= 0:
                continue

            entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
            if entity_alive != 256:
                continue

            weapon_pointer = pm.read_longlong(entity_pawn_addr + m_pClippingWeapon)
            weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
            weapon_name = get_weapon_name_by_index(weapon_index)

            # Check if player is visible
            is_player_visible = is_visible(pm, local_player_pawn_addr, entity_pawn_addr, client_dll)
            
            # Set color based on team and visibility settings
            if settings.get('visibility_colors', 1) == 1:
                # Use visibility-based colors
                if entity_team == local_player_team:
                    # Friendly team
                    if is_player_visible:
                        color = QtGui.QColor(*settings.get('friendly_visible_color', [71, 167, 106]))
                    else:
                        color = QtGui.QColor(*settings.get('friendly_hidden_color', [100, 100, 255]))
                else:
                    # Enemy team
                    if is_player_visible:
                        color = QtGui.QColor(*settings.get('enemy_visible_color', [255, 0, 0]))
                    else:
                        color = QtGui.QColor(*settings.get('enemy_hidden_color', [255, 100, 100]))
            else:
                # Use simple team-based colors (no visibility)
                if entity_team == local_player_team:
                    color = QtGui.QColor(*settings.get('friendly_visible_color', [71, 167, 106]))
                else:
                    color = QtGui.QColor(*settings.get('enemy_visible_color', [255, 0, 0]))
            
            game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)

            headX = pm.read_float(bone_matrix + 6 * 0x20)
            headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
            headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
            head_pos = w2s(view_matrix, headX, headY, headZ, window_width, window_height)
            if head_pos[1] < 0:
                continue
            if settings['line_rendering'] == 1:
                legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)
                bottom_center_x = window_width // 2
                bottom_center_y = window_height - 1
                scene.addLine(bottom_center_x, bottom_center_y, leg_pos[0], leg_pos[1], QtGui.QPen(color, 1))
                
            legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
            leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)
            deltaZ = abs(head_pos[1] - leg_pos[1])
            leftX = head_pos[0] - deltaZ // 4
            rightX = head_pos[0] + deltaZ // 4
            rect = scene.addRect(QtCore.QRectF(leftX, head_pos[1], rightX - leftX, leg_pos[1] - head_pos[1]), QtGui.QPen(color, 1), QtCore.Qt.NoBrush)

            if settings['hp_bar_rendering'] == 1:
                max_hp = 100
                hp_percentage = min(1.0, max(0.0, entity_hp / max_hp))
                hp_bar_width = 3
                hp_bar_height = deltaZ
                hp_bar_x_left = leftX - hp_bar_width - 6
                hp_bar_y_top = head_pos[1]
                hp_bar_outline = scene.addRect(QtCore.QRectF(hp_bar_x_left-1, hp_bar_y_top-1, hp_bar_width+2, hp_bar_height+2), QtGui.QPen(QtGui.QColor(0,0,0), 2), QtCore.Qt.NoBrush)
                hp_bar = scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_top, hp_bar_width, hp_bar_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(40, 40, 40))
                current_hp_height = hp_bar_height * hp_percentage
                hp_bar_y_bottom = hp_bar_y_top + hp_bar_height - current_hp_height
                hp_bar_current = scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_bottom, hp_bar_width, current_hp_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(255, 0, 0))
                max_armor_hp = 100
                armor_hp_percentage = min(1.0, max(0.0, armor_hp / max_armor_hp))
                armor_bar_width = 3
                armor_bar_height = deltaZ
                armor_bar_x_left = hp_bar_x_left - armor_bar_width - 4
                armor_bar_y_top = head_pos[1]
                armor_bar_outline = scene.addRect(QtCore.QRectF(armor_bar_x_left-1, armor_bar_y_top-1, armor_bar_width+2, armor_bar_height+2), QtGui.QPen(QtGui.QColor(0,0,0), 2), QtCore.Qt.NoBrush)
                armor_bar = scene.addRect(QtCore.QRectF(armor_bar_x_left, hp_bar_y_top, armor_bar_width, armor_bar_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(40, 40, 40))
                current_armor_height = armor_bar_height * armor_hp_percentage
                armor_bar_y_bottom = armor_bar_y_top + armor_bar_height - current_armor_height
                armor_bar_current = scene.addRect(QtCore.QRectF(armor_bar_x_left, armor_bar_y_bottom, armor_bar_width, current_armor_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(62, 95, 138))

            if settings['head_hitbox_rendering'] == 1:
                head_hitbox_size = (rightX - leftX) / 5
                head_hitbox_radius = head_hitbox_size * 2 ** 0.5 / 2
                head_hitbox_x = leftX + 2.5 * head_hitbox_size
                head_hitbox_y = head_pos[1] + deltaZ / 9
                ellipse = scene.addEllipse(QtCore.QRectF(head_hitbox_x - head_hitbox_radius, head_hitbox_y - head_hitbox_radius, head_hitbox_radius * 2, head_hitbox_radius * 2), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(255, 0, 0, 128))

            if settings.get('bons', 0) == 1:
                # Проверяем валидность bone_matrix перед отрисовкой костей
                if bone_matrix and bone_matrix > 0x10000:
                    draw_bones(scene, pm, bone_matrix, view_matrix, window_width, window_height)

            if settings.get('nickname', 0) == 1:
                player_name = pm.read_string(entity_controller + m_iszPlayerName, 32)
                font_size = max(6, min(18, deltaZ / 25))
                font = QtGui.QFont('DejaVu Sans', font_size, QtGui.QFont.Bold)
                name_text = scene.addText(player_name, font)
                text_rect = name_text.boundingRect()
                name_x = head_pos[0] - text_rect.width() / 2
                name_y = head_pos[1] - text_rect.height()
                name_text.setPos(name_x, name_y)
                name_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))

            if settings.get('weapon', 0) == 1:
                weapon_name_text = scene.addText(weapon_name, font)
                text_rect = weapon_name_text.boundingRect()
                weapon_name_x = head_pos[0] - text_rect.width() / 2
                weapon_name_y = head_pos[1] + deltaZ
                weapon_name_text.setPos(weapon_name_x, weapon_name_y)
                weapon_name_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))

            if 'radius' in settings:
                if settings['radius'] != 0:
                    center_x = window_width / 2
                    center_y = window_height / 2
                    screen_radius = settings['radius'] / 100.0 * min(center_x, center_y)
                    ellipse = scene.addEllipse(QtCore.QRectF(center_x - screen_radius, center_y - screen_radius, screen_radius * 2, screen_radius * 2), QtGui.QPen(QtGui.QColor(255, 255, 255, 16), 0.5), QtCore.Qt.NoBrush)
        except Exception as e:
            print(f"Exception in entity loop i={i}: {e}")
            continue

def get_weapon_name_by_index(index):
    weapon_names = {
    32: "P2000",
    61: "USP-S",
    4: "Glock",
    2: "Dual Berettas",
    36: "P250",
    30: "Tec-9",
    63: "CZ75-Auto",
    1: "Desert Eagle",
    3: "Five-SeveN",
    64: "R8",
    35: "Nova",
    25: "XM1014",
    27: "MAG-7",
    29: "Sawed-Off",
    14: "M249",
    28: "Negev",
    17: "MAC-10",
    23: "MP5-SD",
    24: "UMP-45",
    19: "P90",
    26: "Bizon",
    34: "MP9",
    33: "MP7",
    10: "FAMAS",
    16: "M4A4",
    60: "M4A1-S",
    8: "AUG",
    43: "Galil",
    7: "AK-47",
    39: "SG 553",
    40: "SSG 08",
    9: "AWP",
    38: "SCAR-20",
    11: "G3SG1",
    43: "Flashbang",
    44: "Hegrenade",
    45: "Smoke",
    46: "Molotov",
    47: "Decoy",
    48: "Incgrenage",
    49: "C4",
    31: "Taser",
    42: "Knife",
    41: "Knife Gold",
    59: "Knife",
    80: "Knife Ghost",
    500: "Knife Bayonet",
    505: "Knife Flip",
    506: "Knife Gut",
    507: "Knife Karambit",
    508: "Knife M9",
    509: "Knife Tactica",
    512: "Knife Falchion",
    514: "Knife Survival Bowie",
    515: "Knife Butterfly",
    516: "Knife Rush",
    519: "Knife Ursus",
    520: "Knife Gypsy Jackknife",
    522: "Knife Stiletto",
    523: "Knife Widowmaker"
}
    return weapon_names.get(index, 'Unknown')

def draw_bones(scene, pm, bone_matrix, view_matrix, width, height):
    bone_ids = {
        "head": 6,
        "neck": 5,
        "spine": 4,
        "pelvis": 0,
        "left_shoulder": 13,
        "left_elbow": 14,
        "left_wrist": 15,
        "right_shoulder": 9,
        "right_elbow": 10,
        "right_wrist": 11,
        "left_hip": 25,
        "left_knee": 26,
        "left_ankle": 27,
        "right_hip": 22,
        "right_knee": 23,
        "right_ankle": 24,
    }
    bone_connections = [
        ("head", "neck"),
        ("neck", "spine"),
        ("spine", "pelvis"),
        ("pelvis", "left_hip"),
        ("left_hip", "left_knee"),
        ("left_knee", "left_ankle"),
        ("pelvis", "right_hip"),
        ("right_hip", "right_knee"),
        ("right_knee", "right_ankle"),
        ("neck", "left_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("left_elbow", "left_wrist"),
        ("neck", "right_shoulder"),
        ("right_shoulder", "right_elbow"),
        ("right_elbow", "right_wrist"),
    ]
    bone_positions = {}
    bone_world = {}
    def is_valid_screen_point(p, width, height):
        return p != [-999, -999] and 0 <= p[0] <= width and 0 <= p[1] <= height
    try:
        for bone_name, bone_id in bone_ids.items():
            boneX = pm.read_float(bone_matrix + bone_id * 0x20)
            boneY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
            boneZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
            bone_world[bone_name] = (boneX, boneY, boneZ)
            bone_pos = w2s(view_matrix, boneX, boneY, boneZ, width, height)
            if is_valid_screen_point(bone_pos, width, height):
                bone_positions[bone_name] = bone_pos
        for connection in bone_connections:
            if connection[0] in bone_positions and connection[1] in bone_positions:
                w1 = bone_world[connection[0]]
                w2 = bone_world[connection[1]]
                # Проверка на мусорные world-координаты и адекватную длину кости
                if (
                    all(abs(x) > 0.01 and abs(x) < 10000 for x in w1+w2) and
                    ((w1[0]-w2[0])**2 + (w1[1]-w2[1])**2 + (w1[2]-w2[2])**2)**0.5 < 120
                ):
                    p1 = bone_positions[connection[0]]
                    p2 = bone_positions[connection[1]]
                    scene.addLine(
                        p1[0], p1[1],
                        p2[0], p2[1],
                        QtGui.QPen(QtGui.QColor(255, 255, 255, 128), 1)
                    )
    except Exception:
        pass

def draw_minimap(scene, pm, client, offsets, client_dll, local_player_pawn_addr, local_yaw, window_width, window_height, settings):
    minimap_size = 200
    margin = 20
    map_center_x = window_width - minimap_size // 2 - margin
    map_center_y = window_height - minimap_size // 2 - margin
    radius_world = 1000.0
    scene.addRect(map_center_x - minimap_size//2, map_center_y - minimap_size//2, minimap_size, minimap_size,
                  QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(20, 20, 20, 180))
    scene.addEllipse(map_center_x - minimap_size//2, map_center_y - minimap_size//2, minimap_size, minimap_size,
                    QtGui.QPen(QtGui.QColor(120,120,120,180), 1))
    scene.addEllipse(map_center_x-4, map_center_y-4, 8, 8, QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(0,255,0,255))
    arrow_len = 20
    import math
    arrow_x = map_center_x + arrow_len * math.sin(math.radians(local_yaw))
    arrow_y = map_center_y - arrow_len * math.cos(math.radians(local_yaw))
    scene.addLine(map_center_x, map_center_y, arrow_x, arrow_y, QtGui.QPen(QtGui.QColor(0,255,0,200), 2))
    dwEntityList = offsets['client.dll']['dwEntityList']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
    m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
    entity_list = pm.read_longlong(client + dwEntityList)
    entity_ptr = pm.read_longlong(entity_list + 0x10)
    local_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
    local_scene = pm.read_longlong(local_player_pawn_addr + m_pGameSceneNode)
    local_x = pm.read_float(local_scene + m_vecAbsOrigin)
    local_y = pm.read_float(local_scene + m_vecAbsOrigin + 0x4)
    for i in range(1, 64):
        try:
            entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
            if entity_controller == 0:
                continue
            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            if entity_controller_pawn == 0 or entity_controller_pawn == local_player_pawn_addr:
                continue
            entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
            if entity_list_pawn == 0:
                continue
            entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
            if entity_pawn_addr == 0:
                continue
            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
            entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
            if entity_alive != 256:
                continue
            entity_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
            ent_x = pm.read_float(entity_scene + m_vecAbsOrigin)
            ent_y = pm.read_float(entity_scene + m_vecAbsOrigin + 0x4)
            dx = ent_x - local_x
            dy = ent_y - local_y
            angle = math.radians(local_yaw)
            rel_x =  dx * math.cos(angle) + dy * math.sin(angle)
            rel_y = -dx * math.sin(angle) + dy * math.cos(angle)
            map_x = map_center_x + (rel_x / radius_world) * (minimap_size/2-10)
            map_y = map_center_y - (rel_y / radius_world) * (minimap_size/2-10)
            if entity_team == local_team:
                color = QtGui.QColor(0, 128, 255, 200)
            else:
                color = QtGui.QColor(255, 0, 0, 200)
            scene.addEllipse(map_x-3, map_y-3, 6, 6, QtGui.QPen(QtCore.Qt.NoPen), color)
        except Exception:
            continue

def esp_main():
    settings = load_settings()
    app = QtWidgets.QApplication(sys.argv)
    window = ESPWindow(settings)
    window.show()
    sys.exit(app.exec())

# Trigger Bot
def triggerbot():
    offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
    client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    mouse = Controller()
    default_settings = {
        "keyboards": "X",
        "trigger_bot_active": 1,
        "esp_mode": 1
    }

    def load_settings():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return default_settings

    def is_key_pressed(key_vk):
        if isinstance(key_vk, int):
            return win32api.GetAsyncKeyState(key_vk) & 0x8000
        return False

    def main(settings):
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        while True:
            try:
                trigger_bot_active = settings["trigger_bot_active"]
                trigger_mode = settings.get("trigger_mode", 0)
                keyboards = settings.get("keyboards", {"type": "key", "code": 0x58})
                if trigger_bot_active == 1:
                    if trigger_mode == 1:  # Автоматический режим
                        try:
                            player = pm.read_longlong(client + dwLocalPlayerPawn)
                            entityId = pm.read_int(player + m_iIDEntIndex)
                            if entityId > 0:
                                entList = pm.read_longlong(client + dwEntityList)
                                entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                                entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))
                                entityTeam = pm.read_int(entity + m_iTeamNum)
                                playerTeam = pm.read_int(player + m_iTeamNum)
                                if settings.get('trigger_enemies_only', 1) == 1:
                                    if entityTeam == playerTeam:
                                        continue
                                entityHp = pm.read_int(entity + m_iHealth)
                                if entityHp > 0:
                                    mouse.press(Button.left)
                                    time.sleep(0.03)
                                    mouse.release(Button.left)
                        except Exception:
                            pass
                        time.sleep(0.03)
                    else:  # По кнопке
                        if is_key_pressed(keyboards):
                            try:
                                player = pm.read_longlong(client + dwLocalPlayerPawn)
                                entityId = pm.read_int(player + m_iIDEntIndex)
                                if entityId > 0:
                                    entList = pm.read_longlong(client + dwEntityList)
                                    entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                                    entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))
                                    entityTeam = pm.read_int(entity + m_iTeamNum)
                                    playerTeam = pm.read_int(player + m_iTeamNum)
                                    if settings.get('trigger_enemies_only', 1) == 1:
                                        if entityTeam == playerTeam:
                                            continue
                                    entityHp = pm.read_int(entity + m_iHealth)
                                    if entityHp > 0:
                                        mouse.press(Button.left)
                                        time.sleep(0.03)
                                        mouse.release(Button.left)
                            except Exception:
                                pass
                            time.sleep(0.03)
                        else:
                            time.sleep(0.1)
                else:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(1)

    def start_main_thread(settings):
        while True:
            main(settings)

    def setup_watcher(app, settings):
        watcher = QFileSystemWatcher()
        watcher.addPath(CONFIG_FILE)
        def reload_settings():
            new_settings = load_settings()
            settings.update(new_settings)
        watcher.fileChanged.connect(reload_settings)
        app.exec()

    def main_program():
        app = QCoreApplication(sys.argv)
        settings = load_settings()
        threading.Thread(target=start_main_thread, args=(settings,), daemon=True).start()
        setup_watcher(app, settings)

    main_program()

# Aim Bot
def aim():
    default_settings = {
        'esp_rendering': 1,
        'esp_mode': 1,
        'keyboard': "C",
        'aim_active': 1,
        'aim_mode': 1,
        'radius': 20,
        'aim_mode_distance': 1,
        'aim_smooth': 10
    }

    def get_window_size(window_name="Counter-Strike 2"):
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd:
            rect = win32gui.GetClientRect(hwnd)
            return rect[2] - rect[0], rect[3] - rect[1]
        return 1920, 1080



    def load_settings():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return default_settings

    def get_offsets_and_client_dll():
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
        return offsets, client_dll

    def esp(pm, client, offsets, client_dll, settings, target_list, window_size):
        width, height = window_size
        if settings['aim_active'] == 0:
            return
        dwEntityList = offsets['client.dll']['dwEntityList']
        dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
        dwViewMatrix = offsets['client.dll']['dwViewMatrix']
        m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
        m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
        m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
        m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
        m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
        view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
        local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
        try:
            local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
        except:
            return
        entity_list = pm.read_longlong(client + dwEntityList)
        entity_ptr = pm.read_longlong(entity_list + 0x10)

        for i in range(1, 64):
            try:
                if entity_ptr == 0:
                    break
    
                entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
                if entity_controller == 0:
                    continue
    
                entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
                if entity_controller_pawn == 0:
                    continue
    
                entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
                if entity_list_pawn == 0:
                    continue
    
                entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
                if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                    continue
    
                entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
                if settings.get('aim_enemies_only', 1) == 1:
                    if entity_team == local_player_team:
                        continue
                entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
                if entity_alive != 256:
                    continue
                game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                try:
                    bone_id = 6 if settings['aim_mode'] == 1 else 4
                   

                    headX = pm.read_float(bone_matrix + bone_id * 0x20)
                    headY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
                    headZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
                    head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
                    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)

                    leg_pos = w2s(view_matrix, headX, headY, legZ, width, height)
                    deltaZ = abs(head_pos[1] - leg_pos[1])
                    if head_pos[0] != -999 and head_pos[1] != -999:
                        # Фильтрация по видимости если включен legit aim
                        if settings.get('aim_legit', 0) == 1:
                        
                            if not is_visible(pm, local_player_pawn_addr, entity_pawn_addr, client_dll):
                               
                                continue
                            else:
                                print("visible")
                        if settings['aim_mode_distance'] == 1:
                            target_list.append({
                                'pos': head_pos,
                                'deltaZ': deltaZ
                            })
                        else:
                            target_list.append({
                                'pos': head_pos,
                                'deltaZ': None
                            })
                except Exception as e:
                    pass
            except:
                return
        return target_list

    def is_key_pressed(key_vk):
        if isinstance(key_vk, int):
            return win32api.GetAsyncKeyState(key_vk) & 0x8000
        return False

    def aimbot(target_list, radius, aim_mode_distance, smooth):
        if not target_list:
            return
        center_x = win32api.GetSystemMetrics(0) // 2
        center_y = win32api.GetSystemMetrics(1) // 2
       
        if radius == 0:
            closest_target = None
            closest_dist = float('inf')
            for target in target_list:
                dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
                if dist < closest_dist:
                    closest_target = target['pos']
                    closest_dist = dist
        else:
            screen_radius = radius / 100.0 * min(center_x, center_y)
            closest_target = None
            closest_dist = float('inf')
            if aim_mode_distance == 1:
                target_with_max_deltaZ = None
                max_deltaZ = -float('inf')
                for target in target_list:
                    dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
                    if dist < screen_radius and target['deltaZ'] > max_deltaZ:
                        max_deltaZ = target['deltaZ']
                        target_with_max_deltaZ = target
                closest_target = target_with_max_deltaZ['pos'] if target_with_max_deltaZ else None
            else:
                for target in target_list:
                    dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
                    if dist < screen_radius and dist < closest_dist:
                        closest_target = target['pos']
                        closest_dist = dist
        if closest_target:
            target_x, target_y = closest_target
            dx = int(target_x - center_x)
            dy = int(target_y - center_y)
            dx = int(dx / max(1, smooth))
            dy = int(dy / max(1, smooth))
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

    def main(settings):
        offsets, client_dll = get_offsets_and_client_dll()
        window_size = get_window_size()
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        while True:
            # Всегда берем актуальные настройки
            try:
                with open(CONFIG_FILE, 'r') as f:
                    settings.update(json.load(f))
            except Exception:
                pass
            target_list = []
            target_list = esp(pm, client, offsets, client_dll, settings, target_list, window_size)
            key = settings.get('keyboard', {"type": "key", "code": 0x43})
            smooth = settings.get('aim_smooth', 10)
            if is_key_pressed(key):
                aimbot(target_list, settings['radius'], settings['aim_mode_distance'], smooth)
            time.sleep(0.001)

    def start_main_thread(settings):
        while True:
            main(settings)

    def setup_watcher(app, settings):
        watcher = QFileSystemWatcher()
        watcher.addPath(CONFIG_FILE)
        def reload_settings():
            new_settings = load_settings()
            settings.update(new_settings)
        watcher.fileChanged.connect(reload_settings)
        app.exec()

    def main_program():
        app = QCoreApplication(sys.argv)
        settings = load_settings()
        threading.Thread(target=start_main_thread, args=(settings,), daemon=True).start()
        setup_watcher(app, settings)

    main_program()
    
if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)
    print("Waiting cs2.exe")
    while True:
        time.sleep(1)
        try:
            pm = pymem.Pymem("cs2.exe")
            client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
            break
        except Exception as e:
            pass
    print("Starting Mortal cheat!")
    time.sleep(2)
    process1 = multiprocessing.Process(target=configurator)
    process2 = multiprocessing.Process(target=esp_main)
    process3 = multiprocessing.Process(target=triggerbot)
    process4 = multiprocessing.Process(target=aim)

    process1.start()
    process2.start()
    process3.start()
    process4.start()

    process1.join()
    process2.join()
    process3.join()
    process4.join()
