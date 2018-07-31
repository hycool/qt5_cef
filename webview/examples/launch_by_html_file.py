import webview
import os

if __name__ == '__main__':
    webview.create_window(url='file:///{dirName}/index.html'.format(dirName=os.path.dirname(__file__)),
                          maximized=False, context_menu=True, icon_path=os.path.dirname(__file__))
