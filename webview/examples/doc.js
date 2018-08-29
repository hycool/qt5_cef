const __cef__ = window.__cef__;

/**
 * the usage of [__cef__.nestFrame]
 * description: 用于提供一个Native窗口，承载第三方应用或者加载新地址（相当于启动一个新浏览器Tab页），
 *             并将该窗口作为父窗口的自适应跟随窗口，即该窗口的size将跟随父窗口的size变化而变化
 */
__cef__.nestFrame({
    newCid: String, // 必填，表示创建的内嵌窗口的cid
    targetCid: String, // 必填，表示将创建的窗口内嵌到cid = targetCid的目标窗口中
    url: String, // 非必填，如果创建的内嵌窗口需要加载额外的新地址，则url为加载目标地址
    top: Number, // 内嵌窗口距离父窗口顶部像素距离，默认为20逻辑像素
    right: Number, // 内嵌窗口距离父窗口右侧像素距离，默认为20逻辑像素
    bottom: Number, // 内嵌窗口距离父窗口底部像素距离，默认为20逻辑像素
    left: Number, // 内嵌窗口距离父窗口左侧像素距离，默认为20逻辑像素
});