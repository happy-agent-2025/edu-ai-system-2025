#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MLflow模型管理脚本
支持模型热更新、A/B测试和版本回滚
"""

import mlflow
import yaml
import os
from datetime import datetime
from backend.utils.model_manager import model_manager


def setup_mlflow_tracking():
    """设置MLflow跟踪"""
    # 从配置文件加载MLflow配置
    config = model_manager.agent_config.get('model_management', {}).get('mlflow', {})
    tracking_uri = config.get('tracking_uri', 'http://localhost:5000')
    
    # 设置跟踪URI
    mlflow.set_tracking_uri(tracking_uri)
    
    return tracking_uri


def create_experiment(experiment_name):
    """创建MLflow实验"""
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
        print(f"创建实验 '{experiment_name}' 成功，实验ID: {experiment_id}")
        return experiment_id
    except Exception as e:
        # 实验可能已存在
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment:
            print(f"实验 '{experiment_name}' 已存在，实验ID: {experiment.experiment_id}")
            return experiment.experiment_id
        else:
            print(f"创建实验时出错: {e}")
            return None


def log_model_version(model_name, version, metrics=None, params=None):
    """记录模型版本到MLflow"""
    with mlflow.start_run():
        # 记录参数
        if params:
            mlflow.log_params(params)
        
        # 记录指标
        if metrics:
            mlflow.log_metrics(metrics)
        
        # 记录模型信息
        mlflow.set_tag("model_name", model_name)
        mlflow.set_tag("version", version)
        mlflow.set_tag("timestamp", datetime.now().isoformat())
        
        print(f"模型 {model_name} 版本 {version} 已记录到MLflow")


def start_ab_test(test_name, variants):
    """启动A/B测试"""
    # 使用模型管理器启动A/B测试
    success = model_manager.start_ab_test(test_name, variants)
    
    if success:
        print(f"A/B测试 '{test_name}' 启动成功")
        print("变体配置:")
        for variant in variants:
            print(f"  - {variant['name']}: {variant['traffic_percentage']}%")
    else:
        print(f"A/B测试 '{test_name}' 启动失败")


def activate_model_version(model_name, version):
    """激活模型版本"""
    success = model_manager.activate_version(model_name, version)
    
    if success:
        print(f"模型 {model_name} 版本 {version} 激活成功")
    else:
        print(f"模型 {model_name} 版本 {version} 激活失败")


def rollback_model_version(model_name, steps=1):
    """回滚模型版本"""
    success = model_manager.rollback_version(model_name, steps)
    
    if success:
        print(f"模型 {model_name} 已回滚 {steps} 步")
    else:
        print(f"模型 {model_name} 回滚失败")


def list_model_versions(model_name):
    """列出模型版本"""
    if model_name in model_manager.versions:
        versions = model_manager.versions[model_name]
        print(f"模型 {model_name} 的版本列表:")
        for version in versions:
            status = "活跃" if version.is_active else "非活跃"
            print(f"  - 版本: {version.version}, 创建时间: {version.created_at}, 状态: {status}")
    else:
        print(f"未找到模型 {model_name} 的版本信息")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MLflow模型管理工具')
    parser.add_argument('--setup', action='store_true', help='设置MLflow跟踪')
    parser.add_argument('--experiment', type=str, help='创建实验')
    parser.add_argument('--log-model', nargs=2, metavar=('MODEL_NAME', 'VERSION'), help='记录模型版本')
    parser.add_argument('--ab-test', type=str, help='启动A/B测试')
    parser.add_argument('--activate', nargs=2, metavar=('MODEL_NAME', 'VERSION'), help='激活模型版本')
    parser.add_argument('--rollback', nargs=1, metavar='MODEL_NAME', help='回滚模型版本')
    parser.add_argument('--list-versions', type=str, help='列出模型版本')
    
    args = parser.parse_args()
    
    if args.setup:
        tracking_uri = setup_mlflow_tracking()
        print(f"MLflow跟踪URI设置为: {tracking_uri}")
    
    elif args.experiment:
        experiment_id = create_experiment(args.experiment)
        if experiment_id:
            # 设置当前实验
            mlflow.set_experiment(experiment_id=experiment_id)
    
    elif args.log_model:
        model_name, version = args.log_model
        log_model_version(model_name, version)
    
    elif args.ab_test:
        # 示例A/B测试配置
        if args.ab_test == "agent-test":
            variants = [
                {"name": "qwen-0.5b", "model": "qwen:0.5b", "traffic_percentage": 70},
                {"name": "llama2", "model": "llama2", "traffic_percentage": 30}
            ]
            start_ab_test("agent-ab-test", variants)
    
    elif args.activate:
        model_name, version = args.activate
        activate_model_version(model_name, version)
    
    elif args.rollback:
        model_name = args.rollback[0]
        rollback_model_version(model_name)
    
    elif args.list_versions:
        model_name = args.list_versions
        list_model_versions(model_name)
    
    else:
        print("请指定操作参数")
        parser.print_help()


if __name__ == '__main__':
    main()