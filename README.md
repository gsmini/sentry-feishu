# sentry_feishu_gsmini

`Sentry`的`飞书`通知插件

## 适用sentry版本24.10.0
```shell
当前版本只在24.10.0试过，由于老版本(10.0等)插件实现方式和当前新的不一样，所以才有的这个项目
```
## 安装

```bash
git clone  https://github.com/getsentry/self-hosted.git

cd  self-hosted/
cp enhance-image.example.sh enhance-image.sh 
chmod 777 enhance-image.sh # 如果不改权限 本地文件copy到容器内后过可能无法执行
```
enhance-image.sh 内容如下
```shell
#!/bin/bash
set -euo pipefail
pip install sentry_feishu_gsmini=1.14 # 安装插件pip包

```
> 官方说明： https://develop.sentry.dev/self-hosted/#enhance-sentry-image

## 使用

### 进入项目设置
![img.png](doc-images/project-setting.png)

### 点击 Legacy Integrations打开飞书插件开关
![img.png](doc-images/integrations.png)

### 刷新页面后看到有飞书插件后，点击进入填写飞书webhook
![img.png](doc-images/webhook-url.png)

### 触发错误后飞书群聊收到机器人消息
![img.png](doc-images/feishu.png)

 