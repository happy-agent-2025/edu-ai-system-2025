# 说明
1. 下载目录，git lsf install
## 运行步骤
1. 解压models--Qwen--Qwen2.5-0.5B.zip
2. 运行`python3 two_stage_train.py`
3. 模型保存在`../models/`文件夹下，接下来进行模型部署

## 模型部署
1. 解压emotion_lora.zip
2. window下：cd edu-ai-system\models\agents\emotion_model\training，linux参考
3. 运行模型转换脚本（windows下）
    python llama.cpp/convert_lora_to_gguf.py ..\models\emotion_final\ --outfile ..\deployment\emotion_lora.gguf
4. cd .\deployment\ 加载模型, ollama create emotion_final -f .\Modelfile_final.emotion  
5. 运行 运行 ollama run emotion_final

## 后续优化方向

1. **学习率调度优化**
   - 目前第二阶段使用固定的学习率（5e-5）
   - 建议采用更复杂的学习率调度策略，如预热（warmup）或余弦衰减（cosine decay）

2. **训练数据增强**
   - 增加第一阶段训练数据的多样性和质量
   - 添加更多富有情感的对话数据
   - 考虑添加数据过滤机制以提高数据质量

3. **延长第一阶段训练**
   - 当前的第一阶段可能训练不足
   - 考虑增加训练轮数或实现早停机制

4. **模型架构改进**
   - 在两个阶段之间添加中间评估步骤
   - 实现更好的检查点机制
   - 在训练过程中添加模型验证

5. **超参数优化**
   - 替代固定的参数设置，考虑：
     - 逐层解冻（gradual unfreezing）
     - 分层学习率
     - 自适应批大小调整

6. **评估和反馈循环**
   - 在第一阶段后添加自动评估指标
   - 实现基于验证的训练停止机制
   - 添加困惑度（perplexity）跟踪以监控对话质量

7. **内存和训练效率**
   - 添加梯度累积以获得更好的优化效果
   - 实现混合精度训练
   - 添加适当的日志记录和监控