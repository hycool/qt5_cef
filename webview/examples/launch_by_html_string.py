import webview

HTML_CODE = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>py webview demostrate</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            box-sizing: border-box;
            font-family: "Microsoft YaHei UI";
            overflow: hidden;
            user-select: none;
            background-color: #d7d7d7;
        }
        h1 {
            font-size: 16px;
            text-align: center;
            margin: 15px;
        }
        div {
            margin: 0 auto;
            text-align: center;
        }
        button {
            display: inline-block;
            font-size: 14px;
            width: 600px;
            padding: 5px;
            margin: 5px;
            text-align: left;
            color: #2a5aff;
        }
        button>span {
            display: inline-block;
            width: 150px;
            text-align: right;
            color: black;
        }
    </style>
</head>
<body>
    <h1>
        当前时间：<span id="random"></span> <br/>
        当前窗口ID：<span id="browser_id"></span> <br/>
    </h1>
    <div>
        <button onclick="loadUrl()">
            <span>弹出一个新的窗口：</span>
            window.__cef__.open(param: JsonObject)
        </button>
        <br/>
        <button onclick="window.__cef__.close()">
            <span>主调关闭窗口：</span>
            window.__cef__.close()
        </button>
        <br/>
        <button onclick="window.__cef__.closeAll()">
            <span>关闭所有窗口：</span>
            window.__cef__.closeAll()
        </button>
        <br/>
        <button onclick="window.__cef__.toggleFullScreen()">
            <span>切换全屏：</span>
            window.__cef__.toggleFullScreen()()
        </button>
        <br/>
    </div>
    <script>
        function loadUrl() {
            if (window.__cef__) {
                window.__cef__.open({
                    url: 'http://localhost:8421/pywebview/burgeon/assets/index.html',
                    title: '伯俊软件',
                    payload: {
                        json: { a: 1, b: 2 },
                        array: [1, 2, 3],
                        str: 'str',
                        number: Math.PI,
                    }
                });
            }
        }
        const updateInfo = () => {
            document.getElementById('random').innerText = new Date().toLocaleDateString() + '    ' + new Date().toLocaleTimeString()
            document.getElementById('browser_id').innerText = window.windowId
        };
        window.onload = function() {
            updateInfo();
            setInterval(updateInfo, 1000)
        };

        const f1 = (e) => {
            if (confirm('确定关闭当前窗口')) {
                window.__cef__.close();
            }
        };

        setTimeout(() => {
            __cef__.addEventListener('windowCloseEvent', f1);
        }, 10);
    </script>
</body>
</html>
    """

if __name__ == '__main__':
    webview.create_window(url=HTML_CODE, context_menu=True, url_type='string')

