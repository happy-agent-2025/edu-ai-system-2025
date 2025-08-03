#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API路由
"""

from flask import Blueprint, request, jsonify
from backend.agents.meta_agent import MetaAgent
from backend.agents.safety_agent import SafetyAgent
from backend.agents.memory_agent import MemoryAgent
from backend.database.manager import DatabaseManager
from backend.database.queries import DatabaseQueries
from backend.logging.logger import EduAILogger

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 初始化各组件
meta_agent = MetaAgent()
safety_agent = SafetyAgent()
memory_agent = MemoryAgent()
db_manager = DatabaseManager()
db_queries = DatabaseQueries(db_manager)
logger = EduAILogger()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': 'Education AI System API is running'
    })


@api_bp.route('/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        # 获取请求数据
        data = request.get_json()
        user_text = data.get('text', '')
        user_id = data.get('user_id', 'default_user')
        
        if not user_text:
            return jsonify({
                'status': 'error',
                'message': '缺少文本内容'
            }), 400
        
        # 记录用户输入
        logger.info(f"用户 {user_id} 输入: {user_text}")
        
        # 使用元Agent处理用户输入
        input_data = {
            'text': user_text,
            'user_id': user_id
        }
        
        # 获取Agent响应
        agent_response = meta_agent.process(input_data)
        
        # 安全检查
        safety_input = {
            'response': agent_response.get('response', ''),
            'agent': agent_response.get('agent', 'Unknown')
        }
        safety_result = safety_agent.process(safety_input)
        
        # 如果安全检查未通过，生成安全响应
        if safety_result['status'] == 'rejected':
            safe_response = safety_agent.generate_safe_response(user_text)
            final_response = safe_response
            
            # 记录安全违规
            safety_log_data = {
                'user_id': user_id,
                'user_input': user_text,
                'agent_response': agent_response.get('response', ''),
                'violation_reason': safety_result.get('reason', 'Unknown'),
                'agent_name': agent_response.get('agent', 'Unknown')
            }
            db_manager.insert_safety_log(safety_log_data)
            logger.log_safety_violation(
                user_id=user_id,
                user_input=user_text,
                agent_response=agent_response.get('response', ''),
                violation_reason=safety_result.get('reason', 'Unknown'),
                agent_name=agent_response.get('agent', 'Unknown')
            )
        else:
            final_response = agent_response.get('response', '')
        
        # 存储对话历史
        conversation_data = {
            'user_id': user_id,
            'user_input': user_text,
            'agent_response': final_response,
            'agent_name': agent_response.get('agent', 'Unknown'),
            'safety_check': safety_result['status']
        }
        db_manager.insert_conversation(conversation_data)
        
        # 记录交互日志
        logger.log_interaction(
            user_id=user_id,
            user_input=user_text,
            agent_response=final_response,
            agent_name=agent_response.get('agent', 'Unknown'),
            safety_check=safety_result['status']
        )
        
        # 更新记忆
        memory_data = {
            'action': 'store',
            'user_id': user_id,
            'conversation': conversation_data
        }
        memory_agent.process(memory_data)
        
        return jsonify({
            'status': 'success',
            'response': final_response,
            'agent': agent_response.get('agent', 'Unknown')
        })
        
    except Exception as e:
        logger.error(f"处理聊天请求时出错: {e}")
        return jsonify({
            'status': 'error',
            'message': '处理请求时发生错误'
        }), 500


@api_bp.route('/user/<user_id>/history', methods=['GET'])
def get_user_history(user_id):
    """获取用户对话历史"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db_queries.get_user_conversation_history(user_id, limit)
        
        return jsonify({
            'status': 'success',
            'history': [conv.to_dict() for conv in history]
        })
        
    except Exception as e:
        logger.error(f"获取用户 {user_id} 历史记录时出错: {e}")
        return jsonify({
            'status': 'error',
            'message': '获取历史记录时发生错误'
        }), 500


@api_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """获取系统统计信息"""
    try:
        stats = db_queries.get_system_statistics()
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"获取系统统计信息时出错: {e}")
        return jsonify({
            'status': 'error',
            'message': '获取统计信息时发生错误'
        }), 500


@api_bp.route('/safety/violations', methods=['GET'])
def get_safety_violations():
    """获取安全违规记录"""
    try:
        limit = request.args.get('limit', 50, type=int)
        violations = db_queries.get_recent_safety_violations(limit)
        
        return jsonify({
            'status': 'success',
            'violations': [violation.to_dict() for violation in violations]
        })
        
    except Exception as e:
        logger.error(f"获取安全违规记录时出错: {e}")
        return jsonify({
            'status': 'error',
            'message': '获取安全违规记录时发生错误'
        }), 500


@api_bp.route('/search', methods=['GET'])
def search_conversations():
    """搜索对话记录"""
    try:
        keyword = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)
        
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': '缺少搜索关键词'
            }), 400
        
        conversations = db_queries.search_conversations(keyword, limit)
        
        return jsonify({
            'status': 'success',
            'results': [conv.to_dict() for conv in conversations],
            'count': len(conversations)
        })
        
    except Exception as e:
        logger.error(f"搜索对话记录时出错: {e}")
        return jsonify({
            'status': 'error',
            'message': '搜索时发生错误'
        }), 500