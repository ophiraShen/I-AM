from pathlib import Path
import os

class ProjectPaths:
    # 获取项目根目录路径
    ROOT_DIR = Path(__file__).resolve().parent
    
    # 定义常用的目录路径
    DATA_DIR = ROOT_DIR / 'data'
    SCRIPTS_DIR = DATA_DIR / 'scripts'
    
    @classmethod
    def get_project_path(cls, *paths) -> Path:
        """获取项目中的文件路径
        
        Args:
            *paths: 相对于项目根目录的路径部分
            
        Returns:
            完整的文件路径
        """
        return cls.ROOT_DIR.joinpath(*paths)
    
    @classmethod
    def get_data_path(cls, *paths) -> Path:
        """获取数据目录中的文件路径
        
        Args:
            *paths: 相对于data目录的路径部分
            
        Returns:
            完整的文件路径
        """
        return cls.DATA_DIR.joinpath(*paths)
    
    @classmethod
    def ensure_dir(cls, *paths) -> Path:
        """确保目录存在，如果不存在则创建
        
        Args:
            *paths: 相对于项目根目录的路径部分
            
        Returns:
            目录路径
        """
        dir_path = cls.get_project_path(*paths)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
