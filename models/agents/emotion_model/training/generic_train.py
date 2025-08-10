#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI儿童情感陪伴角色模型训练脚本

基于儿童情感陪伴场景数据进行LoRA微调，
训练出具有特定角色语言风格的对话模型。

参考项目: https://github.com/KMnO4-zx/huanhuan-chat
使用方法:
    python training/two_stage_train.py

优化特性:
    1. 支持混合精度训练以节省显存
    2. 支持梯度检查点以进一步节省显存
    3. 支持LoRA参数微调以减少训练参数量
    4. 支持渐进式解冻训练策略
    5. 支持两阶段训练策略
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from peft import LoraConfig, get_peft_model, TaskType
from loguru import logger

# 正确配置tokenizers并行化
# 在训练开始前设置，避免fork后的并行化冲突
if "TOKENIZERS_PARALLELISM" not in os.environ:
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置logger
logger.remove()  # 移除默认的控制台输出
logger.add(sys.stdout, level="INFO")  # 添加控制台输出
script_dir = Path(__file__).parent
log_dir = script_dir / "logs"
log_dir.mkdir(exist_ok=True)

logger.add(str(log_dir / "training.log"), rotation="10 MB", retention="7 days", level="INFO")



class GenericDataset(Dataset):
    """
    对话数据集
    """
    
    def __init__(self, data_file: str, tokenizer, max_length: int = 512, character_config: Optional[Dict] = None,):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.character_config = character_config
        self.conversations = self.load_conversations(data_file)
        
        # 设置特殊token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
    
    def load_conversations(self, data_file: str) -> List[Dict]:
        """
        加载对话数据
        """
        conversations = []
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        conversations.append(data)
            logger.info(f"加载了 {len(conversations)} 条对话数据")
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            raise
        
        return conversations
    
    def __len__(self):
        return len(self.conversations)
    
    def __getitem__(self, idx):
        conversation = self.conversations[idx]
        
        # 构建输入文本
        instruction = conversation.get('instruction', '')
        input_text = conversation.get('input', '')
        output = conversation.get('output', '')

        if self.character_config:
            character_name = self.character_config.get('name', 'AI助手')
            character_background = self.character_config.get('background', '').strip()
            # 将角色背景信息加入到指令中
            if character_background:
                instruction = f"你是{character_name}。{character_background}\n\n{instruction}"
        
        # 格式化对话 - 使用更适合儿童的格式
        if input_text:
            prompt = f"用户：{input_text}\n助手："
        else:
            prompt = f"指令：{instruction}\n助手："
        
        # 完整文本
        full_text = prompt + output + self.tokenizer.eos_token
        
        # 编码
        encoding = self.tokenizer(
            full_text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        # 计算标签（只对回应部分计算损失）
        prompt_encoding = self.tokenizer(
            prompt,
            truncation=True,
            max_length=self.max_length,
            padding=False,
            return_tensors='pt'
        )
        
        labels = encoding['input_ids'].clone()
        prompt_length = len(prompt_encoding['input_ids'][0])
        labels[0, :prompt_length] = -100  # 忽略prompt部分的损失
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': labels.flatten()
        }

class GenericTrainer:
    """
    甄嬛角色模型训练器
    """
    
    def __init__(self, config_path: str = "./config_optimized.yaml"):
        self.config_path = config_path
        self.config = None
        self.device = None
        self.model = None
        self.tokenizer = None
        self.train_dataset = None
        self.eval_dataset = None
        self.trainer = None
        
        logger.info(f"Trainer 初始化完成，配置文件: {config_path}")
        
        # 初始化所有组件
        self.load_config()
        self.setup_device()
        self.load_model_and_tokenizer()
        self.setup_lora()
        self.setup_training_arguments()
    
    def load_config(self):
        """
        加载配置文件
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # 创建输出目录
            os.makedirs(self.config['training']['output_dir'], exist_ok=True)
            logger.info(f"配置文件加载成功: {self.config_path}")
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def setup_device(self):
        """
        设置计算设备
        """
        device_config = self.config['system']['device']
        
        if device_config == 'auto':
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
                logger.info(f"使用CUDA设备: {torch.cuda.get_device_name()}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = torch.device('mps')
                logger.info("使用Apple Silicon MPS设备")
            else:
                self.device = torch.device('cpu')
                logger.info("使用CPU设备")
        else:
            self.device = torch.device(device_config)
            logger.info(f"使用指定设备: {self.device}")
    
    def load_model_and_tokenizer(self):
        """
        加载模型和分词器
        """
        model_name = self.config['model']['base_model']
        
        logger.info(f"加载分词器: {model_name}")
        
        # 检查是否为本地模型路径
        if os.path.exists(self.config['model']['base_model']):
            custom_dir = self.config['model']['base_model']
            logger.info(f"使用本地模型路径: {custom_dir}")
        else:
            custom_dir = "./base_model/models--Qwen--Qwen2.5-0.5B/snapshots/060db6499f32faf8b98477b0a26969ef7d8b9987"
            logger.info(f"使用默认模型路径: {custom_dir}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            custom_dir,  # 使用本地路径,
            trust_remote_code=self.config['model'].get('trust_remote_code', True),
            padding_side='left'
        )
        
        # 设置特殊token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        logger.info(f"加载模型: {model_name}")
        # 根据配置决定是否使用混合精度
        use_fp16 = self.config['system'].get('mixed_precision', 'no') == 'fp16'
        torch_dtype = torch.float16 if use_fp16 else torch.float32
        
        # 文本生成模型常用，因果语言建模，根据上文预测下一个词。第一次使用某个模型时会下载模型权重和相关配置文件
        self.model = AutoModelForCausalLM.from_pretrained(
            custom_dir,
            trust_remote_code=self.config['model'].get('trust_remote_code', True),
            torch_dtype=torch_dtype,
            device_map=None,  # 禁用自动设备映射
            use_cache=not self.config['system'].get('gradient_checkpointing', False)  # 根据是否启用梯度检查点决定
        )
        
        # 启用梯度检查点以节省显存
        if self.config['system'].get('gradient_checkpointing', False):
            self.model.gradient_checkpointing_enable()
            self.model.use_cache = False
            logger.info("已启用梯度检查点")
        
        # 手动移动到指定设备
        self.model = self.model.to(self.device)
        logger.info(f"模型已移动到设备: {self.device}")
        
        logger.info(f"模型参数量: {self.model.num_parameters():,}")
    
    def setup_lora(self):
        """
        设置LoRA配置
        """
        # 检查是否启用LoRA（默认启用）
        if not self.config['lora'].get('use_lora', True):
            logger.info("未启用LoRA，使用全参数微调")
            return
        
        logger.info("配置LoRA参数")
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config['lora'].get('r', 8),
            lora_alpha=self.config['lora'].get('lora_alpha', 16),
            lora_dropout=self.config['lora'].get('lora_dropout', 0.1),
            target_modules=self.config['lora'].get('target_modules', ["q_proj", "v_proj"]),
            bias=self.config['lora'].get('bias', 'none')
        )
        
        self.model = get_peft_model(self.model, lora_config)
        
        # 打印可训练参数
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        
        logger.info(f"可训练参数: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
        logger.info(f"总参数量: {total_params:,}")
    
    def prepare_datasets(self):
        """
        准备训练数据集
        """
        data_file = self.config['data']['train_file']
        
        if not os.path.exists(data_file):
            logger.error(f"训练数据文件不存在: {data_file}")
            raise FileNotFoundError(f"训练数据文件不存在: {data_file}")
        
        logger.info(f"加载训练数据: {data_file}")

        # 获取角色配置
        character_config = self.config.get('character', None)
        if character_config:
            character_name = character_config.get('name', 'AI助手')
            logger.info(f"使用角色配置: {character_name}")
        
        # 创建数据集
        dataset = GenericDataset(
            data_file=data_file,
            tokenizer=self.tokenizer,
            character_config=character_config,
            max_length=self.config['model'].get('max_length', 2048)
        )
        
        # 分割数据集
        total_size = len(dataset)
        val_size = int(total_size * 0.1)  # 默认10%验证集
        test_size = int(total_size * 0.1)  # 默认10%测试集
        train_size = total_size - val_size - test_size
        
        train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size, test_size],
            generator=torch.Generator().manual_seed(self.config['system']['seed'])
        )
        
        logger.info(f"训练集: {len(train_dataset)} 样本")
        logger.info(f"验证集: {len(val_dataset)} 样本")
        logger.info(f"测试集: {len(test_dataset)} 样本")
        
        return train_dataset, val_dataset, test_dataset
    
    def setup_training_arguments(self):
        """
        设置训练参数并创建Trainer
        """
        training_config = self.config['training']
        
        # 根据设备类型动态调整参数
        is_mps_device = self.device.type == 'mps'
        is_cuda_device = self.device.type == 'cuda'
        
        # 数据加载器配置：根据设备和系统能力调整
        if is_mps_device:
            # MPS设备优化配置
            dataloader_num_workers = 0  # MPS设备建议使用单线程
            dataloader_pin_memory = False  # MPS不支持pin_memory
            logger.info("检测到MPS设备，使用MPS优化配置")
        elif is_cuda_device:
            # CUDA设备可以使用更多优化
            dataloader_num_workers = min(4, os.cpu_count() or 1)
            dataloader_pin_memory = True
            logger.info(f"检测到CUDA设备，使用{dataloader_num_workers}个数据加载器工作进程")
        else:
            # CPU设备配置
            dataloader_num_workers = min(2, os.cpu_count() or 1)
            dataloader_pin_memory = False
            logger.info(f"使用CPU设备，配置{dataloader_num_workers}个数据加载器工作进程")
        
        # 根据配置决定是否使用混合精度
        use_fp16 = self.config['system'].get('mixed_precision', 'no') == 'fp16'
        use_bf16 = self.config['system'].get('mixed_precision', 'no') == 'bf16'
        
        training_args = TrainingArguments(
            output_dir=training_config['output_dir'],
            num_train_epochs=training_config['num_train_epochs'],
            per_device_train_batch_size=training_config['per_device_train_batch_size'],
            per_device_eval_batch_size=training_config['per_device_eval_batch_size'],
            gradient_accumulation_steps=training_config['gradient_accumulation_steps'],
            learning_rate=float(training_config['learning_rate']),
            weight_decay=float(training_config['weight_decay']),
            warmup_ratio=training_config.get('warmup_ratio', 0.1),
            max_grad_norm=float(training_config.get('max_grad_norm', 1.0)),
            
            # 保存和评估
            save_steps=training_config.get('save_steps', 100),
            eval_steps=training_config.get('eval_steps', 50),
            logging_steps=training_config.get('logging_steps', 10),
            eval_strategy=training_config.get('evaluation_strategy', 'steps'),
            save_strategy=training_config.get('save_strategy', 'steps'),
            
            # 设备相关优化配置
            fp16=use_fp16 and not is_mps_device,  # MPS不支持fp16
            bf16=use_bf16 and not is_mps_device,
            dataloader_num_workers=dataloader_num_workers,
            dataloader_pin_memory=dataloader_pin_memory,
            seed=self.config['system'].get('seed', 42),
            
            # 日志和报告
            logging_dir=f"{training_config['output_dir']}/logs",
            report_to=training_config.get('report_to', []),
            
            # 最佳模型保存
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            save_total_limit=3,
            
            # 移除未使用的列
            remove_unused_columns=False,
        )
        
        # 准备数据集
        train_dataset, val_dataset, test_dataset = self.prepare_datasets()
        
        # 数据整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # 因果语言模型
            pad_to_multiple_of=8 if training_args.fp16 else None
        )
        
        # 创建训练器
        # PEFT模型的label_names警告是信息性的，不影响训练
        # Trainer会自动从数据集中检测labels列
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        logger.info("训练器创建完成")
        
        return training_args
    
    def train(self):
        """
        开始训练
        """
        logger.info("=== 开始情感小助手角色模型训练 ===")

        # 检查配置中是否包含角色信息，如果存在则输出角色相关信息用于调试和验证
        character_config = self.config.get('character', None)
        if character_config:
            # 获取并记录训练角色的名称，便于识别当前训练的是哪个角色
            character_name = character_config.get('name', 'AI助手')
            logger.info(f"训练角色: {character_name}")
            
            # 输出角色的其他辅助信息，如别名，有助于确认角色配置的完整性
            aliases = character_config.get('aliases', [])
            if aliases:
                logger.info(f"角色别名: {', '.join(aliases)}")
            
            # 输出角色的性格特征信息，这些特征将影响模型的回复风格
            personality = character_config.get('personality', [])
            if personality:
                logger.info(f"角色性格特征: {', '.join(personality)}")
            
            # 输出角色的语言风格信息，这些将直接影响模型生成文本的风格
            language_style = character_config.get('language_style', [])
            if language_style:
                logger.info(f"语言风格: {', '.join(language_style)}")
        
        try:
            # 开始训练
            logger.info("🚀 开始模型训练...")
            train_result = self.trainer.train()
            
            # 保存模型
            logger.info("💾 保存最终模型...")
            self.trainer.save_model()
            self.tokenizer.save_pretrained(self.config['training']['output_dir'])

            # 检查是否存在角色配置，如果存在则将其单独保存便于后续使用和参考
            if self.config.get('character'):
                # 构造角色配置文件的保存路径
                character_config_path = os.path.join(self.config['training']['output_dir'], 'character_config.json')
                # 将角色配置以JSON格式保存，便于人类阅读和程序解析
                with open(character_config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config['character'], f, ensure_ascii=False, indent=2)
                # 记录角色配置保存路径，方便用户查找
                logger.info(f"角色配置已保存到: {character_config_path}")
            
            logger.info("=== 训练完成 ===")
            logger.info(f"📁 模型保存在: {self.config['training']['output_dir']}")
            
            return train_result
            
        except Exception as e:
            logger.error(f"训练过程中出错: {e}")
            raise

def main():
    """
    主函数：执行甄嬛角色模型训练
    """
    try:
        # 创建训练器实例
        trainer = GenericTrainer()
        
        # 训练模型
        train_result = trainer.train()
        
        logger.info("🎉 角色模型训练完成！")
        logger.info("📁 接下来可以运行部署脚本: python deployment/deploy.py")
        
    except Exception as e:
        logger.error(f"训练过程出错: {e}")
        raise

if __name__ == "__main__":
    main()