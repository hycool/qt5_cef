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
 * Function Name: __cef__.addEventListener(eventName:String, eventHook:Function)
 * description: 将eventHook注册到eventName上（当eventName对应的系统事件触发时候，会调用eventHook）
 */
const eventHook = () => { console.log('event hook test') };
__cef__.addEventListener('windowCloseEvent', eventHook);


/***
 * Function Name: __cef__.removeEventListener(eventName:String, eventHook:Function)
 * description: 移除注册在eventName上的eventHook监听器（监听函数）
 */
const eventHook = () => { console.log('event hook test') };
__cef__.removeEventListener('windowCloseEvent', eventHook);


/***
 * Function Name: __cef__.show(cid:String)
 * description: 将指定cid所对应的窗口，从隐藏状态（hide）切换为普通显示状态（show）
 */
__cef__.show(); // 无参调用，显示当前窗口
__cef__.show('the_string_of_cid'); // 携参调用，显示指定cid标识的窗口

/***
 * Function Name: __cef__.hide(cid:String)
 * description: 将指定cid所对应的窗口，从普通显示状态（show）切换为隐藏状态（hide）
 */
__cef__.hide(); // 无参调用，隐藏当前窗口
__cef__.hide('the_string_of_cid'); // 携参调用，隐藏指定cid标识的窗口


/***
 * Function Name: __cef__.focus(cid:String)
 * description: 使得指定cid对应的窗口获取焦点。
 */
__cef__.focus(); // 无参调用，使得当前窗口获得焦点
__cef__.focus('the_string_of_cid'); // 携参调用，使得指定cid标识的窗口获得焦点


/***
 * Function Name: __cef__.arouse(cid:String)
 * description: 将指定cid所对应的窗口唤起，并置为顶层窗口。（假设B窗口此时处于最小化状态，或者被A窗口遮挡住了，调用此方法可以将B窗口唤起）
 */
__cef__.arouse(); // 无参调用，唤起当前窗口
__cef__.arouse('the_string_of_cid'); // 携参调用，唤起指定cid标识的窗口


/***
 * Function Name: __cef__.open(params:JsonObject)
 * description: 打开一个新窗口
 */
__cef__.open({
    url: String,         // 必填，打开新窗口需要加载的url地址
    title: String,       // 非必填，设置打开新窗口的标题
    payload: Object,     // 非必填，表示将要传递给新窗口的初始挂载数据，以供新窗口使用。payload中的属性值可为除了Function以外的任何类型。
    cid: String,         // 非必填，新窗口将以cid作为唯一标识之一。如果不填，则新建窗口的cid默认等于wid，窗口的wid由系统自动生成，用户无法指定。
    maximized: Boolean,  // 非必填，表示新窗口打开后是否是最大化。默认False
    minimized: Boolean,  // 非必须，表示新窗口打开后是否是最小化。默认False
    width: Number,       // 非必填，新窗口打开后的宽度。需要注意的是，如果指定了宽度，必须同时指定高度。
    height: Number,      // 非必填，新窗口打开后的高度。需要注意的是，如果指定了高度，必须同时指定宽度。
    enableMax: Boolean   // 非必须，控制新窗口是否允许最大化。True表示允许，False表示禁止。默认是允许。
});


/***
 * Function Name: __cef__.close(cidLists:Array)
 * description: 关闭窗口
 */
__cef__.close();  // 无惨调用表示关闭当前窗口本身。
__cef__.close(['cid-one', 'cid-two', 'cid-N']);  // 携参调用，表示关闭['cid-one', 'cid-two', 'cid-N']中的窗口。


/***
 * Function Name: __cef__.closeAll()
 * description: 关闭所有窗口（当所有窗口关闭时，应用程序将自动终止）
 */
__cef__.closeAll();


/***
 * Function Name: __cef__.toggleFullScreen()
 * description: 切换当前窗口的全屏状态
 */
__cef__.toggleFullScreen();


/***
 * Function Name: __cef__.setBrowserPayload(cid:String, payload:JsonObject)
 * description: 更新指定cid所标识的窗口的payload数据。例如在A窗口调用此方法更新B窗口的数据。
 *              如果B窗口的__cef__.payload中已经存在同名属性，则覆盖。
 *              注意：payload的属性值不能为函数类型。
 */
__cef__.setBrowserPayload('the_cid_of_target_window', {
    payload_property_string: '',
    payload_property_number: 1,
    payload_property_object: {},
    payload_property_array: [],
    payload_property_boolean: true
});


/***
 * Function Name: __cef__.broadCast(eventData:JsonObject)
 * description: 顾名思义，该方法用于在窗口中广播，并可以携带广播数据eventData。
 *              所有为windowBroadcastEvent注册了事件监听器的窗口，都可以接收到广播行为，并获取广播数据。
 *              注意：eventData中的属性值不能为函数类型。
 */
// Step 1 :  假设A窗口进行广播行为
__cef__.broadCast({
    event_data_string: '',
    event_data_number: 1,
    event_data_object: {},
    event_data_array: [],
    event_data_boolean: true
});
// Step 2 : B窗口为windowBroadcastEvent广播事件注册事件监听函数，通过e.detail.eventData获取广播数据。
const broadCastEventHook = (e) => {
    console.log(e.detail.eventData); // 可以通过e.detail.eventData获取广播行为所携带的数据。
};
__cef__.addEventListener('windowBroadcastEvent', broadCastEventHook);


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