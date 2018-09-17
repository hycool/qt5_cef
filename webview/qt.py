import sys
import os
import base64
import time
import datetime
import subprocess
import platform
import signal
from PyQt5 import QtCore
from threading import Event, Thread
import webview.constant as constant
from cefpython3 import cefpython as cef
from uuid import uuid4
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

pixel_ratio = 1
screen_width = 0
screen_height = 0
default_window_width = constant.default_window_width
default_window_height = constant.default_window_height
default_window_title = constant.default_window_title
default_nest_window_margin = constant.default_nest_window_margin
min_window_width = constant.min_window_width
min_window_height = constant.min_window_height
cef_sdk = constant.burgeon_cef_sdk_js
language_locale = constant.language_locale

global_icon_path = ''

debug_mode = False

# dpi 所对应的缩放比
dpi_dict = {
    '96': 1,
    '120': 1.25,
    '144': 1.5,
    '192': 2
}


class Dialog(QDialog):
    def __init__(self, params={}):
        super(Dialog, self).__init__()
        default_params = {
            'topBgColor': '#2a5596',
            'topFontSize': 24,
            'buttonBgColor': '#2a5596',
            'buttonHoverBgColor': '#153D7A',
            'middleFontColor': '#2a5596',
            'middleFontSize': 16,
            'title': 'Dialog Title',
            'description': 'Description Info',
            'dialogWidth': 360,
            'dialogHeight': 201,
            'leftButtonText': 'Left Button',
            'rightButtonText': 'Right Button',
            'leftButtonAction': 'close',
            'rightButtonAction': 'cancel',
            'buttonWidth': 110,
            'buttonHeight': 34,
            'buttonFontSize': 16,
            'borderRadius': 6,
            'blurRadius': 20
        }
        default_params.update(params)
        global pixel_ratio
        if platform.system() == 'Windows':
            pixel_ratio = dpi_dict[str(self.logicalDpiX())]
        self.pixel_ratio = pixel_ratio
        self.m_drag = False
        self.m_DragPosition = 0
        self.params = default_params
        self.init()
        self.init_style()
        # self.show()
        # q = QEventLoop()
        # q.exec_()
        self.exec_()

    def init(self):
        action = {
            'close': self.quit_app,
            'cancel': self.close
        }
        width = self.params['dialogWidth'] * self.pixel_ratio + self.params['blurRadius'] * 2 * self.pixel_ratio
        height = self.params['dialogHeight'] * self.pixel_ratio + self.params['blurRadius'] * 2 * self.pixel_ratio
        self.resize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        if platform.system() == 'Windows':
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setColor(Qt.gray)
            shadow_effect.setBlurRadius(self.params['blurRadius'])
            shadow_effect.setOffset(0, 0)
            self.setGraphicsEffect(shadow_effect)
            self.setContentsMargins(self.params['blurRadius'] * self.pixel_ratio,
                                    self.params['blurRadius'] * self.pixel_ratio,
                                    self.params['blurRadius'] * self.pixel_ratio,
                                    self.params['blurRadius'] * self.pixel_ratio)

        v_layout = QVBoxLayout()

        h_layout_top = QHBoxLayout()
        h_layout_top.setContentsMargins(0, 0, 0, 0)
        h_layout_top.setSpacing(0)

        h_layout_middle = QHBoxLayout()
        h_layout_middle.setContentsMargins(0, 0, 0, 0)
        h_layout_middle.setSpacing(0)

        h_layout_bottom = QHBoxLayout()

        dialog_title = QLabel()
        dialog_title.setText(self.params['title'])
        dialog_title.setAlignment(Qt.AlignCenter)
        dialog_title.setObjectName('dialog_title')
        h_layout_top.addWidget(dialog_title)

        dialog_description = QLabel()
        dialog_description.setText(self.params['description'])
        dialog_description.setAlignment(Qt.AlignCenter)
        dialog_description.setObjectName('dialog_description')
        h_layout_middle.addWidget(dialog_description)

        left_button = QPushButton(self.params['leftButtonText'])
        left_button.clicked.connect(action[self.params['leftButtonAction']])
        right_button = QPushButton(self.params['rightButtonText'])
        right_button.clicked.connect(action[self.params['rightButtonAction']])

        h_layout_bottom.addStretch(1)
        h_layout_bottom.addWidget(left_button)
        h_layout_bottom.addStretch(1)
        h_layout_bottom.addWidget(right_button)
        h_layout_bottom.addStretch(1)

        top_widget = QWidget()
        top_widget.setProperty('name', 'top_widget')

        middle_widget = QWidget()
        middle_widget.setProperty('name', 'middle_widget')

        bottom_widget = QWidget()
        bottom_widget.setProperty('name', 'bottom_widget')

        top_widget.setLayout(h_layout_top)
        middle_widget.setLayout(h_layout_middle)
        bottom_widget.setLayout(h_layout_bottom)

        v_layout.addWidget(top_widget, 50)
        v_layout.addWidget(middle_widget, 101)
        v_layout.addWidget(bottom_widget, 50)
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(v_layout)

    def init_style(self):
        style = """
          QWidget [name="top_widget"] {
            background-color: [topBgColor];
            border-top-left-radius: [borderRadius];
            border-top-right-radius:[borderRadius];
          }
          QWidget [name="middle_widget"] {
            background-color: [middleBgColor];
          }
          QWidget [name="bottom_widget"] {
            border-top: 1px solid #dcdcdc;
            background-color: [bottomBgColor];
            border-bottom-left-radius:[borderRadius];
            border-bottom-right-radius:[borderRadius];
          }
          QPushButton {
            background-color: [buttonBgColor];
            color: #fff;
            font-family: Microsoft YaHei;
            text-align: center;
            border-radius: 5px;
            width: [buttonWidth];
            height: [buttonHeight];
            font-size: [buttonFontSize];
          }
          QPushButton:hover {
            background-color: [buttonHoverBgColor];
          }
          QLabel {
            font-family: Microsoft YaHei;
            text-align: center;
          }
          #dialog_title {
            color: #fff;
            font-size: [topFontSize];
          }
          #dialog_description{
            color: [middleFontColor];
            font-size: [middleFontSize];
          }
        """
        style = style.replace('[borderRadius]', str(self.params['borderRadius'] * self.pixel_ratio) + 'px')
        style = style.replace('[topBgColor]', self.params['topBgColor'])
        style = style.replace('[middleBgColor]', '#fff')
        style = style.replace('[bottomBgColor]', '#fff')
        style = style.replace('[buttonWidth]', str(self.params['buttonWidth'] * self.pixel_ratio) + 'px')
        style = style.replace('[buttonHeight]', str(self.params['buttonHeight'] * self.pixel_ratio) + 'px')
        style = style.replace('[buttonBgColor]', self.params['buttonBgColor'])
        style = style.replace('[middleFontColor]', self.params['middleFontColor'])
        style = style.replace('[middleFontSize]', str(int(self.params['middleFontSize'] * self.pixel_ratio)) + 'px')
        style = style.replace('[topFontSize]', str(int(self.params['topFontSize'] * self.pixel_ratio)) + 'px')
        style = style.replace('[buttonFontSize]', str(int(self.params['buttonFontSize'] * self.pixel_ratio)) + 'px')
        style = style.replace('[buttonHoverBgColor]', self.params['buttonHoverBgColor'])
        self.setStyleSheet(style)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.m_drag and event.buttons() and Qt.LeftButton:
            self.move(event.globalPos() - self.m_DragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False

    def quit_app(self):
        self.close()
        quit_application()


class CefApplication(QApplication):
    def __init__(self, args):
        super(CefApplication, self).__init__(args)
        self.timer = self.create_timer()

    def create_timer(self):
        timer = QTimer()
        timer.timeout.connect(self.on_timer)
        timer.start(10)
        return timer

    @staticmethod
    def on_timer():
        cef.MessageLoopWork()

    def stop_timer(self):
        # Stop the timer after Qt's message loop has ended
        self.timer.stop()


class LoadHandler(object):
    def __init__(self, uid, payload, cid, browser):
        self.payload = payload
        self.uid = uid
        self.cid = cid
        self.browser = browser
        self.main_frame_load_start_time = 0
        self.main_frame_load_end_time = 0

    def OnLoadStart(self, browser, frame):
        if frame.IsMain():
            if debug_mode:
                with open(os.path.dirname(__file__) + '/burgeon.cef.sdk.js', 'r', encoding='UTF-8') as js:
                    browser.ExecuteJavascript(js.read())
            else:
                browser.ExecuteJavascript(cef_sdk)
            self.main_frame_load_start_time = time.time()
            append_payload(self.uid, self.payload, self.cid)
            browser.ExecuteJavascript('window.__cef__.CEF_INFO.start_load_timestamp = {start_load_timestamp}'.format(
                start_load_timestamp=self.main_frame_load_start_time))
            browser.ExecuteJavascript(
                'window.__cef__.CEF_INFO.language = "{language}"'.format(language=get_system_language()))
            self.browser.update_browser_info_one_by_one()

    def OnLoadEnd(self, browser, frame, http_code):
        if frame.IsMain():
            self.main_frame_load_end_time = time.time()
            load_time_cost = self.main_frame_load_end_time - self.main_frame_load_start_time
            browser.ExecuteJavascript('window.__cef__.CEF_INFO.end_load_timestamp = {start_load_timestamp}'.format(
                start_load_timestamp=self.main_frame_load_end_time))
            browser.ExecuteJavascript('window.__cef__.CEF_INFO.loadTimeCost = {time_cost}'.format(
                time_cost=load_time_cost))

    def OnLoadError(self, browser, frame, error_code, error_text_out, failed_url):
        if frame.IsMain():
            if debug_mode:
                with open(os.path.dirname(__file__) + '/burgeon.cef.sdk.js', 'r', encoding='UTF-8') as js:
                    browser.ExecuteJavascript(js.read())
            else:
                browser.ExecuteJavascript(cef_sdk)
            append_payload(self.uid, self.payload, self.cid)
            self.browser.update_browser_info_one_by_one()


class BrowserView(QMainWindow):
    instances = {}
    cid_map = {}
    cid_hwnd_map = {}

    full_screen_trigger = QtCore.pyqtSignal()
    resize_trigger = QtCore.pyqtSignal(int, int)
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

    def __init__(self, uid, title="", url="", width=default_window_width,
                 height=default_window_height,
                 resizable=True, full_screen=False, min_size=(min_window_width, min_window_height),
                 background_color="#ffffff", web_view_ready=None, cid='', enable_max=True, window_type='cef'):
        super(BrowserView, self).__init__()
        BrowserView.instances[uid] = self
        screen = QDesktopWidget().screenGeometry()
        global screen_width, screen_height
        screen_width = screen.width()
        screen_height = screen.height()
        self.attached_child_list = []  # 存储该窗口的跟随子窗口列表
        self.third_party_pid_list = []  # 存储当前窗口所内嵌第三方应用的子进程Id
        self.responsive_params = {
            'top': 0,
            'right': 0,
            'bottom': 0,
            'left': 0
        }  # 当作为某个窗口的跟随子窗口时，如果需要响应式的随着父窗口缩放而改变自身大小，则使用这些参数，表示在窗口自适应过程中，始终距离父窗口四边的距离
        self.uid = uid
        if cid == '':
            self.cid = uid
        else:
            self.cid = cid

        BrowserView.cid_map[uid] = self.cid
        self.is_full_screen = False
        self.load_event = Event()

        # 处理默认窗口大小
        if width != -1 and height != -1:
            self.resize(width, height)
        else:
            self.resize(screen_width * 0.85, screen_height * 0.8)

        self.title = title
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(global_icon_path))

        # Set window background color
        self.background_color = QColor()
        self.background_color.setNamedColor(background_color)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), self.background_color)
        self.setPalette(palette)

        if not resizable:
            self.setFixedSize(width, height)

        self.setMinimumSize(min_size[0], min_size[1])
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        # 禁用窗口最大化
        if not enable_max:
            self.setFixedSize(self.width(), self.height())
            self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        if window_type == 'cef':
            window_info = cef.WindowInfo()
            rect = [0, 0, self.width(), self.height()]
            window_info.SetAsChild(int(self.winId()), rect)

            setting = {
                "standard_font_family": "Microsoft YaHei",
                "default_encoding": "utf-8",
                "plugins_disabled": True,
                "tab_to_links_disabled": True,
                "web_security_disabled": True,
            }

            if url is not None:
                pass
                self.view = cef.CreateBrowserSync(window_info, url=url, settings=setting)
            else:
                self.view = cef.CreateBrowserSync(window_info, url="about:blank", settings=setting)

        # self.view.ShowDevTools()
        self.full_screen_trigger.connect(self.toggle_full_screen)
        self.resize_trigger.connect(self.trigger_window_resize)
        self.load_event.set()

        if full_screen:
            self.emit_full_screen_signal()

        self.move(QApplication.desktop().availableGeometry().center() - self.rect().center())
        self.activateWindow()
        self.raise_()
        if web_view_ready is not None:
            web_view_ready.set()

    def exit_application(self):
        quit_application()

    def changeEvent(self, event):
        if self.isActiveWindow() and hasattr(self, 'view'):
            self.view.SetFocus(True)

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            if hasattr(self, 'view'):
                self.view.ExecuteFunction('window.python_cef.dispatchCustomEvent', 'windowCloseEvent')
            else:
                self.kill_subprocess()
                event.accept()
        else:
            if self.uid == 'master':
                self.kill_subprocess()
                quit_application()
            else:
                self.kill_subprocess()
                self.update_browser_info_one_by_one(increase=False)
                event.accept()

    def resizeEvent(self, event):
        cef.WindowUtils.OnSize(self.winId(), 0, 0, 0)
        size = event.size()
        self.resize_trigger.emit(size.width(), size.height())

    def kill_subprocess(self):
        if platform.system() == 'Windows':
            for sub_pid in self.third_party_pid_list:
                os.popen('taskkill /pid {pid} -f'.format(pid=sub_pid))

    def show_window(self, cid=''):
        uid = self.get_uid_by_cid(cid)
        if cid == '' or cid is None:
            self.show()
        elif uid is not None:
            BrowserView.instances[uid].show()

    def hide_window(self, cid=''):
        uid = self.get_uid_by_cid(cid)
        if cid == '' or cid is None:
            self.hide()
        elif uid is not None:
            BrowserView.instances[uid].hide()

    def close_window(self, cid_lists=[]):
        """
        This method can be invoked by Javascript.
        :return:
        """
        if len(cid_lists) == 0:
            self.view.CloseDevTools()  # 关闭cef的devTools
            self.close()  # 关闭qt的窗口
        else:
            for cid in cid_lists:
                uid = self.get_uid_by_cid(cid)
                if uid in BrowserView.instances.keys():
                    BrowserView.instances[uid].close()
                else:
                    print(cid)
                    self.view.ExecuteFunction('window.python_cef.console', '不存在 cid = {cid} 的窗口'.format(cid=cid),
                                              'warn')

    def close_all_window(self):
        """
        This method can be invoked by Javascript.
        :return:
        """
        # for qt_main_window in BrowserView.instances.values():
        #     qt_main_window.close()
        self.kill_subprocess()
        quit_application()

    def open(self, param=None):
        """
        This method can be invoked by Javascript.
        :return:
        """
        if param is None:
            param = {}
        if isinstance(param, dict):
            param.setdefault('url', 'about:blank')
            param.setdefault('title', default_window_title)
            param.setdefault('payload', {})
            param.setdefault('cid', '')
            param.setdefault('maximized', False)
            param.setdefault('minimized', False)
            param.setdefault('width', default_window_width)
            param.setdefault('height', default_window_height)
            param.setdefault('enableMax', True)
            open_new_window(url=param["url"], title=param["title"], payload=param["payload"],
                            maximized=param["maximized"], minimized=param["minimized"], cid=param["cid"],
                            width=param["width"], height=param["height"], enable_max=param["enableMax"])
        elif isinstance(param, str):
            open_new_window(url=param)

    def toggle_full_screen(self):
        if self.is_full_screen:
            self.showNormal()
        else:
            self.showFullScreen()

        self.is_full_screen = not self.is_full_screen

    def trigger_window_resize(self, width, height):
        global pixel_ratio
        if hasattr(self, 'third_party_wrapper_window'):
            if platform.system() == 'Windows':
                pixel_ratio = dpi_dict[str(self.logicalDpiX())]
            param = self.third_party_window_geometry
            width = width - param['left'] * pixel_ratio - param['right'] * pixel_ratio
            height = height - param['top'] * pixel_ratio - param['bottom'] * pixel_ratio
            self.third_party_wrapper_window.resize(width, height)

        # 处理该窗口的所有跟随子窗口的resize行为
        for child_window in self.attached_child_list:
            if platform.system() == 'Windows':
                pixel_ratio = dpi_dict[str(child_window.logicalDpiX())]
            param = child_window.responsive_params
            width = width - param['left'] * pixel_ratio - param['right'] * pixel_ratio
            height = height - param['top'] * pixel_ratio - param['bottom'] * pixel_ratio
            child_window.resize(width, height)

    def emit_full_screen_signal(self):
        self.full_screen_trigger.emit()

    def create_cef_pure_window(self, url):
        """
        This method can be invoked by Javascript.
        :return:
        """
        cef.CreateBrowserSync(url=url)

    def maximize_current_window(self):
        self.showMaximized()

    def minimize_current_window(self):
        self.showMinimized()

    def maximize_window(self, uid):
        BrowserView.instances[uid].showMaximized()

    def minimize_window(self, uid):
        BrowserView.instances[uid].showMinimized()

    def update_browser_info_one_by_one(self, increase=True):
        # 移除窗口实例
        if not increase:
            if self.uid in BrowserView.instances.keys():
                del BrowserView.instances[self.uid]
            if self.uid in BrowserView.cid_map.keys():
                del BrowserView.cid_map[self.uid]

        for browser in BrowserView.instances.values():
            if hasattr(browser, 'view'):
                browser.view.ExecuteFunction('window.python_cef.updateCefConfig', 'cidLists',
                                             list(BrowserView.cid_map.values()))
                browser.view.ExecuteFunction('window.python_cef.updateCefConfig', 'widLists',
                                             list(BrowserView.cid_map.keys()))

    def focus_browser(self, cid=None):
        if cid is not None and isinstance(cid, str):
            for (uid, _cid_) in BrowserView.cid_map.items():
                if _cid_ == cid:
                    BrowserView.instances[uid].activateWindow()
                    BrowserView.instances[uid].view.SetFocus(True)
                    BrowserView.instances[uid].view.SetFocus(True)
                    break
        else:
            self.activateWindow()
            self.setFocus(True)
            self.view.SetFocus(True)

    def arouse_window(self, cid=None):
        if cid is not None and isinstance(cid, str):
            for (uid, _cid_) in BrowserView.cid_map.items():
                if _cid_ == cid:
                    BrowserView.instances[uid].activateWindow()
                    BrowserView.instances[uid].showNormal()
                    break
        else:
            self.showNormal()
            self.activateWindow()

    def set_browser_payload(self, cid, payload):
        for (uid, value) in BrowserView.cid_map.items():
            if value == cid:
                BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCustomizePayload', payload)
                break

    def set_cookie(self, cookieObj={}):
        if not isinstance(cookieObj, dict):
            return
        else:
            cookieObj.setdefault('name', 'default_cookie_name')
            cookieObj.setdefault('value', 'default_cookie_value')
            cookieObj.setdefault('domain', '127.0.0.1')
            cookieObj.setdefault('path', '/')
            cookie_manager = cef.CookieManager().GetGlobalManager()
            cookie = cef.Cookie()
            cookie.SetName(cookieObj['name'])
            cookie.SetValue(cookieObj['value'])
            cookie.SetDomain(cookieObj['domain'])
            cookie.SetPath(cookieObj['path'])
            cookie_manager.SetCookie(self.view.GetUrl(), cookie)

    def get_room_level(self):
        self.view.ExecuteFunction('window.python_cef.console', self.view.GetZoomLevel())

    def set_roo_level(self, level):
        self.view.SetZoomLevel(level)

    def get_uid_by_cid(self, cid):
        for (uid, value) in BrowserView.cid_map.items():
            if value == cid:
                return uid

    def dispatch_customize_event(self, event_name='', event_data={}):
        for uid in BrowserView.instances.keys():
            if hasattr(BrowserView.instances[uid], 'view'):
                BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.dispatchCustomEvent', event_name,
                                                                event_data)

    def nest_third_party_application(self, param={}):
        if param is None:
            param = {}
        param.setdefault('newCid', '')  # 本窗口的cid
        param.setdefault('targetCid', 'master')  # 内嵌应用目标窗口的cid
        param.setdefault('top', 0)  # 内嵌窗口距离目标窗口顶部的自适应距离
        param.setdefault('right', 0)  # 内嵌窗口距离目标窗口右侧的自适应距离
        param.setdefault('bottom', 0)  # 内嵌窗口距离目标窗口底部的自适应距离
        param.setdefault('left', 0)  # 内嵌窗口距离目标窗口左侧的自适应距离
        param.setdefault('applicationPath', '')
        param.setdefault('launchParams', {})
        nest_third_party_application(target_uid=self.get_uid_by_cid(param['targetCid']),
                                     cid=param['newCid'],
                                     third_party_window_geometry={
                                         'top': param['top'],
                                         'right': param['right'],
                                         'bottom': param['bottom'],
                                         'left': param['left'],
                                     },
                                     application_path=param['applicationPath'],
                                     launch_params=param['launchParams'],
                                     )

    def nest_frame_window(self, param={}):
        if param is None:
            param = {}
        if isinstance(param, dict):
            param.setdefault('newCid', '')  # 新窗口的cid
            param.setdefault('targetCid', 'master')  # 目标窗口cid
            param.setdefault('url', '')  # 新窗口将要加载的url
            param.setdefault('payload', {})  # 需要传递给新窗口的挂载数据
            param.setdefault('top', default_nest_window_margin)  # 内嵌窗口距离target窗口的顶部距离
            param.setdefault('right', default_nest_window_margin)  # 内嵌窗口距离target窗口的右侧距离
            param.setdefault('bottom', default_nest_window_margin)  # 内嵌窗口距离target窗口的底部距离
            param.setdefault('left', default_nest_window_margin)  # 内嵌窗口距离target窗口的左侧距离
            frame_window = create_qt_view(url=param['url'], cid=param['newCid'], default_show=False,
                                          payload=param['payload'])
            frame_window.responsive_params['top'] = param['top']
            frame_window.responsive_params['right'] = param['right']
            frame_window.responsive_params['bottom'] = param['bottom']
            frame_window.responsive_params['left'] = param['left']
            target_uid = self.get_uid_by_cid(param['targetCid'])
            if target_uid is not None:
                global pixel_ratio
                if platform.system() == 'Windows':
                    pixel_ratio = dpi_dict[str(frame_window.logicalDpiX())]
                target_window = BrowserView.instances[target_uid]
                target_window.attached_child_list.append(frame_window)
                frame_window.setParent(target_window)
                frame_window.show()
                frame_window.move(param['left'] * pixel_ratio, param['top'] * pixel_ratio)
                width = target_window.width() - param['left'] * pixel_ratio - param['right'] * pixel_ratio
                height = target_window.height() - param['top'] * pixel_ratio - param['bottom'] * pixel_ratio
                frame_window.resize(width, height)
                frame_window.setWindowFlags(Qt.FramelessWindowHint)

    def update_window_geometry(self, cid=None):
        if cid is None:
            uid = self.uid
        else:
            uid = self.get_uid_by_cid(cid)
        print('uid = ', uid)
        BrowserView.instances[uid].view.ExecuteJavascript(
            'window.__cef__.CEF_INFO.windowLogicalWidth = {windowLogicalWidth}'.format(
                windowLogicalWidth=self.width()))
        BrowserView.instances[uid].view.ExecuteJavascript(
            'window.__cef__.CEF_INFO.windowLogicalHeight = {windowLogicalHeight}'.format(
                windowLogicalHeight=self.height()))

    def show_close_dialog(self, params={}):
        if params is None:
            params = {}
        Dialog(params)


class ThirdPartyWindow(QWidget):
    def __init__(self, child_window):
        super(ThirdPartyWindow, self).__init__()
        embed = self.createWindowContainer(child_window, self)
        window_layout = QHBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(embed)
        self.setLayout(window_layout)


def get_uid_by_cid(cid):
    for (uid, value) in BrowserView.cid_map.items():
        if value == cid:
            return uid


def get_system_language():
    language_code = QLocale().language()
    if str(language_code) in language_locale.keys():
        return language_locale[str(language_code)]['locale']
    else:
        return 'en_US'


def get_handle_id(third_party_application_title):
    if platform.system() == 'Windows':
        import win32gui
        hwnd = 0

        def call_back(item_hwnd, window_title):
            if win32gui.GetWindowText(item_hwnd) == window_title:
                nonlocal hwnd
                hwnd = item_hwnd

        if hwnd == 0:
            start = time.time()
            while hwnd == 0:
                time.sleep(0.1)
                win32gui.EnumWindows(call_back, third_party_application_title)
                end = time.time()
                if hwnd != 0 or end - start > 10:
                    return hwnd

        return hwnd


def launch_f4_client(application_title,
                     application_path,
                     launch_params,
                     qt_window):
    exe_path = application_path + ' -t:' + application_title + ' -p:' + str(os.getpid())
    for (k, v) in launch_params.items():
        exe_path = exe_path + ' ' + '--' + k + ':' + v + ''
    child_process = subprocess.Popen(exe_path)
    qt_window.third_party_pid_list.append(child_process.pid)


def nest_third_party_application(target_uid='master',
                                 cid='',
                                 third_party_window_geometry={'top': 0, 'right': 0, 'bottom': 0, 'left': 0},
                                 application_path='',
                                 launch_params={}):
    third_party_application_title = generate_guid('third_party_application_title')
    third_party_wrapper_window = create_qt_view(default_show=False, window_type='qt', cid=cid)
    global pixel_ratio
    if platform.system() == 'Windows':
        pixel_ratio = dpi_dict[str(third_party_wrapper_window.logicalDpiX())]
    geometry = third_party_window_geometry
    target_window = BrowserView.instances[target_uid]
    offset_top = pixel_ratio * geometry['top']
    offset_right = pixel_ratio * geometry['right']
    offset_bottom = pixel_ratio * geometry['bottom']
    offset_left = pixel_ratio * geometry['left']
    t = Thread(target=launch_f4_client,
               args=(third_party_application_title, application_path, launch_params, target_window))
    t.start()
    # t.join()

    hwnd = get_handle_id(third_party_application_title)
    if hwnd != 0:
        if cid != '':
            BrowserView.cid_hwnd_map[cid] = hwnd
        temp_window = QWindow.fromWinId(hwnd)
        temp_window.setFlags(
            Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint | Qt.WA_TranslucentBackground)
        third_party_window = ThirdPartyWindow(temp_window)

        third_party_wrapper_window.setCentralWidget(third_party_window)
        third_party_wrapper_window.setWindowFlags(Qt.FramelessWindowHint)
        target_window.third_party_wrapper_window = third_party_wrapper_window  # 设置内嵌【第三方内嵌应用】引用
        target_window.third_party_window_geometry = third_party_window_geometry  # 设置内【第三方内嵌应用】在父窗口size发生改变时的同步规则
        third_party_wrapper_window.setParent(target_window)  # 将【第三方内嵌应用】作为target_window的子控件
        third_party_wrapper_window.show()  # 将【第三方内嵌应用】显示出来
        third_party_wrapper_window.move(offset_left, offset_top)  # 移动【第三方内嵌应用】 窗口位置（相对于target_window）
        # 根据【第三方内嵌应用】的应用场景同步其应具备的宽和高
        third_party_wrapper_window.resize(target_window.width() - offset_left - offset_right,
                                          target_window.height() - offset_top - offset_bottom)


def launch_third_party_application(params={}):
    if params is None:
        params = {}
    params.setdefault('targetCid', 'master')
    params.setdefault('newCid', generate_guid())
    params.setdefault('top', 0)
    params.setdefault('right', 0)
    params.setdefault('bottom', 0)
    params.setdefault('left', 0)
    params.setdefault('applicationPath', '')
    params.setdefault('launchParams', {})
    nest_third_party_application(target_uid=get_uid_by_cid(params['targetCid']),
                                 cid=params['newCid'],
                                 third_party_window_geometry={
                                     'top': params['top'],
                                     'right': params['right'],
                                     'bottom': params['bottom'],
                                     'left': params['left']
                                 },
                                 application_path=params['applicationPath'],
                                 launch_params=params['launchParams']
                                 )


def html_to_data_uri(html):
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    return ret


def generate_guid(prefix='child'):
    return prefix + '_' + uuid4().hex[:8]


def open_new_window(url, title=default_window_title, payload=None, maximized=False, minimized=False, cid='',
                    width=default_window_width, height=default_window_height, enable_max=True):
    create_browser_view(uid=generate_guid(), url=url, title=title, payload=payload, maximized=maximized,
                        minimized=minimized, cid=cid, width=width, height=height, enable_max=enable_max)


def create_qt_view(default_show=True, window_type='cef', url='', cid='', payload={}):
    uid = generate_guid()
    qt_view = BrowserView(uid, window_type=window_type, url=url, cid=cid)
    if window_type == 'cef':
        set_client_handler(uid, payload=payload, cid=cid, browser=qt_view)
        set_javascript_bindings(uid)
    if default_show:
        qt_view.show()
    return qt_view


def create_browser_view(uid, title="", url=None, width=default_window_width, height=default_window_height,
                        resizable=True, full_screen=False,
                        min_size=(min_window_width, min_window_height),
                        background_color="#ffffff", web_view_ready=None, payload=None, maximized=False,
                        minimized=False, cid='', call_back=None, enable_max=True):
    browser = BrowserView(uid, title, url, width, height, resizable, full_screen, min_size,
                          background_color, web_view_ready, cid=cid, enable_max=enable_max)
    if maximized:
        browser.showMaximized()

    if minimized:
        browser.showMinimized()

    browser.show()
    if hasattr(call_back, '__call__'):
        call_back(browser)

    set_client_handler(uid, payload, cid, browser)
    set_javascript_bindings(uid)


def launch_main_window(uid, title, url, width, height, resizable, full_screen, min_size,
                       background_color, web_view_ready, context_menu=False, maximized=True, minimized=False,
                       user_agent='ffpos/1.0.01', icon_path='', call_back=None):
    global global_icon_path
    global_icon_path = icon_path
    global app
    app = CefApplication(sys.argv)
    app_name = 'FC-POS Copyright©2017-{currentYear} Burgeon. All Rights Reserved.'.format(
        currentYear=datetime.datetime.now().year)
    app.setApplicationName(app_name)
    cef_work_path = ''
    if platform.system() == 'Windows':
        cef_work_path = os.environ['ALLUSERSPROFILE']
    elif platform.system() == 'Darwin':
        cef_work_path = os.environ['HOME']
    cache_path = os.path.join(cef_work_path, 'Burgeon', 'CEF')
    settings = {
        'context_menu': {'enabled': context_menu},
        'auto_zooming': 0.0,
        'user_agent': user_agent,
        'cache_path': cache_path,
        'persist_user_preferences': True,
        'remote_debugging_port': 3333,
    }
    switches = {
        'disable-gpu': ''
    }

    cef.Initialize(settings=settings, switches=switches)
    create_browser_view(uid=uid, title=title, url=url, width=width, height=height, resizable=resizable,
                        full_screen=full_screen, min_size=min_size,
                        background_color=background_color, web_view_ready=web_view_ready, maximized=maximized,
                        minimized=minimized, call_back=call_back)
    app.exec_()
    app.stop_timer()
    del app
    cef.Shutdown()


def set_client_handler(uid, payload, cid, browser):
    BrowserView.instances[uid].view.SetClientHandler(LoadHandler(uid, payload, cid, browser))


def set_javascript_bindings(uid):
    bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)
    bindings.SetProperty("cefPython3", cef.GetVersion())
    bindings.SetProperty('windowId', uid)
    bindings.SetProperty('system', platform.system())
    bindings.SetProperty('systemLanguage', get_system_language())
    bindings.SetObject('windowInstance', BrowserView.instances[uid])
    BrowserView.instances[uid].view.SetJavascriptBindings(bindings)


def append_payload(uid, payload, cid=''):
    BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCefConfig', 'wid', uid)
    if cid != '':
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCefConfig', 'cid', cid)
    else:
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCefConfig', 'cid', uid)
    if payload is None:
        return
    if isinstance(payload, dict):
        fun_list = []
        for (k, v) in payload.items():
            if isinstance(v, cef.JavascriptCallback):
                fun_list.append(k)
                BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.console',
                                                                '检测到 payload.{key} 是函数类型，启动新窗口时挂载的payload中不允许包含函数'
                                                                .format(key=k),
                                                                'warn')
        for key in fun_list:
            del payload[key]
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCustomizePayload', payload)
    else:
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.console',
                                                        '启动新窗口时挂载的payload必须为JsonObject，且对象属性不能为函数: payload = {payload}'
                                                        .format(payload=payload))


def execute_javascript(script, uid):
    if uid in BrowserView.instances:
        BrowserView.instances[uid].view.ExecuteJavascript(script)
    else:
        return


def set_cookies(url, cookies):
    cookie_manager = cef.CookieManager().GetGlobalManager()
    cookie_manager.SetCookie(url, cookies)


def quit_application():
    app.quit()
    t = Thread(target=exit_python)
    t.start()


def exit_python():
    if platform.system() == 'Windows':
        pid = os.getpid()
        os.kill(pid, signal.CTRL_BREAK_EVENT)
    else:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
