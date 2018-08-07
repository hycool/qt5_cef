default_window_width = -1
default_window_height = -1
default_window_title = 'FC-POS'
min_window_width = 800
min_window_height = 600

burgeon_cef_sdk_js = """
(function () {
    if (window.CEF_HAS_INITIALIZED) {
        return
    }
    const moduleName = 'windowInstance';
    const sdkModuleName = '__cef__';
    const pythonCallBack = 'python_cef';
    const cef = {
        payload: {},
        hooks: {}
    };
    const python_cef = {};
    const customEventMap = {
        windowCloseEvent: {
            name: 'windowCloseEvent',
            event: new CustomEvent('windowCloseEvent', {detail: {windowId: window.windowId}}),
            hooks: 0
        }
    };
    python_cef.console = (msg, type) => {
        switch (type) {
            case 'error':
                console.error(msg);
                break;
            case 'warn':
                console.warn(msg);
                break;
            default:
                console.log(msg);
                break;
        }
    };
    python_cef.updateCustomizePayload = (params) => {
        Object.keys(params).forEach(key => {
            cef.payload[key] = params[key]
        })
    };
    python_cef.updateCefConfig = (key, value) => {
        if (window[sdkModuleName] === undefined) {
            window[sdkModuleName] = {}
        }
        window[sdkModuleName][key] = value;
    };
    python_cef.dispatchCustomEvent = (eventName) => {
        console.info(`dispatchCustomEvent eventName=${eventName}`);
        console.info(customEventMap);
        if (customEventMap[eventName].hooks === 0 &&
            window[moduleName] &&
            typeof window[sdkModuleName].close === 'function') {
            console.info('u will close current window');
            // window[sdkModuleName].close();
        } else {
            window.dispatchEvent(customEventMap[eventName].event)
        }
    };
    cef.addEventListener = (eventName, eventHook) => {
        if (customEventMap[eventName] === undefined) {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook) : eventName 必须是 ${Object.keys(customEventMap)} 中的一个`)
            return;
        }
        if (typeof eventHook !== 'function') {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook): eventHook 必须是一个函数`);
            return;
        }
        customEventMap[eventName].hooks += 1;
        cef.hooks[eventName] = customEventMap[eventName].hooks;
        window.addEventListener(eventName, eventHook);
    };
    cef.removeEventListener = (eventName, eventHook) => {
        if (customEventMap[eventName] === undefined) {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook) : eventName 必须是 ${Object.keys(customEventMap)} 中的一个`)
            return;
        }
        if (typeof eventHook !== 'function') {
            console.error(`window.${sdkModuleName}.addEventListener(eventName, eventHook): eventHook 必须是一个函数`);
            return;
        }
        customEventMap[eventName].hooks -= 1;
        cef.hooks[eventName] = customEventMap[eventName].hooks;
        window.removeEventListener(eventName, eventHook);
    };
    cef.open = (params) => {
        if (window[moduleName] && typeof window[moduleName].open === 'function') {
            window[moduleName].open(params);
        }
    };
    cef.close = () => {
        if (window[moduleName] && typeof window[moduleName]['close_window'] === 'function') {
            window[moduleName]['close_window']();
        }
    };
    cef.closeAll = () => {
        if (window[moduleName] && typeof window[moduleName]['close_all_window'] === 'function') {
            window[moduleName]['close_all_window']();
        }
    };
    cef.toggleFullScreen = () => {
        if (window[moduleName] && typeof window[moduleName]['toggle_full_screen'] === 'function') {
            window[moduleName]['toggle_full_screen']();
        }
    };
    cef.maximize = (uid) => {
        if (typeof uid === 'string') {
            if (window[moduleName] && typeof window[moduleName]['maximize_window'] === 'function') {
                window[moduleName]['maximize_window'](uid);
            }
        } else {
            if (window[moduleName] && typeof window[moduleName]['maximize_current_window'] === 'function') {
                window[moduleName]['maximize_current_window']();
            }
        }
    };
    cef.minimize = (uid) => {
        if (typeof uid === 'string') {
            if (window[moduleName] && typeof window[moduleName]['minimize_window'] === 'function') {
                window[moduleName]['minimize_window'](uid);
            }
        } else {
            if (window[moduleName] && typeof window[moduleName]['minimize_current_window'] === 'function') {
                window[moduleName]['minimize_current_window']();
            }
        }
    };
    cef.focus = (cid) => {
        if (window[moduleName] && typeof window[moduleName]['focus_browser'] === 'function') {
            window[moduleName]['focus_browser'](cid);
        }
    };
    cef.arouse = (cid) => {
        if (window[moduleName] && typeof window[moduleName]['arouse_window'] === 'function') {
            window[moduleName]['arouse_window'](cid);
        }
    };
    cef.setBrowserPayload = (cid, payload) => {
        if (typeof cid !== 'string' || cid === '') {
            console.error('__cef__.setBrowserPayload(cid ,payload): cid 必须为字符类型，且不为空字符串');
            return;
        }
        if (Object.prototype.toString.call(payload) !== '[object Object]') {
            console.error('__cef__.setBrowserPayload(cid ,payload): payload 必须为JsonObject');
            return;
        }
        if (window[moduleName] && typeof window[moduleName]['set_browser_payload'] === 'function') {
            window[moduleName]['set_browser_payload'](cid, payload);
        }

    };
    window[sdkModuleName] = cef;
    window[pythonCallBack] = python_cef;
    window.CEF_HAS_INITIALIZED = true;
}());
"""
