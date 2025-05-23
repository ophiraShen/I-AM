# I-AM 前端

这是I-AM项目的前端部分，提供了与后端交互的用户界面。

## 功能

- 实时对话：与AI助手进行自然语言对话
- 肯定语生成：根据您的需求生成个性化肯定语
- 冥想音频：生成并播放定制冥想音频

## 文件结构

- `index.html` - 主HTML文件
- `styles.css` - 样式表
- `app.js` - JavaScript交互逻辑

## 与后端集成

前端通过WebSocket与后端通信，支持以下类型的消息：

1. 普通文本消息 - `message`
2. 用户中断确认 - `interrupt`
3. 进度更新 - `progress`
4. 肯定语内容 - `affirmation`
5. 冥想音频 - `audio`

## 使用方法

1. 在浏览器中访问后端服务URL (例如: `http://localhost:8000/`)
2. 在左侧聊天框中输入消息并按回车或点击发送
3. 如果AI助手建议生成肯定语或冥想音频，会弹出确认窗口
4. 生成的肯定语会显示在右侧上方区域
5. 生成的冥想音频会显示在右侧下方区域，可直接播放 

## 最近修复

### 白屏问题修复 (2024-xx-xx)

解决了在以下情况下出现的白屏问题：
- 点击对话输入框时
- 刷新页面时

修复内容包括：
1. 修正资源路径：由 `/static/app.js` 和 `/static/styles.css` 改为相对路径 `app.js` 和 `styles.css`
2. 改进 WebSocket 连接逻辑
   - 添加断线重连机制
   - 添加错误处理
   - 连接失败时显示友好提示
3. 优化视觉特效以提高性能
   - 减少动画和特效数量
   - 移除页面点击时的流星效果
   - 减少DOM操作
4. 添加适当的错误处理
   - 在各个关键函数中添加 try/catch
   - 错误消息友好显示
5. 修复滚动问题
   - 优化滚动容器设置
   - 添加移动设备支持
6. 消息发送前检查连接状态

这些修改提高了前端页面的稳定性和性能，特别是在网络不稳定的环境下。 