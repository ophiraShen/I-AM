# 个性化冥想引导模块设计

## 一、核心组成部分
1. **引导词生成系统** ✅
2. **语音合成模块** ✅
3. **背景音乐系统** ✅
4. **音频混合器** ✅

## 二、引导词生成结构

### 1. 生成流程
1. 对话分析 -> 冥想大纲生成
2. 大纲扩展 -> 详细引导词脚本
3. 语气标记 -> 带情感标记的脚本
4. TTS合成 -> 最终音频

### 2. 大纲结构
```json
{
    "user_context": {
        "main_goal": "用户的主要目标",
        "current_state": "当前的情绪状态",
        "desired_outcome": "期望达到的效果"
    },
    "script_structure": {
        "opening": {
            "focus": "开场主题",
            "content_brief": "开场内容概要"
        },
        "main_guidance": {
            "segments": [
                {
                    "focus": "段落主题焦点",
                    "content_brief": "内容简要提示"
                }
                // ... 更多段落
            ]
        },
        "closing": {
            "focus": "结束主题",
            "content_brief": "结束内容概要"
        }
    }
}
```

### 3. 脚本结构
```yaml
sequences:
  - id: 0
    text: "引导词文本"
    duration: 3  # 秒
  # ... 更多文本段落
```

## 三、已实现的功能

### 1. 引导词生成系统
```python
def create_meditation_outline(state):
    """基于对话生成冥想大纲"""

def create_meditation_script(state):
    """基于大纲生成详细脚本"""

def create_marked_meditation_script(state):
    """添加语气和情感标记"""
```

主要特性：
- 基于对话内容分析用户需求
- 自动生成个性化冥想大纲
- 结构化的引导词生成
- 智能语气标记系统
- 错误重试机制

### 2. 语音合成系统 (CosyVoice2TTS)
```python
class CosyVoice2TTS:
    def generate_audio(self, texts, voice_type, background_music_type, output_path):
        """生成完整的冥想音频"""
```

主要特性：
- 基于 CosyVoice2 模型的高质量语音合成
- 支持多种声音类型
- 自动处理语音段落和停顿
- 错误重试机制
- 流式处理支持

### 3. 音频处理系统
```python
def _combined_audios(self, text_segments, audio_segments, background_music_type):
    """音频混合处理"""
```

实现功能：
- 背景音乐与语音混合
- 音量自动调节
- 淡入淡出效果
- 自动音频长度匹配
- 防止音频溢出处理

## 四、配置文件结构

### 1. 语音提示配置 (prompts_zero_shot.yaml)
```yaml
prompts:
  speech:
    male1: "path/to/male_voice_sample.wav"
    female1: "path/to/female_voice_sample.wav"
  text:
    male1: "示例文本"
    female1: "示例文本"
background_music:
  bmusic_01: "path/to/background_music_1.wav"
  bmusic_02: "path/to/background_music_2.wav"
```

## 五、使用示例

```python
# 创建冥想处理图
meditation_graph = create_meditation_graph()

# 处理用户对话，生成冥想音频
result = meditation_graph.invoke(NodeResult(data={"conversation": conversation}))
```

## 六、待实现功能

1. **用户反馈系统**
   - 冥想效果评估
   - 用户偏好学习
   - 内容动态调整

## 七、技术栈

### 已使用：
- LangChain (文本生成)
- LangGraph (工作流编排)
- CosyVoice2 (语音合成)
- PyTorch (音频处理)
- TorchAudio (音频处理)
- YAML (配置管理)

## 七、注意事项

1. **音频处理**
   - 确保音频采样率匹配 (16kHz)
   - 控制背景音乐音量 (20%-30%)
   - 添加适当的淡入淡出效果

2. **性能优化**
   - 使用 CUDA 加速 (如可用)
   - 批处理音频生成
   - 缓存常用音频片段

3. **错误处理**
   - 实现音频生成重试机制
   - 记录详细错误日志
   - 提供优雅的降级方案