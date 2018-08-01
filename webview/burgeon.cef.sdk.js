(function () {
    const moduleName = 'windowInstance';
    const sdkModuleName = '__cef__';
    const cef = {
        payload: {},
        hooks: {}
    };
    const customEventMap = {
        windowCloseEvent: {
            name: 'windowCloseEvent',
            event: new CustomEvent('windowCloseEvent', {detail: {windowId: window.windowId}}),
            hooks: 0
        }
    };
    cef.dispatchCustomEvent = (eventName) => {
        if (customEventMap[eventName].hooks === 0 &&
            window[moduleName] &&
            typeof window[sdkModuleName].close === 'function') {
            window[sdkModuleName].close();
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
    cef.console = (msg, type) => {
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
    cef.initializeCustomizePayload = (params) => {
        Object.keys(params).forEach(key => {
            cef.payload[key] = params[key]
        })
    };
    cef.updateWindowInstance = (key, value) => {
        if (window[moduleName] === undefined) {
            window[moduleName] = {}
        }
        window[moduleName][key] = value;
    };
    cef.updateCefConfig = (key, value) => {
        if (window[sdkModuleName] === undefined) {
            window[sdkModuleName] = {}
        }
        window[sdkModuleName][key] = value;
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
    window[sdkModuleName] = cef;
}());