# I-AM/project/backend/agents/meditation_tts.py

import sys
# 添加必要的系统路径
sys.path.append("/root/autodl-tmp/I-AM/CosyVoice")
sys.path.append("/root/autodl-tmp/I-AM/CosyVoice/third_party/Matcha-TTS")

import yaml
import torch
import torchaudio
from tqdm import tqdm
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav

class CosyVoice2TTS:
    def __init__(self, model_path, prompts_config_path):
        """
        初始化 TTS 系统
        
        Args:
            model_path: CosyVoice2 模型路径
            prompts_config_path: 提示配置文件路径
        """
        self.cosyvoice = CosyVoice2(
            model_path,
            load_jit=True,
            load_onnx=False,
            load_trt=False
        )
        with open(prompts_config_path, 'r', encoding='utf-8') as file:
            self.prompts_config = yaml.safe_load(file)

    def generate_audio(
        self,
        texts,
        voice_type,
        background_music_type,
        output_path,
        speed=1.0,
        stream=False,
        music_volume=0.2,
        music_extension_duration=30,
        fade_in_duration=5,
        fade_out_duration=10,
        max_retries=3
    ):
        """
        生成完整的冥想音频，包含语音和背景音乐
        
        Args:
            texts_path: 文本配置文件路径
            voice_type: 声音类型
            background_music_type: 背景音乐类型
            output_path: 输出文件路径
            speed: 语速
            stream: 是否流式处理
            music_volume: 背景音乐音量
            music_extension_duration: 音乐延长时间
            fade_in_duration: 淡入时间
            fade_out_duration: 淡出时间
            max_retries: 最大重试次数
        """

        if isinstance(texts, str):
            with open(texts, 'r', encoding='utf-8') as file:
                text_segments = yaml.safe_load(file)['sequences']
        else:
            text_segments = texts['sequences']

        prompt_speech_16k = load_wav(self.prompts_config['prompts']['speech'][voice_type], 16000)
        prompt_text = self.prompts_config['prompts']['text'][voice_type]

        total_len = len(text_segments)

        success = False
        attempt = 0

        while not success and attempt < max_retries:
            attempt += 1
            audio_segments = [None] * total_len
            failed = False

            print(f"Attempt {attempt} of {max_retries}")
            # 创建进度条
            pbar = tqdm(total=total_len, desc="Generating audio segments")

            for idx in range(total_len):
                audio = self._generate_single(
                    text_segments[idx]['text'],
                    prompt_text,
                    prompt_speech_16k
                )
                if audio is None:
                    print(f"\nFailed to generate audio for segment {idx}, retrying entire sequence...")
                    failed = True
                    pbar.close()
                    break

                audio_segments[idx] = audio
                pbar.update(1)
            if not failed:
                success = True
                pbar.close()

            if not success and attempt == max_retries:
                raise Exception("Failed to generate all audio segments after maximum retries")

        print("Combining audio segments with background music...")

        combined_audio = self._combined_audios(
            text_segments,
            audio_segments,
            background_music_type,
            music_extension_duration,
            fade_in_duration,
            fade_out_duration
        )

        print(f"Saving final audio to {output_path}")

        torchaudio.save(
            output_path,
            combined_audio,
            self.cosyvoice.sample_rate
        )

        print("Audio generation completed!")


    def _generate_single(self, text, prompt_text, prompt_speech_16k, speed=1.0, stream=False):
        """生成单个音频片段"""
        try:
            with torch.inference_mode(), torch.amp.autocast('cuda'):
                for i, output in enumerate(self.cosyvoice.inference_zero_shot(
                    text,
                    prompt_text,
                    prompt_speech_16k,
                    speed=speed,
                    stream=stream
                )):
                    audio = output['tts_speech']
                    return audio
        except Exception as e:
            print(f"Error generating audio for text: {text}")
            print(str(e))
            return None

    def _combined_audios(
        self,
        text_segments,
        audio_segments,
        background_music_type,
        music_extension_duration=30,
        fade_in_duration=5,
        fade_out_duration=10
    ):
        """合并音频片段并添加背景音乐"""
        combined_audio = self._generate_silence(fade_in_duration)
        for i, audio in enumerate(audio_segments):
            silence = self._generate_silence(text_segments[i]['duration'])
            combined_audio = torch.cat([combined_audio, audio, silence], dim=1)
        
        music_extension_samples = self._generate_silence(music_extension_duration)
        combined_audio =  torch.cat([combined_audio, music_extension_samples], dim=1)

        background_music, bg_sample_rate = torchaudio.load(self.prompts_config['background_music'][background_music_type])

        if background_music.shape[0] > 1:
            background_music = torch.mean(background_music, dim=0, keepdim=True)

        if bg_sample_rate != self.cosyvoice.sample_rate:
            resampler = torchaudio.transforms.Resample(bg_sample_rate, self.cosyvoice.sample_rate)
            background_music = resampler(background_music)

        # 调整背景音乐的长度以匹配语音长度
        target_length = combined_audio.shape[1]
        if background_music.shape[1] > target_length:
            # 如果背景音乐更长，截取需要的部分
            background_music = background_music[:, :target_length]
        elif background_music.shape[1] < target_length:
            # 如果背景音乐更短，循环播放直到达到所需长度
            num_repeats = (target_length + background_music.shape[1] - 1) // background_music.shape[1]
            background_music = background_music.repeat(1, num_repeats)
            background_music = background_music[:, :target_length]

        fade_in_samples = fade_in_duration * self.cosyvoice.sample_rate
        fade_out_samples = fade_out_duration * self.cosyvoice.sample_rate

        fade_in_curve = self._create_fade_curve(fade_in_samples, fade_in_samples, fade_in=True)
        fade_out_curve = self._create_fade_curve(fade_out_samples, fade_out_samples, fade_in=False)

        background_music[0, :fade_in_samples] *= fade_in_curve
        background_music[0, -fade_out_samples:] *= fade_out_curve

        # 调整背景音乐的音量（这里设置为语音的20%音量）
        background_volume = 0.3
        background_music = background_music * background_volume

        # 混合语音和背景音乐
        final_audio = combined_audio + background_music

        # 防止音频溢出（可选）
        if torch.max(torch.abs(final_audio)) > 1:
            final_audio = final_audio / torch.max(torch.abs(final_audio))

        return final_audio

        
    def _generate_silence(self, silence_duration):
        """生成静音片段"""
        return torch.zeros(1, silence_duration * self.cosyvoice.sample_rate)

    def _create_fade_curve(self, length, fade_length, fade_in=True):
        """创建淡入淡出曲线"""
        if fade_in:
            return torch.linspace(0, 1, fade_length)
        else:
            return torch.linspace(1, 0, fade_length)

# 使用示例
if __name__ == "__main__":
    

    # 初始化 TTS 系统
    tts = CosyVoice2TTS(
        model_path='/root/autodl-fs/cosyvoice/pretrained_models/CosyVoice2-0.5B',
        prompts_config_path='/root/autodl-tmp/I-AM/project/backend/agents/prompts/meditation/tts/zero_shot.yaml'
    )

    # 生成音频
    tts.generate_audio(
        texts="/root/autodl-tmp/I-AM/project/backend/agents/jupyter/output/script/exam.yaml",
        voice_type="female1",
        background_music_type="bmusic_02",
        output_path="/root/autodl-tmp/I-AM/project/backend/agents/jupyter/output/tts/exam.wav"
    )