import webview
import os

if __name__ == '__main__':
    webview.create_window(url='file:///{dirName}/index.html'.format(dirName=os.path.dirname(__file__)),
                          maximized=True, context_menu=True)
