# I-AM 小程序开发文档

## 一、开发环境准备
1. **必要工具**
   - 微信开发者工具
   - VSCode (推荐编辑器)
   - Git (版本控制)

2. **小程序账号**
   - 注册小程序开发账号
   - 获取 AppID
   - 配置开发者权限

## 二、项目结构
```
miniprogram/
├── pages/                    # 页面文件
│   ├── index/               # 首页
│   │   ├── index.js        # 逻辑
│   │   ├── index.wxml      # 结构
│   │   ├── index.wxss      # 样式
│   │   └── index.json      # 配置
│   ├── chat/               # 对话页
│   ├── affirmation/        # 肯定语页
│   └── meditation/         # 冥想页
├── components/             # 公共组件
│   ├── chat-item/         # 聊天气泡组件
│   ├── audio-player/      # 音频播放组件
│   └── loading/           # 加载组件
├── images/                # 图片资源
├── utils/                 # 工具函数
│   ├── request.js        # 网络请求
│   ├── websocket.js      # WebSocket封装
│   └── storage.js        # 存储工具
├── services/             # API服务
│   ├── chat.js          # 对话相关
│   ├── affirmation.js   # 肯定语相关
│   └── meditation.js    # 冥想相关
├── app.js               # 小程序入口
├── app.json            # 全局配置
└── app.wxss            # 全局样式
```

## 三、页面功能说明

### 1. 首页 (index)
- 功能导航菜单
- 用户信息展示
- 最近对话记录
- 快捷功能入口

### 2. 对话页面 (chat)
- 聊天界面
  - 消息气泡
  - 输入框
  - 发送按钮
- WebSocket连接状态
- 历史消息加载
- 错误重试机制

### 3. 肯定语页面 (affirmation)
- 肯定语卡片展示
- 保存/收藏功能
- 分享功能
- 生成新的肯定语

### 4. 冥想页面 (meditation)
- 音频播放器
- 播放控制
- 进度显示
- 背景图切换

## 四、开发流程

### 1. 基础框架搭建 (2天)
- [x] 创建项目
- [ ] 配置基础页面
- [ ] 实现导航
- [ ] 搭建组件框架

### 2. 核心功能开发 (3天)
- [ ] WebSocket通信
- [ ] 对话功能
- [ ] 音频播放
- [ ] 数据存储

### 3. 界面优化 (2天)
- [ ] UI美化
- [ ] 交互动画
- [ ] 加载状态
- [ ] 错误提示

## 五、API接口

### 1. WebSocket
```javascript
// 连接地址
ws://your-domain.com/ws/chat

// 消息格式
{
  type: 'text|image|audio',
  content: string,
  timestamp: number
}
```

### 2. HTTP接口
```javascript
// 获取肯定语
GET /api/affirmations

// 获取冥想音频
GET /api/meditation/audio

// 用户信息
GET /api/user/info
```

## 六、开发注意事项

### 1. 性能优化
- 合理使用分包加载
- 图片资源压缩
- 避免频繁重渲染
- 及时销毁不需要的事件监听

### 2. 体验优化
- 添加加载提示
- 骨架屏加载
- 下拉刷新
- 触底加载更多

### 3. 安全考虑
- 数据加密传输
- 敏感信息脱敏
- 防止XSS攻击
- 控制API调用频率

## 七、发布流程
1. 完整测试
2. 代码审查
3. 打包上传
4. 提交审核
5. 灰度发布
6. 正式上线

## 八、后续优化
1. 性能监控
2. 错误日志
3. 用户反馈
4. 新功能规划 