# 吸引力法则App训练数据生成方案

## 一、总体目标
- 数据量：1000条高质量对话
- 质量要求：确保数据可用于模型训练

## 二、数据格式
### 1. 数据结构
```json
{
    "id": "1",
    "dialogue": [
        {
            "role": "user",
            "content": "xxx",
            "annotations": {
                "topic": ["xxx"],
                "intent": ["xxx"],
                "emotion": ["xxx"]
            }
        },
        {
            "role": "assistant",
            "content": "xxx",
            "annotations": {
                "topic": ["xxx"],
                "intent": ["xxx"],
                "tone": ["xxx"],
                "tools": {
                    "technique_type": ["xxx"],
                    "technique_purpose": ["xxx"]
                },
                "dialogue_stage": {
                    "phase": "xxx",
                    "progress_state": "xxx"
                }
            }
        }
    ]
}
```
### 2. 标注维度
- topic：话题
```json
"topic": [
    "career",        // 事业发展、工作压力、职场关系等
    "relationship",  // 感情、婚姻、家庭关系等
    "friendship",    // 朋友关系、社交困扰等
    "health",        // 身心健康、压力管理等
    "study",         // 学业、考试、学习压力等
    "finance",       // 财务问题、理财压力等
    "self_growth",   // 个人成长、自我提升等
    "mental_health", // 情绪管理、心理健康等
    "life_purpose",  // 人生方向、目标规划等
    "family",        // 亲子关系、家庭矛盾等
    "confidence",    // 自信心、自我认同等
    "anxiety",       // 焦虑、恐惧、担忧等
    "work_life_balance", // 工作生活平衡
    "social",        // 社交压力、人际关系等
    "other"          // 其他未分类问题
]
```
- intent：意图
```json
"intent": {
    "user_intent": [
        "seeking_help",           // 寻求帮助
        "expressing_concern",     // 表达担忧
        "sharing_experience",     // 分享经历
        "asking_guidance",        // 请求指导
        "seeking_clarification",  // 寻求解释
        "expressing_doubt",       // 表达怀疑
        "showing_resistance",     // 表现抗拒
        "accepting_guidance",     // 接受指导
        "requesting_tools",       // 请求具体工具/方法
        "following_up"           // 跟进反馈
    ],
    "assistant_intent": [
        "providing_guidance",     // 提供指导
        "offering_comfort",       // 给予安慰
        "giving_explanation",     // 解释说明
        "encouraging",            // 鼓励支持
        "acknowledging_feelings", // 认可感受
        "reframing_perspective", // 重构视角
        "suggesting_practice",   // 建议练习
        "checking_understanding", // 确认理解
        "providing_feedback",    // 提供反馈
        "summarizing_progress"   // 总结进展
    ]
}
```
- emotion/tone：情感
```json
    "user_emotion": [
        // 负面情绪
        "anxious",      // 焦虑的
        "frustrated",   // 沮丧的
        "fearful",      // 恐惧的
        "sad",          // 悲伤的
        "angry",        // 愤怒的
        "overwhelmed",  // 压抑的
        "insecure",     // 不安的
        
        // 中性情绪
        "confused",     // 困惑的
        "neutral",      // 平静的
        "skeptical",    // 怀疑的
        
        // 正面情绪
        "hopeful",      // 充满希望的
        "relieved",     // 释然的
        "grateful",     // 感激的
        "excited",      // 兴奋的
        "confident",    // 自信的
        "peaceful"      // 平和的
    ],
    
    "assistant_tone": [ 
        "gentle",        // 温和的
        "firm",          // 坚定的
        "warm",          // 温暖的
        "professional",  // 专业的
        "patient",       // 耐心的
        "understanding", // 理解的
        "direct",        // 直接的
        "reflective"     // 反思的
    ]
```
- tools：工具
```json
"tools": {
    "technique_type": [
        // 引导练习类
        "guided_meditation",    // 引导冥想
        "breathing_exercise",   // 呼吸练习
        "body_scan",           // 身体扫描
        "visualization",        // 引导想象
        
        // 书写练习类
        "gratitude_journal",   // 感恩日记
        "reflection_journal",  // 反思日记
        "goal_setting",        // 目标设定
        "affirmation_writing", // 肯定宣言
        
        // 对话工具类
        "reframing_dialogue",  // 重构对话
        "inner_child_dialogue", // 内在小孩对话
        "self_inquiry",        // 自我探询
        
        // 行动计划类
        "action_planning",     // 行动规划
        "habit_tracking",      // 习惯追踪
        "progress_review"      // 进展回顾
    ],
    
    "technique_purpose": [
        "emotional_awareness",     // 情绪觉察
        "stress_relief",          // 压力缓解
        "confidence_building",     // 建立自信
        "mindset_shift",          // 思维转变
        "self_discovery",         // 自我发现
        "behavior_change",        // 行为改变
        "relationship_improvement" // 关系改善
    ]
}
```
- dialogue_stage：对话阶段
```json
"dialogue_stage": {
    "phase": [
        // 初始阶段
        "problem_identification",  // 问题识别
        "emotional_expression",    // 情绪表达
        "context_sharing",         // 背景分享
        
        // 探索阶段
        "problem_exploration",     // 问题探索
        "root_cause_analysis",     // 根源分析
        "perspective_examination", // 视角探讨
        
        // 介入阶段
        "tool_introduction",       // 工具介绍
        "technique_guidance",      // 技巧指导
        "practice_engagement",     // 练习参与
        
        // 整合阶段
        "insight_integration",     // 洞察整合
        "action_planning",         // 行动规划
        "progress_review",         // 进展回顾
        
        // 结束阶段
        "summary_reflection",      // 总结反思
        "closure",                 // 对话结束
        "follow_up"               // 后续跟进
    ],
    
    "progress_state": [
        "beginning",     // 开始
        "developing",    // 发展中
        "deepening",     // 深化中
        "concluding",    // 结束中
        "completed"      // 已完成
    ]
}
```

## 三、数据构建
1. 从书中提取高质量内容当作回答模板；
2. 让 AI 根据模板、设计合适的对话场景；
3. 依次生成每个场景的对话数据；
4. 将数据整理成jsonl格式；

## 四、关键点管控
### 1. 质量保证
- 每1000条抽检50条
- 设置关键词检测
- 保持场景均衡性

### 2. 应急预案
- 准备备用API
- 设置断点续传
- 保持实时备份

## 四、验收标准
1. 数据量达到1000条
2. 随机抽检通过率>95%
3. 各场景数据分布均衡
4. 对话轮次平均3-8轮
5. 格式规范统一

---
注：此计划以最高效率为导向，如遇到问题需及时调整策略。