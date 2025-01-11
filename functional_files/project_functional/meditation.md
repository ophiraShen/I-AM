# 个性化冥想引导模块设计

## 一、核心组成部分
1. **引导词生成系统** (待实现)
2. **语音合成模块** ✅
3. **背景音乐系统** ✅
4. **音频混合器** ✅

## 二、引导词生成结构

1. 引导词提纲
```json
{
    "meditation_script": {
        "user_context": {
            "main_goal": "通过考试",
            "current_stress": "学习压力大",
            "preferred_duration": 4  // 分钟
        },
        "script_structure": {
            "opening": {
                "duration": 30,  // 秒
                "content": "让我们找到一个舒适的姿势，深深地呼吸..."
            },
            "main_guidance": {
                "duration": 180,  // 秒
                "segments": [
                    {
                        "focus": "放松身心",
                        "content": "感受每一次呼吸带来的平静...",
                        "duration": 45
                    },
                    {
                        "focus": "目标可视化",
                        "content": "想象你正坐在考场中，感受知识自然流动...",
                        "duration": 90
                    },
                    {
                        "focus": "信心建立",
                        "content": "你已经为考试做了充分的准备...",
                        "duration": 45
                    }
                ]
            },
            "closing": {
                "duration": 30,  // 秒
                "content": "慢慢地，让我们带着这份平静和自信回到当下..."
            }
        }
    }
}
```

## 三、已实现的功能

### 1. 语音合成系统 (CosyVoice2TTS)
```python
class CosyVoice2TTS:
    def __init__(self, model_path, prompts_config_path):
        """初始化语音合成系统"""
        
    def generate_audio(self, texts_path, voice_type, background_music_type, output_path):
        """生成完整的冥想音频"""
```

主要特性：
- 基于 CosyVoice2 模型的高质量语音合成
- 支持多种声音类型
- 自动处理语音段落和停顿
- 错误重试机制
- 流式处理支持

### 2. 音频处理系统
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

### 2. 冥想文本配置 (meditation_texts.yaml)
```yaml
sequences:
  - text: "让我们开始今天的冥想..."
    duration: 3
  - text: "深深地吸一口气..."
    duration: 2
  # ... 更多文本段落
```

## 五、使用示例

```python
# 初始化 TTS 系统
tts = CosyVoice2TTS(
    model_path='path/to/CosyVoice2-0.5B',
    prompts_config_path='path/to/prompts_zero_shot.yaml'
)

# 生成冥想音频
tts.generate_audio(
    texts_path="path/to/meditation_texts.yaml",
    voice_type="male1",
    background_music_type="bmusic_01",
    output_path="path/to/output/meditation.wav"
)
```

## 六、待实现功能

1. **引导词生成系统**
   - 基于用户目标的文本生成
   - 情感分析和适应
   - 个性化内容调整

2. **用户反馈系统**
   - 冥想效果评估
   - 用户偏好学习
   - 内容动态调整

## 七、技术栈

### 已使用：
- CosyVoice2 (语音合成)
- PyTorch (音频处理)
- TorchAudio (音频处理)
- YAML (配置管理)

### 计划使用：
- LLM (文本生成)
- Sentiment Analysis (情感分析)
- FastAPI (API 服务)

## 八、注意事项

1. **音频处理**
   - 确保音频采样率匹配 (16kHz)
   - 控制背景音乐音量 (建议 20%-30%)
   - 添加适当的淡入淡出效果

2. **性能优化**
   - 使用 CUDA 加速 (如可用)
   - 批处理音频生成
   - 缓存常用音频片段

3. **错误处理**
   - 实现音频生成重试机制
   - 记录详细错误日志
   - 提供优雅的降级方案