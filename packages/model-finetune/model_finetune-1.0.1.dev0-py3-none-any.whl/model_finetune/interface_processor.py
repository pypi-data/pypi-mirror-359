#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
接口处理器 - 为固定接口提供统一的处理方法

这个模块提供了一个简洁的接口，供外部固定接口调用。
所有复杂的业务逻辑都封装在这里，保持固定接口的简洁性。
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime

# 导入包内模块
from .downloader import ResourceDownloader
from .validators import InputValidator, ValidationError
from .exceptions import ExceptionHandler, convert_to_standard_exception

logger = logging.getLogger(__name__)


class InterfaceProcessor:
    """
    接口处理器 - 为固定接口提供统一的处理方法
    
    这个类封装了所有复杂的业务逻辑，为固定接口提供简洁的调用方式。
    """
    
    def __init__(self, output_dir: str = "./processor_output", logger: Optional[logging.Logger] = None):
        """
        初始化处理器
        
        Args:
            output_dir: 输出目录路径
            logger: 外部传入的日志器，如果为None则使用默认日志器
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用传入的日志器或创建默认日志器
        self.logger = logger if logger is not None else logging.getLogger(__name__)
    
    def process_from_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从配置字典处理数据并返回标准化结果
        
        Args:
            config: 包含file_url和measure_data的配置字典
            
        Returns:
            标准化的处理结果字典
        """
        try:
            self.logger.info("开始处理数据配置")
            
            # 使用统一的输入验证器
            try:
                # 验证配置字典
                validated_config = InputValidator.validate_config_dict(
                    config, 
                    required_keys=["file_url", "measure_data"]
                )
                
                zip_url = validated_config["file_url"]
                measure_url = validated_config["measure_data"]
                
                # 验证URL格式
                if self._looks_like_url(zip_url):
                    InputValidator.validate_url(zip_url)
                if self._looks_like_url(measure_url):
                    InputValidator.validate_url(measure_url)
                    
            except ValidationError as e:
                return self._create_error_result(f"输入验证失败: {str(e)}")
            
            self.logger.info(f"处理数据源: {zip_url}")
            self.logger.info(f"测量数据: {measure_url}")
            
            # 创建下载目录
            downloads_dir = self.output_dir / "downloads"
            downloads_dir.mkdir(exist_ok=True)
            
            # 下载文件
            downloader = ResourceDownloader(str(downloads_dir))
            
            self.logger.info("开始下载ZIP文件...")
            zip_path = downloader.download(zip_url)
            if not zip_path:
                return self._create_error_result("ZIP文件下载失败")
            
            self.logger.info("开始下载测量数据文件...")
            csv_path = downloader.download(measure_url)
            if not csv_path:
                return self._create_error_result("测量数据文件下载失败")
            
            self.logger.info(f"文件下载完成: ZIP={zip_path}, CSV={csv_path}")
            
            # 调用核心处理函数 (延迟导入避免循环依赖)
            from .main import process_data
            result = process_data(zip_path=zip_path, measure_data_path=csv_path)
            
            # 处理结果并加密保存
            if result:
                # 提取模型结果
                if isinstance(result, tuple) and len(result) >= 1:
                    model_result = result[0]
                else:
                    model_result = result
                
                # 加密保存模型结果
                encrypted_path = self._encrypt_and_save_model(model_result)
                
                return self._create_success_result(
                    model_path=encrypted_path,
                    message="数据处理和模型训练成功完成"
                )
            else:
                return self._create_error_result("模型训练失败")
                
        except Exception as e:
            # 使用统一的异常处理器
            handler = ExceptionHandler(self.logger)
            standard_exception = convert_to_standard_exception(e)
            error_info = handler.handle_exception(standard_exception, "接口数据处理")
            
            return {
                "success": False,
                "timestamp": self._get_timestamp(),
                **error_info
            }
    
    def _encrypt_and_save_model(self, model_result: Any) -> Optional[str]:
        """
        加密并保存模型结果
        
        Args:
            model_result: 模型结果对象
            
        Returns:
            加密文件的路径，失败返回None
        """
        if not model_result:
            return None
            
        try:
            # 导入加密相关模块
            from autowaterqualitymodeler.utils.encryption import encrypt_data_to_file
            
            # 创建模型保存目录
            models_dir = self.output_dir / "models"
            models_dir.mkdir(exist_ok=True)
            
            # 获取加密配置
            encryption_config = self._get_encryption_config()
            
            # 加密保存
            encrypted_path = encrypt_data_to_file(
                data_obj=model_result,
                password=encryption_config['password'],
                salt=encryption_config['salt'],
                iv=encryption_config['iv'],
                output_dir=str(models_dir),
                logger=self.logger,
            )
            
            if encrypted_path:
                self.logger.info(f"模型已加密保存到: {encrypted_path}")
                return str(encrypted_path)
            else:
                self.logger.error("模型加密保存失败")
                return None
                
        except Exception as e:
            self.logger.error(f"加密模型失败: {e}")
            return None
    
    def _get_encryption_config(self) -> Dict[str, Any]:
        """
        获取加密配置
        
        Returns:
            加密配置字典
        """
        try:
            from .utils import ConfigManager
            return ConfigManager.get_encryption_config()
        except (ImportError, ModuleNotFoundError, AttributeError) as e:
            # 如果无法获取配置，报错不提供默认配置
            error_msg = f"加密配置加载失败: {e}"
            self.logger.error(error_msg)
            self.logger.error("请按照 SECURITY_CONFIG.md 指南配置加密密钥")
            raise RuntimeError(error_msg) from e
    
    def _create_success_result(self, model_path: str, message: str = "处理成功") -> Dict[str, Any]:
        """
        创建成功结果
        
        Args:
            model_path: 模型文件路径
            message: 成功消息
            
        Returns:
            标准化的成功结果字典
        """
        return {
            "success": True,
            "message": message,
            "model_path": model_path,
            "metrics": {"processing": "completed"},
            "output_dir": str(self.output_dir),
            "timestamp": self._get_timestamp()
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        创建错误结果
        
        Args:
            error_message: 错误消息
            
        Returns:
            标准化的错误结果字典
        """
        return {
            "success": False,
            "error": error_message,
            "timestamp": self._get_timestamp()
        }
    
    def _looks_like_url(self, url_or_path: str) -> bool:
        """判断字符串是否看URL"""
        try:
            from urllib.parse import urlparse
            
            parsed = urlparse(url_or_path)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def process_interface_config(config: Dict[str, Any], output_dir: str = "./processor_output", logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    便捷函数：从配置处理数据
    
    Args:
        config: 配置字典
        output_dir: 输出目录
        logger: 外部传入的日志器
        
    Returns:
        处理结果字典
    """
    processor = InterfaceProcessor(output_dir=output_dir, logger=logger)
    return processor.process_from_config(config)