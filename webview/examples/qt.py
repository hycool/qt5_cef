import sys
import os
import base64
from PyQt5 import QtCore
from threading import Event, Thread
import webview.constant as constant
from cefpython3 import cefpython as cef
from uuid import uuid4
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

default_window_width = constant.default_window_width
default_window_height = constant.default_window_height
default_window_title = constant.default_window_title
min_window_width = constant.min_window_width
min_window_height = constant.min_window_height
cef_sdk = constant.burgeon_cef_sdk_js

global_icon_path = ''

debug_mode = False


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

    def OnLoadStart(self, browser, frame):
        if debug_mode:
            with open(os.path.dirname(__file__) + '/burgeon.cef.sdk.js', 'r', encoding='UTF-8') as js:
                browser.ExecuteJavascript(js.read())
        else:
            browser.ExecuteJavascript(cef_sdk)
        append_payload(self.uid, self.payload, self.cid)
        self.browser.update_browser_info_one_by_one()

    def OnLoadError(self, browser, frame, error_code, error_text_out, failed_url):
        if debug_mode:
            with open(os.path.dirname(__file__) + '/burgeon.cef.sdk.js', 'r', encoding='UTF-8') as js:
                browser.ExecuteJavascript(js.read())
        else:
            browser.ExecuteJavascript(cef_sdk)
        append_payload(self.uid, self.payload, self.cid)
        self.browser.update_browser_info_one_by_one()


class KeyboardHandler(object):
    def OnPreKeyEvent(self, browser, event, event_handle, is_keyboard_shortcut_out):
        print(event)


class BrowserView(QMainWindow):
    instances = {}
    cid_map = {}

    full_screen_trigger = QtCore.pyqtSignal()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

    def __init__(self, uid, title, url, width, height, resizable, full_scrren,
                 min_size, background_color, webview_ready, cid, enable_max):
        super(BrowserView, self).__init__()
        BrowserView.instances[uid] = self
        self.uid = uid
        if cid == '':
            self.cid = uid
        else:
            self.cid = cid
        BrowserView.cid_map[uid] = self.cid
        self.is_full_screen = False
        self.load_event = Event()

        self.resize(width, height)  # QWidget.resize 重新调整qt 窗口大小
        self.title = title
        self.setWindowTitle(title)  # QWidget.setWindowTitle 窗口标题重命名
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
        # 禁用窗口最大化
        if not enable_max:
            self.setFixedSize(self.width(), self.height())

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
        self.load_event.set()

        if full_scrren:
            self.emit_full_screen_signal()

        self.move(QApplication.desktop().availableGeometry().center() - self.rect().center())
        self.activateWindow()
        self.raise_()
        if webview_ready is not None:
            webview_ready.set()

    def exit_application(self):
        quit_application()

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            self.view.ExecuteFunction('window.python_cef.dispatchCustomEvent', 'windowCloseEvent')
        else:
            if self.uid == 'master':
                quit_application()
            else:
                event.accept()
                self.update_browser_info_one_by_one(increase=False)

    def resizeEvent(self, event):
        cef.WindowUtils.OnSize(self.winId(), 0, 0, 0)

    def close_window(self):
        """
        This method can be invoked by Javascript.
        :return:
        """
        self.view.CloseDevTools()  # 关闭cef的devTools
        self.close()  # 关闭qt的窗口

    def close_all_window(self):
        """
        This method can be invoked by Javascript.
        :return:
        """
        # for qt_main_window in BrowserView.instances.values():
        #     qt_main_window.close()
        quit_application()

    def open(self, param=None):
        """
        This method can be invoked by Javascript.
        :return:
        """
        if param is None:
            param = {}
        if isinstance(param, dict):
            print('param = ', param)
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

    def emit_full_screen_signal(self):
        self.full_screen_trigger.emit()

    def create_cef_pure_window(self, url):
        """
        This method can be invoked by Javascript.
        :return:
        """
        cef_window = cef.CreateBrowserSync(url=url)
        cef_window.SetZoomLevel(5.0)

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
            del BrowserView.instances[self.uid]
            del BrowserView.cid_map[self.uid]

        for browser in BrowserView.instances.values():
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
        print(cid, payload)
        for (uid, value) in BrowserView.cid_map.items():
            if value == cid:
                BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCustomizePayload', payload)
                break


def html_to_data_uri(html):
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    return ret


def generate_guid():
    return 'child_' + uuid4().hex[:8]


def open_new_window(url, title=default_window_title, payload=None, maximized=False, minimized=False, cid='',
                    width=default_window_width, height=default_window_height, enable_max=True):
    create_browser_view(uid=generate_guid(), url=url, title=title, payload=payload, maximized=maximized,
                        minimized=minimized, cid=cid, width=width, height=height, enable_max=enable_max)


def create_browser_view(uid, title="", url=None, width=default_window_width, height=default_window_height,
                        resizable=True, full_screen=False,
                        min_size=(min_window_width, min_window_height),
                        background_color="#ffffff", web_view_ready=None, payload=None, maximized=False,
                        minimized=False, icon_path='', cid='', call_back=None, enable_max=True):
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
    settings = {
        'context_menu': {'enabled': context_menu},
        'auto_zooming': 0.0,
        'user_agent': user_agent
    }
    switches = {
        'disable-gpu': ''
    }
    # gpu 硬件加速在mac上跑步起来，暂时注释
    # if platform.system() == 'Windows':
    #     from gpuinfo.windows import get_gpus
    #     if len(get_gpus()) == 0:
    #         switches.setdefault('disable-gpu', '')

    cef.Initialize(settings=settings, switches=switches)
    create_browser_view(uid=uid, title=title, url=url, width=width, height=height, resizable=resizable,
                        full_screen=full_screen, min_size=min_size,
                        background_color=background_color, web_view_ready=web_view_ready, maximized=maximized,
                        minimized=minimized, icon_path=icon_path, call_back=call_back)
    app.exec_()
    app.stop_timer()
    del app
    cef.Shutdown()


def set_client_handler(uid, payload, cid, browser):
    BrowserView.instances[uid].view.SetClientHandler(LoadHandler(uid, payload, cid, browser))
    BrowserView.instances[uid].view.SetClientHandler(KeyboardHandler())


def set_javascript_bindings(uid):
    bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)
    bindings.SetProperty("cefPython3", cef.GetVersion())
    bindings.SetProperty('windowId', uid)
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
        print('payload = ', payload)
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.updateCustomizePayload', payload)
    else:
        BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.console',
                                                        '启动新窗口时挂载的payload必须为JsonObject，且对象属性不能为函数: payload = {payload}'
                                                        .format(payload=payload))


def execute_javascript(script, uid):
    BrowserView.instances[uid].view.ExecuteJavascript(script)


def set_cookies(url, cookies):
    cookie_manager = cef.CookieManager().GetGlobalManager()
    cookie_manager.SetCookie(url, cookies)


def quit_application():
    app.quit()
    t = Thread(target=exit_python)
    t.start()


def exit_python():
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
