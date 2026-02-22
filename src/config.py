"""
配置文件
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "Feishu AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 飞书配置
    FEISHU_APP_ID: str = os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET: str = os.getenv("FEISHU_APP_SECRET", "")
    FEISHU_BASE_URL: str = os.getenv("FEISHU_BASE_URL", "https://open.feishu.cn")
    FEISHU_API_TIMEOUT: int = int(os.getenv("FEISHU_API_TIMEOUT", "30"))
    FEISHU_RETRY_COUNT: int = int(os.getenv("FEISHU_RETRY_COUNT", "3"))
    
    # Webhook配置
    FEISHU_WEBHOOK_VERIFICATION_TOKEN: str = os.getenv("FEISHU_WEBHOOK_VERIFICATION_TOKEN", "")
    FEISHU_WEBHOOK_ENCRYPT_KEY: str = os.getenv("FEISHU_WEBHOOK_ENCRYPT_KEY", "")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/feishu_assistant")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS配置
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # 监控配置
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def validate_config():
    """验证配置"""
    errors = []
    
    # 检查飞书配置
    if not settings.FEISHU_APP_ID:
        errors.append("FEISHU_APP_ID 未配置")
    if not settings.FEISHU_APP_SECRET:
        errors.append("FEISHU_APP_SECRET 未配置")
    
    # 检查Webhook配置
    if not settings.FEISHU_WEBHOOK_VERIFICATION_TOKEN:
        print("警告: FEISHU_WEBHOOK_VERIFICATION_TOKEN 未配置，Webhook验证将跳过")
    
    if errors:
        raise ValueError(f"配置错误: {', '.join(errors)}")
    
    print(f"✅ 配置验证通过: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   飞书App ID: {settings.FEISHU_APP_ID[:8]}...")
    print(f"   Webhook验证: {'已配置' if settings.FEISHU_WEBHOOK_VERIFICATION_TOKEN else '未配置'}")
    print(f"   调试模式: {settings.DEBUG}")
    
    return True


if __name__ == "__main__":
    # 测试配置
    try:
        validate_config()
    except ValueError as e:
        print(f"❌ {e}")