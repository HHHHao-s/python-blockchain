# python-blockchain

#### 介绍
使用python实现简单的区块链


#### 安装教程

1.  打开区块链.py
2.  communicte.py包含了使用所有接口

#### 使用说明

通常，当你打开运行区块链.py,会提示你输入一个端口,回车后会提示你此区块链在网络上开放的地址，你可以使用requests库或Postman对此区块链进行交互


####  API

|API| 使用方法|
|--|--|
| /chain|GET 查看当前区块链
 |/mine|GET 挖矿，创建一个新的区块，并奖励一个币
 |/transactions/new|POST 新建新的交易信息，post一个json数据包括sender,receiver,amount|
 |/nodes/register|POST 注册其他端口，当作网络邻居，保存到当前的服务端，post一个json数据包括nodes   Example:{"nodes":["http://192.168.0.5:5000"]}
 |/nodes/resolve|GET 解决网络上区块链不同的冲突，将最长的有效链复制到当前服务端
 



