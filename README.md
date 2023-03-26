# biliDanmu
bilibili弹幕解码

## 测试环境
python-3.8.6
requests-2.28.1

## 使用
```python
dr = DmRobot()
dms = dr.fromSegSoUrl(弹幕文件链接)
```
或者
```python
dr = DmRobot()
dms = dr.fromBuffer(弹幕文件bytes)
```

## 其他
根据视频bv号或者视频链接号获取弹幕还没有实现。
网上实现很多，经测试只要获取oid替换`https://api.bilibili.com/x/v2/dm/web/seg.so?type=1&oid=745899804&pid=638907823&segment_index=1&pull_mode=1&ps=120000&pe=360000`即可得到url，再调用`fromsegSoUrl`进行解析即可。
