import webview
import os

if __name__ == '__main__':
    icon_path = 'E:/SymanWorkplace/qt5_cef/bitbug_favicon.ico'
    webview.create_window(url='file:///{dirName}/index.html'.format(dirName=os.path.dirname(__file__)),
                          maximized=False, context_menu=True, icon_path=icon_path)
