import sys
import os
import base64
import win32gui
import time
import subprocess
from PyQt5 import QtCore
from threading import Event, Thread
import webview.constant as constant
from cefpython3 import cefpython as cef
from uuid import uuid4
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

screen_width = 0
screen_height = 0
default_window_width = constant.default_window_width
default_window_height = constant.default_window_height
default_window_title = constant.default_window_title
min_window_width = constant.min_window_width
min_window_height = constant.min_window_height
cef_sdk = constant.burgeon_cef_sdk_js

global_icon_path = ''

debug_mode = False

dpi_dict = {
    '96': 1,
    '120': 1.25,
    '144': 1.5,
    '192': 2
}


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


class BrowserView(QMainWindow):
    instances = {}
    cid_map = {}

    full_screen_trigger = QtCore.pyqtSignal()
    resize_trigger = QtCore.pyqtSignal(int, int)
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

    def __init__(self, uid, title, url, width, height, resizable, full_screen,
                 min_size, background_color, web_view_ready, cid, enable_max, window_type='cef'):
        super(BrowserView, self).__init__()
        BrowserView.instances[uid] = self
        screen = QDesktopWidget().screenGeometry()
        global screen_width
        screen_width = screen.width()

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
            self.resize(screen_width * 0.5, screen_width * 0.5 * 0.618)

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
        # 禁用窗口最大化
        if not enable_max:
            self.setFixedSize(self.width(), self.height())

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

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            if hasattr(self, 'view'):
                self.view.ExecuteFunction('window.python_cef.dispatchCustomEvent', 'windowCloseEvent')
            else:
                event.accept()
        else:
            if self.uid == 'master':
                quit_application()
            else:
                event.accept()
                self.update_browser_info_one_by_one(increase=False)

    def resizeEvent(self, event):
        cef.WindowUtils.OnSize(self.winId(), 0, 0, 0)
        size = event.size()
        self.resize_trigger.emit(size.width(), size.height())

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
                BrowserView.instances[self.get_uid_by_cid(cid)].close()

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
        if hasattr(self, 'f4_window'):
            self.f4_window.move(0, self.f4_window_geometry['top'])
            self.f4_window.resize(width, height - self.f4_window_geometry['top'])

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
            del BrowserView.instances[self.uid]
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
            BrowserView.instances[uid].view.ExecuteFunction('window.python_cef.dispatchCustomEvent', event_name,
                                                            event_data)

    def new_f4_window(self):
        create_qt_view()

    def nest_f4_report(self):
        nest_f4_report()


class Report(QWidget):
    def __init__(self, child_window):
        super(Report, self).__init__()
        self.report_window = child_window
        embed = self.createWindowContainer(self.report_window, self)
        window_layout = QHBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(embed)
        self.setLayout(window_layout)


def get_handle_id():
    report_window_title = None
    report_window_class = 'WindowsForms10.Window.8.app.0.1ca0192_r9_ad1'

    hwnd = win32gui.FindWindow(report_window_class, report_window_title)
    if hwnd == 0:
        start = time.time()
        while hwnd == 0:
            time.sleep(0.5)
            hwnd = win32gui.FindWindow(report_window_class, report_window_title)
            end = time.time()
            if hwnd != 0 or end - start > 10:
                return hwnd
    else:
        return hwnd


def launch_f4_client():
    exe_path = "D:\\report demo\\FastFish.Client.Pos.Win.exe debug -n:3203401 -p:1234 -b:true -m:false -pid:" + str(
        os.getpid()) + ' -t:NESTED_F4_REPORT_WINDOW'
    subprocess.Popen(exe_path)


def nest_f4_report(uid='master', f4_window_geometry={'top': 50}):
    f4_window = create_qt_view(default_show=False)
    offset_top = dpi_dict[str(f4_window.logicalDpiX())] * f4_window_geometry['top']
    t = Thread(target=launch_f4_client)
    t.start()
    # t.join()

    hwnd = get_handle_id()
    report_window = QWindow.fromWinId(hwnd)
    report_window.setFlags(
        Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint | Qt.WA_TranslucentBackground)
    window = Report(report_window)

    f4_window.setCentralWidget(window)
    f4_window.setWindowFlags(Qt.FramelessWindowHint)
    target_window = BrowserView.instances[uid]
    target_window.f4_window = f4_window  # 设置内嵌f4_window引用
    target_window.f4_window_geometry = f4_window_geometry  # 设置内f4_window在父窗口size发生改变时的同步规则
    f4_window.setParent(target_window)  # 将f4_window作为target_window的子控件
    f4_window.show()  # 将f4_window显示出来
    f4_window.move(0, offset_top)  # 移动f4_window 窗口位置（相对于target_window）
    f4_window.resize(target_window.width(), target_window.height() - offset_top)  # 根据f4_window的应用场景同步其应具备的宽和高


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


def create_qt_view(default_show=True):
    uid = generate_guid()
    qt_view = BrowserView(uid, title="", url="", width=default_window_width,
                          height=default_window_height,
                          resizable=True, full_screen=False, min_size=(min_window_width, min_window_height),
                          background_color="#ffffff", web_view_ready=None, cid=uid, enable_max=True, window_type='qt')
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
    import platform
    import signal
    if platform.system() == 'Windows':
        pid = os.getpid()
        os.kill(pid, signal.CTRL_BREAK_EVENT)
    else:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
