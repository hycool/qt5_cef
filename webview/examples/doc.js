const __cef__ = window.__cef__;

// [__cef__ ~ Properties:]
/*

__cef__.wid        String  wid(window id)    用于唯一标识一个浏览器窗口，每个浏览器窗口有且只有全局唯一的wid
__cef__.cid        String  cid(customize id) 用于唯一标识一个浏览器窗口，每个浏览器窗口有且只应该有全局唯一的cid
__cef__.widLists   Array   widLists记录着应用程序运行期间，所有活动窗口的wid列表，e.g [ 'master', 'child_1', 'child_2', '...' ]
__cef__.cidLists   Array   cidLists记录着应用程序运行期间，所有活动窗口的cid列表，e.g [ 'master', 'child_1', 'child_2', '...' ]
__cef__.hooks      Object  hooks(cef event listener hooks) 表示当前窗口中，所有通过__cef__.addEventListener方法添加的指定事件的事件监听器的数量。
                   e.g  hooks: Object
                          windowBroadcastEvent: 1
                          windowCloseEvent: 1
                   说明：
                   目前系统内置了两种事件类型，对同一事件类型，可以绑定多个事件监听器。
                   windowBroadcastEvent：窗口广播事件，使用__cef__.addEventListener监听该事件，当系统产生广播行为时，会触发相对应的回调函数。
                   windowCloseEvent：窗口关闭事件，使用__cef__.addEventListener监听该事件，当窗口关闭时，会触发相对应的回调。
                   需要注意的是，如果在窗口中为该事件添加了事件监听器，那么系统会默认阻止窗口关闭行为，用户要关闭窗口必须在回调中主动调用相对应的窗口关闭方法。
__cef__.payload    Object  payload(挂载数据)，用于在窗口间传递数据。当从A窗口，调用__cef__.open(params)方法打开新窗口B时，如果B想获取从A传递过来的数据，则取该值。

* */


// -------------------------------------------------------------------------------------------------------------------------------------------
// [__cef__ ~ Functions:]
/***
 * Function Name: __cef__.nestFrame(params:JsonObject)
 * description: 用于提供一个Native窗口，承载第三方应用或者加载新地址（相当于启动一个新浏览器Tab页），
 *             并将该窗口作为父窗口的自适应跟随窗口，即该窗口的size将跟随父窗口的size变化而变化
 */


/**
 * Function Name: __cef__.nestFrame(params:JsonObject)
 * description: 用于提供一个Native窗口，承载第三方应用或者加载新地址（相当于启动一个新浏览器Tab页），
 *             并将该窗口作为父窗口的自适应跟随窗口，即该窗口的size将跟随父窗口的size变化而变化
 */
__cef__.nestFrame({
    newCid: String,    // 必填，表示创建的内嵌窗口的cid
    targetCid: String, // 必填，表示将创建的窗口内嵌到cid = targetCid的目标窗口中
    url: String,       // 非必填，如果创建的内嵌窗口需要加载额外的新地址，则url为加载目标地址
    top: Number,       // 内嵌窗口距离父窗口顶部像素距离，默认为0逻辑像素
    right: Number,     // 内嵌窗口距离父窗口右侧像素距离，默认为0逻辑像素
    bottom: Number,    // 内嵌窗口距离父窗口底部像素距离，默认为0逻辑像素
    left: Number,      // 内嵌窗口距离父窗口左侧像素距离，默认为0逻辑像素
});