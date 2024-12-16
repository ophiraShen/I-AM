# 个性化冥想引导模块设计

## 一、核心组成部分
1. **引导词生成系统**
2. **语音合成模块**
3. **背景音乐系统**
4. **音频混合器**

## 二、引导词生成结构
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
        },
        "background_music": {
            "type": "peaceful",
            "volume": 0.3,
            "fade_in": 5,
            "fade_out": 5
        }
    }
}
```

## 三、实现流程

### 1. 引导词生成
```python
class MeditationScriptGenerator:
    def generate_script(self, user_context, chat_history):
        # 基于用户上下文生成个性化引导词
        script = self.model.generate(
            user_context=user_context,
            chat_history=chat_history,
            template=self.get_script_template()
        )
        return self.format_script(script)
```

### 2. 语音合成
```python
class VoiceSynthesizer:
    def synthesize(self, script):
        # 使用Azure或其他TTS服务
        voice_segments = []
        for segment in script['script_structure']:
            audio = self.tts_service.synthesize(
                text=segment['content'],
                voice_style="meditation",  # 平静、舒缓的语音风格
                speaking_rate=0.8  # 稍慢的语速
            )
            voice_segments.append(audio)
        return voice_segments
```

### 3. 音频处理
```python
class AudioProcessor:
    def create_meditation_audio(self, voice_segments, background_music):
        # 混合语音和背景音乐
        final_audio = AudioMixer.mix(
            voice=voice_segments,
            music=background_music,
            voice_volume=1.0,
            music_volume=0.3,
            crossfade_duration=2
        )
        return final_audio
```

## 四、个性化要素

### 1. 内容个性化
- 根据用户目标调整引导词
- 融入用户个人情况
- 使用用户熟悉的场景

### 2. 语音个性化
- 根据用户性别选择声音
- 调整语速和语调
- 控制停顿和重音

### 3. 音乐个性化
- 根据目标选择风格
- 调整音量和节奏
- 匹配用户偏好

## 五、示例场景

### 考试准备场景
```json
{
    "user_context": {
        "goal": "通过考试",
        "stress_point": "记忆力不好",
        "preferred_duration": 4
    },
    "generated_script": {
        "opening": "找到一个舒适的位置，让我们开始这段考前冥想之旅...",
        "main_content": [
            "感受你的呼吸，每一次呼气都带走紧张...",
            "想象知识如同温暖的光芒，自然地流入你的大脑...",
            "看到自己在考场上，平静而自信地答题..."
        ],
        "closing": "带着这份平静和自信，让我们结束这次冥想..."
    }
}
```

## 六、技术选型建议

1. **语音合成**
   - Azure TTS
   - Google Cloud TTS
   - 阿里云语音合成

2. **背景音乐**
   - 自然音效库
   - 冥想音乐库
   - 动态音乐生成

3. **音频处理**
   - FFmpeg
   - PyDub
   - SoX