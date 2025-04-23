#I-AM/project/utils/paths.py
from pathlib import Path
import os
import yaml
from datetime import datetime

class ProjectPaths:
    # 获取项目根目录
    ROOT_DIR = Path(__file__).resolve().parent.parent
    
    # 基础配置文件
    CONFIG_FILE = ROOT_DIR / "backend/config/config.yaml"
    ENV_FILE = ROOT_DIR / ".env"
    TTS_MODEL_DIR = "/root/autodl-fs/cosyvoice/pretrained_models/CosyVoice2-0.5B"
    
    @classmethod
    def load_config(cls) -> dict:
        """加载配置文件"""
        with open(cls.CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def get_path(cls, *paths) -> Path:
        """获取基于项目根目录的路径"""
        return cls.ROOT_DIR.joinpath(*paths)
    
    @classmethod
    def get_prompt_path(cls, module: str, prompt_name: str) -> Path:
        """获取提示词文件路径"""
        config = cls.load_config()
        prompt_path = config[module]['prompts'][prompt_name]
        return cls.get_path('backend', 'agents', 'prompts', prompt_path)
    
    @classmethod
    def get_output_path(cls, module: str, sub_path: str = '') -> Path:
        """获取输出路径"""
        config = cls.load_config()
        base_path = config[module]['output_path']
        return cls.ensure_dir(cls.get_path('backend', 'agents', 'output', base_path, sub_path))
    
    @classmethod
    def get_resource_path(cls, module: str, resource_path: str) -> Path:
        """获取资源文件路径"""
        return cls.get_path('backend', 'agents', 'resources', module, resource_path)
    
    @classmethod
    def ensure_dir(cls, path: Path) -> Path:
        """确保目录存在"""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def get_timestamp_path(cls, base_dir: Path, timestamp: str = None, suffix: str = ".yaml") -> Path:
        """获取带时间戳的文件路径"""
        cls.ensure_dir(base_dir)
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return base_dir / f"{timestamp}{suffix}"