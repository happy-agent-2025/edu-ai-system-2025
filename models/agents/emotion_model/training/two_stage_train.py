#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两阶段微调训练脚本

第一阶段：用大量通用对话数据进行预训练
第二阶段：用角色特定数据进行精细调整
"""

import os
import sys
import yaml
from pathlib import Path
from loguru import logger

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from generic_train import GenericTrainer

def two_stage_training():
    """
    执行两阶段训练
    """
    logger.info("开始两阶段微调训练")
    
    # 第一阶段：通用对话能力训练
    logger.info("=== 第一阶段：通用对话能力训练 ===")
    try:
        stage1_trainer = GenericTrainer(config_path="./config_optimized.yaml")
        stage1_result = stage1_trainer.train()
        logger.info("第一阶段训练完成")
    except Exception as e:
        logger.error(f"第一阶段训练失败: {e}")
        raise
    
    # 第二阶段：角色特定能力训练
    logger.info("=== 第二阶段：角色特定能力训练 ===")
    try:
        # 读取第一阶段配置
        with open("./config_optimized.yaml", 'r', encoding='utf-8') as f:
            stage2_config = yaml.safe_load(f)
        
        # 保存第一阶段模型路径
        stage1_model_path = stage1_trainer.config['training']['output_dir']
        
        # 更新第二阶段配置
        stage2_config['model']['base_model'] = stage1_model_path
        stage2_config['training']['output_dir'] = "../models/emotion_final"
        stage2_config['training']['learning_rate'] = 5e-5  # 进一步降低学习率
        stage2_config['training']['num_train_epochs'] = 3  # 减少训练轮数
        
        # 保存更新后的配置到config_final.yaml
        final_config_path = "./config_final.yaml"
        with open(final_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(stage2_config, f, allow_unicode=True, sort_keys=False)
        
        logger.info(f"第二阶段配置已保存到: {final_config_path}")
        
        stage2_trainer = GenericTrainer(config_path=final_config_path)
        stage2_result = stage2_trainer.train()
        logger.info("第二阶段训练完成")
    except Exception as e:
        logger.error(f"第二阶段训练失败: {e}")
        raise
    
    logger.info("两阶段微调训练全部完成！")

if __name__ == "__main__":
    two_stage_training()