"""
MCP Server - AI需求分析和设计助手
协助AI初级开发者完善需求分析和架构设计

包含三个核心工具：
1. requirement_clarifier - 需求澄清助手
2. requirement_manager - 需求文档管理器  
3. architecture_designer - 架构设计生成器
"""

import logging
import os
import json
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("StudyAIDevelop", description="AI需求分析和设计助手")

# 配置存储目录
def get_storage_dir():
    """获取存储目录，优先使用环境变量配置"""
    env_dir = os.getenv("MCP_STORAGE_DIR", "./mcp_data")
    storage_dir = Path(env_dir)
    storage_dir.mkdir(exist_ok=True)
    return storage_dir

# 全局需求文档存储
current_requirements = {
    "project_overview": [],
    "functional_requirements": [],
    "technical_requirements": [],
    "design_requirements": [],
    "deployment_requirements": [],
    "ai_constraints": [],
    "clarification_history": [],
    "architecture_designs": [],
    "last_updated": None,
    "project_id": None,
    "branch_status": {}  # 分支完成状态跟踪
}

# 存储管理类
class RequirementStorage:
    def __init__(self):
        self.storage_dir = get_storage_dir()
        self.requirements_file = self.storage_dir / "requirements.json"
        self.history_file = self.storage_dir / "history.json"
        self.load_requirements()

    def load_requirements(self):
        """加载已保存的需求文档"""
        global current_requirements
        try:
            if self.requirements_file.exists():
                with open(self.requirements_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    current_requirements.update(saved_data)
                logger.info(f"✅ 已加载需求文档: {self.requirements_file}")
        except Exception as e:
            logger.warning(f"⚠️ 加载需求文档失败: {e}")

    def save_requirements(self):
        """保存需求文档到文件"""
        try:
            current_requirements["last_updated"] = datetime.now().isoformat()
            with open(self.requirements_file, 'w', encoding='utf-8') as f:
                json.dump(current_requirements, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 需求文档已保存: {self.requirements_file}")
        except Exception as e:
            logger.error(f"❌ 保存需求文档失败: {e}")

    def save_history_entry(self, entry_type: str, content: str, metadata: dict = None):
        """保存历史记录条目"""
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                "content": content,
                "metadata": metadata or {}
            }

            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

            history.append(history_entry)

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 历史记录已保存: {entry_type}")
        except Exception as e:
            logger.error(f"❌ 保存历史记录失败: {e}")

    def export_final_document(self):
        """导出最终的完整需求和架构文档"""
        try:
            final_doc = {
                "project_summary": {
                    "generated_at": datetime.now().isoformat(),
                    "project_id": current_requirements.get("project_id"),
                    "last_updated": current_requirements.get("last_updated")
                },
                "requirements": current_requirements,
                "export_format": "markdown"
            }

            export_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(final_doc, f, ensure_ascii=False, indent=2)

            # 同时生成Markdown格式
            md_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self.generate_markdown_report(md_file)

            logger.info(f"✅ 最终文档已导出: {export_file}")
            return str(export_file)
        except Exception as e:
            logger.error(f"❌ 导出最终文档失败: {e}")
            return None

    def generate_markdown_report(self, md_file: Path):
        """生成Markdown格式的报告"""
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write("# 🚀 AI开发项目需求与架构文档\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # 项目概述
                if current_requirements.get("project_overview"):
                    f.write("## 📋 项目概述\n\n")
                    for item in current_requirements["project_overview"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 功能需求
                if current_requirements.get("functional_requirements"):
                    f.write("## ⚙️ 功能需求\n\n")
                    for item in current_requirements["functional_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 技术需求
                if current_requirements.get("technical_requirements"):
                    f.write("## 🔧 技术需求\n\n")
                    for item in current_requirements["technical_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 架构设计
                if current_requirements.get("architecture_designs"):
                    f.write("## 🏗️ 架构设计\n\n")
                    for design in current_requirements["architecture_designs"]:
                        f.write(f"{design}\n\n")

                # 澄清历史
                if current_requirements.get("clarification_history"):
                    f.write("## 📝 需求澄清历史\n\n")
                    for item in current_requirements["clarification_history"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

            logger.info(f"✅ Markdown报告已生成: {md_file}")
        except Exception as e:
            logger.error(f"❌ 生成Markdown报告失败: {e}")

# 初始化存储管理器
storage = RequirementStorage()

# 智能澄清策略模块
class IntelligentClarificationEngine:
    """智能澄清引擎 - 负责生成高质量的澄清问题"""

    @staticmethod
    def analyze_project_characteristics(user_input: str, context: str, existing_requirements: dict) -> dict:
        """分析项目特征和核心需求"""
        return {
            "project_type": IntelligentClarificationEngine._identify_project_type(user_input),
            "complexity_level": IntelligentClarificationEngine._assess_complexity(user_input),
            "key_features": IntelligentClarificationEngine._extract_key_features(user_input),
            "missing_critical_info": IntelligentClarificationEngine._identify_critical_gaps(user_input, existing_requirements)
        }

    @staticmethod
    def _identify_project_type(user_input: str) -> str:
        """识别项目类型"""
        keywords = {
            "web": ["网站", "web", "在线", "平台", "系统"],
            "mobile": ["app", "手机", "移动", "安卓", "ios"],
            "desktop": ["桌面", "pc", "软件", "客户端"],
            "miniprogram": ["小程序", "微信", "支付宝"]
        }

        user_lower = user_input.lower()
        for project_type, words in keywords.items():
            if any(word in user_lower for word in words):
                return project_type
        return "general"

    @staticmethod
    def _assess_complexity(user_input: str) -> str:
        """评估项目复杂度"""
        complex_indicators = ["ai", "智能", "机器学习", "大数据", "分布式", "微服务", "实时", "高并发"]
        user_lower = user_input.lower()

        if any(indicator in user_lower for indicator in complex_indicators):
            return "high"
        elif len(user_input.split()) > 10:
            return "medium"
        return "low"

    @staticmethod
    def _extract_key_features(user_input: str) -> list:
        """提取关键功能特征"""
        feature_keywords = {
            "用户管理": ["用户", "登录", "注册", "账号"],
            "数据处理": ["数据", "存储", "处理", "分析"],
            "交互功能": ["聊天", "评论", "消息", "通知"],
            "内容管理": ["发布", "编辑", "管理", "内容"]
        }

        features = []
        user_lower = user_input.lower()
        for feature, keywords in feature_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                features.append(feature)
        return features

    @staticmethod
    def _identify_critical_gaps(user_input: str, existing_requirements: dict) -> list:
        """识别关键信息缺口"""
        gaps = []

        # 检查是否缺少目标用户信息
        if not any("用户" in str(req) for req in existing_requirements.get("project_overview", [])):
            gaps.append("target_users")

        # 检查是否缺少技术偏好
        if not existing_requirements.get("technical_requirements"):
            gaps.append("tech_preferences")

        # 检查是否缺少功能细节
        if not existing_requirements.get("functional_requirements"):
            gaps.append("functional_details")

        return gaps

    @staticmethod
    def get_current_branch(context: str, user_input: str) -> str:
        """识别当前讨论的分支"""
        context_lower = context.lower()
        input_lower = user_input.lower()

        if any(word in context_lower + input_lower for word in ["功能", "特性", "操作"]):
            return "functional_design"
        elif any(word in context_lower + input_lower for word in ["技术", "框架", "性能"]):
            return "technical_preferences"
        elif any(word in context_lower + input_lower for word in ["界面", "ui", "交互", "设计"]):
            return "ui_design"
        elif any(word in context_lower + input_lower for word in ["目标", "用户", "价值"]):
            return "project_goals"
        else:
            return "general"

    @staticmethod
    def check_branch_completeness(requirements: dict) -> dict:
        """检查各分支完整性"""
        # 核心分支（必需）
        core_branches = {
            "project_goals": len(requirements.get("project_overview", [])) >= 1,
            "functional_design": len(requirements.get("functional_requirements", [])) >= 2,
            "technical_preferences": len(requirements.get("technical_requirements", [])) >= 1,
            "ui_design": len(requirements.get("design_requirements", [])) >= 1
        }

        # 可选分支
        optional_branches = {
            "deployment": len(requirements.get("deployment_requirements", [])) >= 1
        }

        incomplete_core = [branch for branch, complete in core_branches.items() if not complete]
        incomplete_optional = [branch for branch, complete in optional_branches.items() if not complete]

        return {
            "all_complete": len(incomplete_core) == 0,  # 只要核心分支完成即可
            "incomplete_branches": incomplete_core,  # 只显示核心分支的缺失
            "incomplete_optional": incomplete_optional,
            "completion_rate": (len(core_branches) - len(incomplete_core)) / len(core_branches)
        }

# 新增的、作为唯一流程起点的工具
@mcp.tool()
def start_new_project(user_request: str) -> str:
    """
    (最终起点) 开始一个全新的项目。
    此工具会彻底重置所有状态，然后为新需求创建蓝图。
    """
    global current_requirements
    
    logger.info(f"🚀 接到新项目启动指令: {user_request}")
    logger.info("🧹 开始重置系统状态...")

    # 1. 彻底重置内存中的全局变量
    current_requirements = {
        "project_overview": [], "functional_requirements": [], "technical_requirements": [],
        "design_requirements": [], "deployment_requirements": [], "ai_constraints": [],
        "clarification_history": [], "architecture_designs": [], "data_model_design": [],
        "mobile_specifics": [], "project_governance": [], "smart_contract_design": [],
        "wallet_integration": [], "off_chain_services": [], "frontend_interaction": [],
        "security_audit": [], "last_updated": None, "project_id": None, "branch_status": {}
    }
    logger.info("✅ 内存状态已重置。")

    # 2. 删除旧的持久化文件
    try:
        if storage.requirements_file.exists():
            os.remove(storage.requirements_file)
            logger.info(f"✅ 已删除旧的需求文件: {storage.requirements_file}")
        if storage.history_file.exists():
            os.remove(storage.history_file)
            logger.info(f"✅ 已删除旧的历史文件: {storage.history_file}")
    except Exception as e:
        logger.error(f"❌ 清理旧文件时出错: {e}")
        return f"# ❌ 项目启动失败\n\n在清理旧项目文件时发生错误: {e}"

    logger.info("✅ 系统状态已完全重置，准备创建新蓝图...")
    
    # 3. 内部调用蓝图创建的核心逻辑
    try:
        # 主控AI不直接调用create_requirement_blueprint，而是由启动工具封装调用
        report = create_requirement_blueprint(user_request)
        return f"# 🎉 新项目已启动！\n\n{report}"
    except Exception as e:
        return f"# ❌ 项目启动失败\n\n在为您创建新项目蓝图时发生错误: {e}"
# ==============================================================================
# 1. 【全新职责】的工具：create_requirement_blueprint
#    职责：只作为“首席架构师”提示词模板的提供者。
# ==============================================================================
@mcp.tool()
def create_requirement_blueprint(user_request: str) -> str:
    """
    (模板提供者) 返回用于创建需求蓝图的、专家级的提示词模板。
    """
    logger.info(f"为请求'{user_request}'提供了需求蓝图的提示词模板。")
    
    # 这个函数现在唯一的职责就是构建并返回这个强大的Prompt
    prompt_template = f"""
    # 角色与任务
    你现在是主控AI，请立即代入世界顶级CTO和首席产品经理的角色。你的当前任务是分析用户的初始请求，并生成一个全面、专业的“需求蓝图”JSON对象。

    # 用户的原始请求
    "{user_request}"

    # 你的分析与规划指令
    1.  **识别项目类型**: 分析请求，识别其核心类型 (例如：SaaS平台, 数据分析工具, 社交App, AI机器人, 物联网, Web3 DApp等)。
    2.  **规划核心分支**: 基于识别出的项目类型，规划出所有必须澄清的关键需求分支。你的规划必须体现专业性，主动思考并包含但不限于：
        - `user_personas_and_journeys` (用户画像与核心旅程)
        - `core_functional_modules` (核心功能模块拆解)
        - `data_model_and_storage` (数据模型与存储方案)
        - `technology_stack_and_non_functional` (技术栈选型与非功能性需求)
        - `ui_ux_design_principles` (UI/UX设计原则)
    3.  **严格的输出格式**: 你必须且只能输出一个格式完全正确的JSON对象，绝对不能包含任何诸如“好的，这是您要的...”之类的解释性文字或代码块标记。
    4.  **当一个工具的输出是作为另一个工具的输入时，你应在后台静默完成调用，无需在对话中展示中间结果（如JSON字符串）。
    # JSON输出格式定义
    {{
      "project_title": "string",
      "status": "CLARIFYING",
      "checklist": [
        {{
          "branch_name": "string",
          "storage_key": "string",
          "status": "pending"
        }}
      ]
    }}
    """
    return prompt_template
# ==============================================================================
# 2. 【新增】的简单工具：save_requirement_blueprint
#    职责：接收一个JSON字符串，验证并将其保存到系统状态中。
# ==============================================================================
# ==============================================================================
# 【最终优化版】的保存工具：save_requirement_blueprint
#    职责：变得更健壮，能自动处理字典或字符串，确保保存成功。
# ==============================================================================
@mcp.tool()
def save_requirement_blueprint(blueprint_data: Any) -> str:
    """
    (状态更新器-优化版) 将AI生成的蓝图(字典或JSON字符串)验证并保存。
    """
    global current_requirements
    
    logger.info("接收到保存蓝图的指令...")
    
    try:
        blueprint = {}
        # --- 核心优化点：增加类型检查和自动转换 ---
        if isinstance(blueprint_data, dict):
            # 如果AI直接传了字典，我们接受并使用它
            logger.info("输入为字典格式，直接使用。")
            blueprint = blueprint_data
        elif isinstance(blueprint_data, str):
            # 如果AI正确地传了字符串，我们进行JSON解析
            logger.info("输入为字符串格式，进行JSON解析。")
            blueprint = json.loads(blueprint_data)
        else:
            # 如果是其他不支持的类型，则报错
            raise TypeError(f"不支持的输入类型: {type(blueprint_data)}，请输入字典或JSON字符串。")
        # --- 优化结束 ---

        # 验证一下关键字段是否存在
        if "project_title" not in blueprint or "checklist" not in blueprint:
            raise ValueError("解析后的JSON缺少关键字段 'project_title' 或 'checklist'。")

        # 确保所有由AI生成的storage_key都存在于全局状态中
        for item in blueprint.get("checklist", []):
            key = item.get("storage_key")
            if key and key not in current_requirements:
                current_requirements[key] = []
        
        # 保存到系统状态
        current_requirements["requirement_blueprint"] = blueprint
        storage.save_requirements()
        
        logger.info(f"✅ 成功保存了项目 '{blueprint.get('project_title')}' 的需求蓝图。")
        
        branch_names = [item['branch_name'] for item in blueprint.get("checklist", [])]
        return f"# ✅ 项目蓝图已确认并保存！\n\n接下来，我将引导您逐一澄清以下{len(branch_names)}个关键分支。"
        
    except Exception as e:
        logger.error(f"❌ 保存需求蓝图失败：{e}")
        return f"# ❌ 保存蓝图失败\n\n原因: {e}\n请重试。"
# 需求澄清助手工具
# ==============================================================================
# 【新增/替换】 访谈专家 - 提示词提供者
# ==============================================================================
@mcp.tool()
def requirement_clarifier(branch_name_to_clarify: str, project_title: str) -> str:
    """
    (模板提供者) 针对单个分支，返回用于生成“问题清单”的专家级提示词模板。
    """
    logger.info(f"为分支'{branch_name_to_clarify}'提供了问题清单的提示词模板。")
    
    prompt_template = f"""
    # 角色与任务
    你现在是主控AI，请立即代入资深用户访谈专家的角色。你的任务是针对一个具体的需求分支，设计出一系列能够彻底澄清所有细节的、结构化的问题清单，并为每个问题提供一个专业的建议方案。

    # 背景
    我们正在澄清项目“{project_title}”的“{branch_name_to_clarify}”分支。

    # 你的分析与规划指令
    1.  **拆解分支**: 将“{branch_name_to_clarify}”这个宏观概念，拆解成3-5个必须被回答的具体子问题。
    2.  **提供专业建议**: 针对你提出的每一个子问题，都提供一个简洁、专业、符合行业最佳实践的建议答案(`ai_suggestion`)。这是为了在用户不确定时，你能主动引导。
    3.  **严格的输出格式**: 你必须且只能输出一个格式完全正确的JSON对象，绝对不能包含任何解释性文字或代码块标记。
    4.  **行为准则: “你必须严格遵守最小权限原则。当用户授予你自主决策权时（如‘你决定’、‘常规方案’等），该授权仅限于当前正在讨论的、最具体的一个分支或一个问题。你绝对禁止将此授权泛化到任何其他未开始或正在进行中的分支上，除非得到用户的明确指令。”
    5.  **当一个工具的输出是作为另一个工具的输入时，你应在后台静默完成调用，无需在对话中展示中间结果（如JSON字符串）。

    # JSON输出格式定义
    {{
      "branch_name": "{branch_name_to_clarify}",
      "clarification_tasks": [
        {{
          "question_id": "string (例如: FUNC_Q1)",
          "question_text": "string (具体的问题)",
          "ai_suggestion": "string (AI提供的建议答案)",
          "status": "pending",
          "user_answer": null
        }}
      ]
    }}
    """
    return prompt_template
# ==============================================================================
# 【新增】 访谈专家 - 结果保存器
# ==============================================================================
@mcp.tool()
def save_clarification_tasks(branch_storage_key: str, tasks_data: Any) -> str:
    """(状态更新器-优化版) 将问题清单(字典或JSON字符串)保存到指定分支。"""
    try:
        tasks_obj = {}
        if isinstance(tasks_data, dict):
            tasks_obj = tasks_data
        elif isinstance(tasks_data, str):
            tasks_obj = json.loads(tasks_data)
        else:
            raise TypeError(f"不支持的tasks_data类型: {type(tasks_data)}")

        if "requirement_blueprint" in current_requirements:
            for branch in current_requirements["requirement_blueprint"]["checklist"]:
                if branch["storage_key"] == branch_storage_key:
                    branch["clarification_tasks"] = tasks_obj.get("clarification_tasks", [])
                    storage.save_requirements()
                    return f"✅ 分支 '{tasks_obj.get('branch_name')}' 的澄清任务已规划完毕。"
        raise ValueError(f"在蓝图中未找到指定的storage_key: {branch_storage_key}")
    except Exception as e:
        return f"# ❌ 保存任务清单失败: {e}"
def _save_clarification_history(user_input: str, context: str):
    """保存澄清历史记录"""
    current_requirements["clarification_history"].append({
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "context": context
    })
    storage.save_history_entry("requirement_clarification", user_input, {"context": context})
    storage.save_requirements()

def _generate_intelligent_analysis_prompt(user_input: str, context: str, project_analysis: dict) -> str:
    """生成智能化分析提示词"""

    # 获取已有需求信息和分支状态
    existing_info = _get_existing_requirements_summary()
    current_branch = IntelligentClarificationEngine.get_current_branch(context, user_input)
    branch_status = IntelligentClarificationEngine.check_branch_completeness(current_requirements)

    # 检测用户是否要求AI自主设计
    auto_design_keywords = ["常规", "标准", "普通", "一般", "你决定", "ai决定", "自己设计"]
    is_auto_design = any(keyword in user_input.lower() for keyword in auto_design_keywords)

    return f"""# 🧠 智能需求分析任务 - 分支感知模式

## 📝 用户输入分析
**原始输入**: {user_input}
**上下文**: {context}
**当前分支**: {current_branch}
**项目类型**: {project_analysis['project_type']}
**复杂度**: {project_analysis['complexity_level']}
**识别特征**: {', '.join(project_analysis['key_features'])}
**用户授权自主设计**: {"是" if is_auto_design else "否"}

## 📋 已有需求信息
{existing_info}

## 🌿 分支完整性状态
- **完成率**: {branch_status['completion_rate']:.0%}
- **未完成分支**: {', '.join(branch_status['incomplete_branches']) if branch_status['incomplete_branches'] else '无'}
- **当前分支状态**: {"讨论中" if current_branch in branch_status['incomplete_branches'] else "已完成"}

## 🎯 分支感知智能分析指令

### 第一步：分支状态处理
{"**用户授权自主设计当前分支**" if is_auto_design else "**用户提供具体信息**"}

{f'''
**自主设计指令**：
- 仅对当前分支({current_branch})进行合理的标准化设计
- 设计完成后，检查其他未完成分支
- 绝对禁止跳转到架构设计阶段
- 必须提醒用户还有其他分支需要讨论
''' if is_auto_design else '''
**信息澄清指令**：
- 深度分析用户在当前分支的具体需求
- 识别当前分支的关键缺失信息
- 生成针对当前分支的高质量澄清问题
'''}

### 第二步：全局完整性检查
**重要原则：始终保持全局视野，防止遗忘其他分支**

- 当前讨论分支：{current_branch}
- 未完成分支：{', '.join(branch_status['incomplete_branches']) if branch_status['incomplete_branches'] else '无'}
- 完成率：{branch_status['completion_rate']:.0%}

### 第三步：智能问题生成策略
**针对当前分支生成2-3个最重要的问题**：

{f'''
**当前分支({current_branch})的关键澄清点**：
- 如果是功能设计：具体的功能流程、用户操作方式、数据处理逻辑
- 如果是技术偏好：具体的技术栈选择、性能要求、集成需求
- 如果是UI设计：具体的界面风格、交互方式、用户体验偏好
- 如果是项目目标：具体的用户群体、核心价值、解决的问题
''' if not is_auto_design else f'''
**自主设计{current_branch}分支**：
- 基于已有信息进行合理的标准化设计
- 设计内容要具体、可实施
- 避免过于复杂或过于简单的方案
'''}

## 📤 输出格式要求

**🔍 分支感知分析结果**：
- **当前分支**：{current_branch}
- **分支完成状态**：{branch_status['completion_rate']:.0%}
- **已明确信息**：[用户在当前分支已清楚表达的需求]
- **分支关键缺口**：[当前分支缺失的关键信息]

{f'''
**🤖 AI自主设计结果**：
[对{current_branch}分支进行具体的标准化设计]

**⚠️ 重要提醒**：
- 当前仅完成了{current_branch}分支的设计
- 还有以下分支需要讨论：{', '.join(branch_status['incomplete_branches'])}
- 请继续澄清其他分支，不要急于进入架构设计
''' if is_auto_design else f'''
**❓ 针对{current_branch}分支的澄清问题**（按重要性排序）：
1. [最重要的问题 - 说明为什么重要，提供具体选项]
2. [第二重要的问题 - 说明对架构的影响，给出示例]
3. [第三个问题 - 如果必要，解释澄清的价值]
'''}

**🌿 全局进度提醒**：
- 已完成分支：{len([b for b in ['project_goals', 'functional_design', 'technical_preferences', 'ui_design'] if b not in branch_status['incomplete_branches']])}个
- 待完成分支：{len(branch_status['incomplete_branches'])}个
- {"✅ 所有分支已完成，可以考虑架构设计" if branch_status['all_complete'] else f"⏳ 还需完成：{', '.join(branch_status['incomplete_branches'])}"}

**🎯 下一步行动指南**：
{f"请使用 requirement_manager 保存{current_branch}分支的设计结果，然后继续澄清其他分支" if is_auto_design else f"请回答{current_branch}分支的澄清问题，然后使用 requirement_manager 保存"}

---
*🔄 分支完成后，请使用 requirement_manager 工具保存，系统会自动检查其他分支*
"""

def _get_existing_requirements_summary() -> str:
    """获取已有需求信息摘要"""
    summary_parts = []

    if current_requirements.get("project_overview"):
        summary_parts.append(f"项目概述: {len(current_requirements['project_overview'])} 条")

    if current_requirements.get("functional_requirements"):
        summary_parts.append(f"功能需求: {len(current_requirements['functional_requirements'])} 条")

    if current_requirements.get("technical_requirements"):
        summary_parts.append(f"技术需求: {len(current_requirements['technical_requirements'])} 条")

    if not summary_parts:
        return "暂无已保存的需求信息"

    return " | ".join(summary_parts)

# 智能需求管理模块
class IntelligentRequirementManager:
    """智能需求管理器 - 负责需求分类、去重、验证"""

    # 扩展的类别映射
    CATEGORY_MAPPING = {
        "项目概述": "project_overview",
        "项目目标": "project_overview",
        "核心功能需求": "functional_requirements",
        "功能需求": "functional_requirements",
        "功能和UI需求": "functional_requirements",
        "UI设计需求": "design_requirements",
        "用户体验需求": "design_requirements",
        "技术需求": "technical_requirements",
        "技术栈偏好": "technical_requirements",
        "性能需求": "technical_requirements",
        "设计需求": "design_requirements",
        "部署需求": "deployment_requirements",
        "运维需求": "deployment_requirements",
        "AI约束": "ai_constraints",
        "业务约束": "ai_constraints"
    }

    @staticmethod
    def smart_categorize(content: str, suggested_category: str) -> str:
        """智能分类需求内容"""
        # 首先尝试建议的类别
        if suggested_category in IntelligentRequirementManager.CATEGORY_MAPPING:
            return IntelligentRequirementManager.CATEGORY_MAPPING[suggested_category]

        # 基于内容关键词智能分类
        content_lower = content.lower()

        if any(keyword in content_lower for keyword in ["目标", "用户群", "解决", "价值"]):
            return "project_overview"
        elif any(keyword in content_lower for keyword in ["功能", "特性", "操作", "流程"]):
            return "functional_requirements"
        elif any(keyword in content_lower for keyword in ["技术", "框架", "数据库", "api"]):
            return "technical_requirements"
        elif any(keyword in content_lower for keyword in ["界面", "ui", "交互", "体验"]):
            return "design_requirements"
        elif any(keyword in content_lower for keyword in ["部署", "服务器", "运维", "监控"]):
            return "deployment_requirements"

        return "functional_requirements"  # 默认分类

    @staticmethod
    def check_duplicate(content: str, category: str, existing_requirements: dict) -> dict:
        """检查重复需求"""
        category_items = existing_requirements.get(category, [])

        for item in category_items:
            existing_content = item.get('content', '') if isinstance(item, dict) else str(item)

            # 简单的相似度检查
            if IntelligentRequirementManager._calculate_similarity(content, existing_content) > 0.8:
                return {
                    "is_duplicate": True,
                    "similar_content": existing_content,
                    "timestamp": item.get('timestamp', 'unknown') if isinstance(item, dict) else 'unknown'
                }

        return {"is_duplicate": False}

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    @staticmethod
    def validate_requirement(content: str, category: str) -> dict:
        """验证需求内容的完整性"""
        issues = []
        suggestions = []

        if len(content.strip()) < 10:
            issues.append("需求描述过于简短")
            suggestions.append("请提供更详细的描述")

        if category == "technical_requirements" and not any(tech in content.lower() for tech in ["技术", "框架", "数据库", "api", "架构"]):
            issues.append("技术需求缺少具体技术细节")
            suggestions.append("请明确具体的技术选型或约束")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }

# 需求文档管理器工具
@mcp.tool()
def requirement_manager(clarified_info: Any, category: str, force_storage_category: str = None) -> str:
    """(状态更新器-优化版) 保存单条需求，能自动处理字符串或字典。"""
    
    info_content = ""
    # --- 核心优化点：增加类型检查和自动转换 ---
    if isinstance(clarified_info, dict):
        info_content = json.dumps(clarified_info, ensure_ascii=False, indent=2)
    elif isinstance(clarified_info, str):
        info_content = clarified_info
    else:
        raise TypeError(f"不支持的clarified_info类型: {type(clarified_info)}")
    # --- 优化结束 ---
    storage_category = ""
    
    # --- 核心优化点：强制分类覆盖 ---
    if force_storage_category and force_storage_category in current_requirements:
        storage_category = force_storage_category
        logger.info(f"✅ 使用强制分类，目标存储: {storage_category}")
    else:
        logger.info(f"⚠️ 未使用强制分类，启动智能分类...")
        storage_category = IntelligentRequirementManager.smart_categorize(clarified_info, category)

    # 检查重复
    duplicate_check = IntelligentRequirementManager.check_duplicate(
        clarified_info, storage_category, current_requirements
    )

    # 验证需求
    validation_result = IntelligentRequirementManager.validate_requirement(clarified_info, storage_category)

    # 如果发现重复，提供选择
    if duplicate_check["is_duplicate"]:
        return f"""# ⚠️ 发现相似需求

## 🔍 重复检测结果
- **新需求**: {clarified_info}
- **已有需求**: {duplicate_check['similar_content']}
- **添加时间**: {duplicate_check['timestamp']}

## 🤔 处理建议
1. 如果是补充信息，请明确说明"补充："
2. 如果是修正信息，请明确说明"修正："
3. 如果确实是新需求，请重新调用并说明差异

请重新整理后再次提交。
"""

    # 如果验证失败，提供改进建议
    if not validation_result["is_valid"]:
        return f"""# ❌ 需求验证失败

## 🔍 发现的问题
{chr(10).join(f"- {issue}" for issue in validation_result['issues'])}

## 💡 改进建议
{chr(10).join(f"- {suggestion}" for suggestion in validation_result['suggestions'])}

请完善需求描述后重新提交。
"""

    # 保存需求
    requirement_entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "storage_category": storage_category,
        "content": clarified_info
    }

    current_requirements[storage_category].append(requirement_entry)

    # 保存到文件
    storage.save_history_entry("requirement_update", clarified_info, {
        "category": category,
        "storage_category": storage_category
    })
    storage.save_requirements()

    # 生成状态报告
    return _generate_requirement_update_report(category, storage_category, clarified_info)

def _generate_requirement_update_report(category: str, storage_category: str, content: str) -> str:
    """生成需求更新报告"""
    # 统计信息
    total_requirements = sum(len(current_requirements[key]) for key in [
        "project_overview", "functional_requirements", "technical_requirements",
        "design_requirements", "deployment_requirements", "ai_constraints"
    ])

    # 智能下一步建议
    next_steps = _generate_intelligent_next_steps()

    return f"""# ✅ 需求文档智能更新完成

## 📝 更新详情
- **原始类别**: {category}
- **✅ AI智能归类**: {storage_category}
- **内容**: {content}
- **时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 当前需求状态
- **总需求条目**: {total_requirements}
- **项目概述**: {len(current_requirements['project_overview'])} 条
- **功能需求**: {len(current_requirements['functional_requirements'])} 条
- **技术需求**: {len(current_requirements['technical_requirements'])} 条
- **设计需求**: {len(current_requirements['design_requirements'])} 条

## 🎯 智能建议
{next_steps}

## 💾 存储信息
- ✅ 需求已保存: `{storage.requirements_file}`
- ✅ 历史已记录: `{storage.history_file}`
"""

def _generate_intelligent_next_steps() -> str:
    """生成智能化的下一步建议"""
    # 使用现有的分支完整性检查
    branch_status = IntelligentClarificationEngine.check_branch_completeness(current_requirements)

    suggestions = []

    # 基于分支状态给出建议
    if "project_goals" in branch_status['incomplete_branches']:
        suggestions.append("📋 建议澄清项目目标和用户群体")

    if "functional_design" in branch_status['incomplete_branches']:
        suggestions.append("⚙️ 建议详细澄清核心功能设计")

    if "technical_preferences" in branch_status['incomplete_branches']:
        suggestions.append("🔧 建议澄清技术栈偏好和性能要求")

    if "ui_design" in branch_status['incomplete_branches']:
        suggestions.append("🎨 建议澄清UI/UX设计偏好")

    # 如果所有分支完成，建议架构设计
    if branch_status['all_complete']:
        suggestions.append("🏗️ 所有需求分支已完成，可以开始架构设计")
    else:
        suggestions.append(f"⏳ 完成度：{branch_status['completion_rate']:.0%}，继续完善未完成分支")

    return "\n".join(f"- {suggestion}" for suggestion in suggestions) if suggestions else "- 继续使用 requirement_clarifier 完善需求信息"

# 智能架构设计模块
class IntelligentArchitectureDesigner:
    """智能架构设计器 - 基于需求生成定制化架构方案"""

    @staticmethod
    def analyze_requirements_for_architecture(requirements: dict) -> dict:
        """分析需求并提取架构关键信息"""
        analysis = {
            "project_type": "web",  # 默认
            "complexity_indicators": [],
            "key_features": [],
            "tech_preferences": [],
            "performance_requirements": [],
            "integration_needs": []
        }

        # 分析所有需求内容
        all_content = []
        for category in ["project_overview", "functional_requirements", "technical_requirements", "design_requirements"]:
            for item in requirements.get(category, []):
                content = item.get('content', '') if isinstance(item, dict) else str(item)
                all_content.append(content.lower())

        combined_content = " ".join(all_content)

        # 识别项目类型
        if any(keyword in combined_content for keyword in ["api", "后端", "服务"]):
            analysis["project_type"] = "backend"
        elif any(keyword in combined_content for keyword in ["前端", "界面", "ui"]):
            analysis["project_type"] = "frontend"
        elif any(keyword in combined_content for keyword in ["全栈", "网站", "平台"]):
            analysis["project_type"] = "fullstack"

        # 识别复杂度指标
        complexity_keywords = {
            "high_concurrency": ["高并发", "大量用户", "实时"],
            "data_intensive": ["大数据", "数据分析", "存储"],
            "ai_integration": ["ai", "智能", "机器学习"],
            "microservices": ["微服务", "分布式", "集群"]
        }

        for indicator, keywords in complexity_keywords.items():
            if any(keyword in combined_content for keyword in keywords):
                analysis["complexity_indicators"].append(indicator)

        # 提取关键功能
        feature_keywords = {
            "user_management": ["用户", "登录", "注册", "权限"],
            "content_management": ["内容", "发布", "编辑", "管理"],
            "real_time_communication": ["聊天", "消息", "通知", "实时"],
            "data_processing": ["数据处理", "分析", "统计", "报表"],
            "file_handling": ["文件", "上传", "下载", "存储"],
            "payment": ["支付", "订单", "交易", "结算"]
        }

        for feature, keywords in feature_keywords.items():
            if any(keyword in combined_content for keyword in keywords):
                analysis["key_features"].append(feature)

        return analysis

    @staticmethod
    def generate_tech_stack_recommendations(analysis: dict) -> dict:
        """基于分析结果生成技术栈推荐"""
        recommendations = {
            "frontend": [],
            "backend": [],
            "database": [],
            "infrastructure": [],
            "reasoning": []
        }

        # 前端推荐
        if analysis["project_type"] in ["frontend", "fullstack"]:
            if "real_time_communication" in analysis["key_features"]:
                recommendations["frontend"] = ["React + Socket.io", "Vue 3 + WebSocket"]
                recommendations["reasoning"].append("实时通信需求推荐支持WebSocket的前端框架")
            else:
                recommendations["frontend"] = ["React 18", "Vue 3", "Next.js 15"]

        # 后端推荐
        if analysis["project_type"] in ["backend", "fullstack"]:
            if "high_concurrency" in analysis["complexity_indicators"]:
                recommendations["backend"] = ["FastAPI + Uvicorn", "Node.js + Express", "Go + Gin"]
                recommendations["reasoning"].append("高并发需求推荐高性能异步框架")
            elif "ai_integration" in analysis["complexity_indicators"]:
                recommendations["backend"] = ["FastAPI", "Django + DRF", "Flask"]
                recommendations["reasoning"].append("AI集成推荐Python生态系统")
            else:
                recommendations["backend"] = ["FastAPI", "Express.js", "Spring Boot"]

        # 数据库推荐
        if "data_intensive" in analysis["complexity_indicators"]:
            recommendations["database"] = ["PostgreSQL + Redis", "MongoDB + Redis"]
            recommendations["reasoning"].append("数据密集型应用推荐高性能数据库组合")
        elif "real_time_communication" in analysis["key_features"]:
            recommendations["database"] = ["PostgreSQL + Redis", "MySQL + Redis"]
            recommendations["reasoning"].append("实时通信需要缓存支持")
        else:
            recommendations["database"] = ["PostgreSQL", "MySQL", "SQLite"]

        return recommendations

    @staticmethod
    def generate_module_structure(analysis: dict) -> dict:
        """生成模块结构建议"""
        modules = {
            "core_modules": [],
            "optional_modules": [],
            "integration_modules": []
        }

        # 核心模块
        if "user_management" in analysis["key_features"]:
            modules["core_modules"].append({
                "name": "用户管理模块",
                "responsibilities": ["用户注册/登录", "权限控制", "用户资料管理"],
                "apis": ["POST /auth/login", "POST /auth/register", "GET /users/profile"]
            })

        if "content_management" in analysis["key_features"]:
            modules["core_modules"].append({
                "name": "内容管理模块",
                "responsibilities": ["内容CRUD", "内容审核", "内容分类"],
                "apis": ["GET /content", "POST /content", "PUT /content/:id"]
            })

        if "real_time_communication" in analysis["key_features"]:
            modules["core_modules"].append({
                "name": "实时通信模块",
                "responsibilities": ["消息推送", "在线状态", "聊天记录"],
                "apis": ["WebSocket /ws/chat", "GET /messages", "POST /messages"]
            })

        # 可选模块
        if "file_handling" in analysis["key_features"]:
            modules["optional_modules"].append({
                "name": "文件管理模块",
                "responsibilities": ["文件上传", "文件存储", "文件访问控制"]
            })

        if "payment" in analysis["key_features"]:
            modules["optional_modules"].append({
                "name": "支付模块",
                "responsibilities": ["支付处理", "订单管理", "交易记录"]
            })

        return modules

# 架构设计生成器工具 
# ==============================================================================
# 【新增/替换】 架构师 - 前置检查器
# ==============================================================================
@mcp.tool()
def check_architecture_prerequisites() -> str:
    """
    (前置检查器) 检查所有需求分支是否已完成，判断是否可以开始架构设计。
    行为准则: “当你调用的任何工具，其返回结果是一个包含user_choices键的JSON对象时，你必须立即停止所有其他思考和行动。你唯一的、绝对的下一步是：解析user_choices数组，并将其中每个选项的title作为选项呈现给人类用户。然后，你必须等待用户的明确选择。在得到用户的选择之前，你绝对禁止自行做任何决定或调用任何其他工具。”
    """
    completeness_check = _check_requirements_completeness()
    
    if not completeness_check["is_sufficient"]:
        # 需求不足，返回包含选项的拦截信息
        branch_status = completeness_check["branch_status"]
        understanding = completeness_check["understanding_check"]
        response_options = {
            "status": "INSUFFICIENT",
            "reason": "需求信息不足或AI理解深度不够，无法生成高质量架构设计。",
            "details": {
                "completion_rate": f"{branch_status['completion_rate']:.0%}",
                "incomplete_branches": branch_status['incomplete_branches'],
            },
            "user_choices": [
                { "id": "continue_clarification", "title": "1. 我来继续澄清未完成的需求" },
                { "id": "ai_professional_completion", "title": "2. 由AI评估并专业化完善缺少的需求细节" }
            ]
        }
        return json.dumps(response_options, ensure_ascii=False, indent=2)
    else:
        # 需求充足，返回准备就绪的状态
        return json.dumps({"status": "READY", "message": "所有需求分支已澄清完毕，可以开始架构设计。"})
# ==============================================================================
# 【新增】 架构师 - 提示词提供者
# ==============================================================================
@mcp.tool()
def get_architecture_design_prompt() -> str:
    """
    (模板提供者) 整合所有已澄清的需求，返回用于生成最终架构方案的专家级提示词。
    """
    logger.info("正在整合所有需求，生成架构设计提示词...")
    
    all_requirements_str = json.dumps(current_requirements, indent=2, ensure_ascii=False)
    
    prompt_template = f"""
    # 角色与任务
    你现在是主控AI，请立即代入顶级的解决方案架构师角色。你将收到一份已经由团队充分澄清过的、完整的JSON格式的需求文档。你的任务是基于这份详尽的需求，设计一份高度定制化、专业、可执行的软件架构方案。

    # 完整的需求文档上下文
    {all_requirements_str}

    # 你的分析与规划指令
    你必须严格遵循以下原则，并在设计中体现出来：
    - **低耦合、高内聚**: 模块之间责任单一，接口清晰，低代码，必须避免重复造轮子，保证性能的同时最简化实现。
    - **模块化**: 定义清晰的业务模块和服务边界。
    - **考虑上下文**: 你的设计必须考虑到用户在需求中提到的所有细节，比如用户规模（影响并发设计）、部署偏好（影响技术选型）等。
    - **专业输出**: 输出一份详细的Markdown格式架构设计文档，必须包含但不限于：技术栈选型、系统架构图（用Mermaid语法）、核心模块拆分及API定义、数据表结构设计、部署方案。
    - **开发流程设计**: 基于需求和架构设计完整的高可用的满足以上开发要求开发流程补充到文档结尾。


    # 你的输出
    现在，请直接开始撰写这份Markdown文档，直接保存不需要输出给用户。不要添加任何额外的解释性文字，符合markdown语法，清晰展示，避免文字堆叠，格式混乱使用户无法阅读。
    """
    return prompt_template
# ==============================================================================
# 【新增】 架构师 - 结果保存器
# ==============================================================================
@mcp.tool()
def save_architecture_design(architecture_markdown: str, design_focus: str = "full_architecture") -> str:
    """(状态更新器) 将最终架构设计Markdown文档保存到状态中。"""
    # 这个工具的输入已经是Markdown字符串，所以它天生就是健壮的，无需修改。
    try:
        _save_architecture_design(design_focus, architecture_markdown)
        return "✅ 架构设计方案已成功保存。"
    except Exception as e:
        return f"❌ 保存架构设计时出错: {e}"
def _check_requirements_completeness() -> dict:
    """检查需求完整性 - 使用分支状态检查"""
    branch_status = IntelligentClarificationEngine.check_branch_completeness(current_requirements)

    # AI理解深度检查
    understanding_check = _ai_understanding_depth_check()

    return {
        "is_sufficient": branch_status['all_complete'] and understanding_check['ready_for_architecture'],
        "branch_status": branch_status,
        "understanding_check": understanding_check,
        "status_summary": f"分支完成度：{branch_status['completion_rate']:.0%}，AI理解深度：{understanding_check['confidence_level']}"
    }

def _ai_understanding_depth_check() -> dict:
    """AI理解深度自检"""
    total_reqs = sum(len(current_requirements[key]) for key in [
        "project_overview", "functional_requirements", "technical_requirements", "design_requirements"
    ])

    # 简单的理解深度评估
    confidence_indicators = {
        "has_clear_goals": len(current_requirements["project_overview"]) >= 1,
        "has_detailed_functions": len(current_requirements["functional_requirements"]) >= 2,
        "has_tech_preferences": len(current_requirements["technical_requirements"]) >= 1,
        "has_design_guidance": len(current_requirements["design_requirements"]) >= 1
    }

    confidence_score = sum(confidence_indicators.values()) / len(confidence_indicators)

    remaining_questions = []
    if not confidence_indicators["has_clear_goals"]:
        remaining_questions.append("项目目标和用户群体不够明确")
    if not confidence_indicators["has_detailed_functions"]:
        remaining_questions.append("功能设计细节不足")
    if not confidence_indicators["has_tech_preferences"]:
        remaining_questions.append("技术偏好未明确")

    return {
        "confidence_level": "高" if confidence_score >= 0.75 else "中" if confidence_score >= 0.5 else "低",
        "confidence_score": confidence_score,
        "remaining_questions": remaining_questions,
        "ready_for_architecture": confidence_score >= 0.75 and len(remaining_questions) == 0
    }

def _generate_customized_architecture_design(design_focus: str, analysis: dict, tech_recs: dict, modules: dict) -> str:
    """生成定制化架构设计文档"""

    return f"""# 🏗️ 智能定制架构设计方案

## 🎯 设计概览
- **设计重点**: {design_focus}
- **项目类型**: {analysis['project_type']}
- **复杂度特征**: {', '.join(analysis['complexity_indicators']) if analysis['complexity_indicators'] else '标准复杂度'}
- **核心功能**: {', '.join(analysis['key_features'])}

## 🧠 需求分析驱动的设计决策

### 架构复杂度评估
{_generate_complexity_analysis(analysis)}

### 关键设计原则
1. **需求驱动**: 每个架构决策都基于明确的需求
2. **渐进式扩展**: 支持功能的逐步增加
3. **AI友好开发**: 模块清晰，便于AI辅助开发
4. **低耦合高内聚**: 模块间依赖最小化

## 🔧 定制化技术栈推荐

### 推荐方案及理由
{_format_tech_recommendations(tech_recs)}

## 📦 智能模块划分

### 核心业务模块
{_format_module_structure(modules['core_modules'])}

### 可选扩展模块
{_format_module_structure(modules['optional_modules'])}

## 🏛️ 架构模式建议

{_generate_architecture_pattern_recommendation(analysis)}

## 📅 分阶段实施计划

{_generate_implementation_phases(modules)}

## 🤖 AI开发优化建议

### 开发顺序优化
1. **先核心后扩展**: 优先实现核心业务逻辑
2. **接口先行**: 先定义清晰的模块接口
3. **测试驱动**: 每个模块都有对应的测试

### 代码组织建议
```
project/
├── src/
│   ├── core/          # 核心业务模块
│   ├── modules/       # 功能模块
│   ├── shared/        # 共享组件
│   └── config/        # 配置文件
├── tests/             # 测试文件
└── docs/              # 文档
```

## 🎯 实施建议与风险提醒

### 关键成功因素
- 严格按照模块边界开发，避免耦合
- 及时进行集成测试
- 保持文档与代码同步

### 潜在风险点
{_identify_potential_risks(analysis)}

---

**🎉 定制化架构设计完成！**

此方案基于您的具体需求生成，确保技术选择与业务需求完美匹配。

## 💾 存储信息
- **架构设计已保存**: `{storage.requirements_file}`
- **完整文档导出**: 使用 `export_final_document` 工具
"""

def _generate_complexity_analysis(analysis: dict) -> str:
    """生成复杂度分析"""
    if not analysis['complexity_indicators']:
        return "- **标准复杂度**: 适合传统的三层架构模式"

    complexity_desc = {
        "high_concurrency": "高并发处理需求，需要异步架构和缓存策略",
        "data_intensive": "数据密集型应用，需要优化数据存储和查询",
        "ai_integration": "AI功能集成，需要考虑模型服务化和API设计",
        "microservices": "微服务架构需求，需要服务拆分和治理"
    }

    return "\n".join(f"- **{indicator}**: {complexity_desc.get(indicator, '需要特殊考虑')}"
                    for indicator in analysis['complexity_indicators'])

def _format_tech_recommendations(tech_recs: dict) -> str:
    """格式化技术推荐"""
    sections = []

    for category, recommendations in tech_recs.items():
        if category == "reasoning" or not recommendations:
            continue

        sections.append(f"**{category.title()}**: {', '.join(recommendations)}")

    if tech_recs.get("reasoning"):
        sections.append("\n**选择理由**:")
        sections.extend(f"- {reason}" for reason in tech_recs["reasoning"])

    return "\n".join(sections)

def _format_module_structure(modules: list) -> str:
    """格式化模块结构"""
    if not modules:
        return "- 暂无特定模块需求"

    formatted = []
    for module in modules:
        formatted.append(f"**{module['name']}**")
        formatted.append(f"- 职责: {', '.join(module['responsibilities'])}")
        if 'apis' in module:
            formatted.append(f"- 接口: {', '.join(module['apis'])}")
        formatted.append("")

    return "\n".join(formatted)

def _generate_architecture_pattern_recommendation(analysis: dict) -> str:
    """生成架构模式推荐"""
    if "microservices" in analysis['complexity_indicators']:
        return """**推荐模式**: 微服务架构
- 服务按业务域拆分
- 使用API网关统一入口
- 独立部署和扩展"""
    elif len(analysis['key_features']) > 4:
        return """**推荐模式**: 模块化单体架构
- 清晰的模块边界
- 共享数据库
- 统一部署"""
    else:
        return """**推荐模式**: 分层架构
- 表现层、业务层、数据层
- 简单清晰的依赖关系
- 易于开发和维护"""

def _generate_implementation_phases(modules: dict) -> str:
    """生成实施阶段计划"""
    phases = []

    phases.append("**第一阶段 (1-2周)**: 基础框架搭建")
    phases.append("- 项目初始化和环境配置")
    phases.append("- 数据库设计和基础表结构")
    phases.append("- 核心模块接口定义")
    phases.append("")

    if modules['core_modules']:
        phases.append("**第二阶段 (2-4周)**: 核心功能开发")
        for module in modules['core_modules']:
            phases.append(f"- {module['name']}实现")
        phases.append("")

    if modules['optional_modules']:
        phases.append("**第三阶段 (1-3周)**: 扩展功能开发")
        for module in modules['optional_modules']:
            phases.append(f"- {module['name']}实现")
        phases.append("")

    phases.append("**第四阶段 (1周)**: 集成测试和优化")
    phases.append("- 端到端测试")
    phases.append("- 性能优化")
    phases.append("- 部署准备")

    return "\n".join(phases)

def _identify_potential_risks(analysis: dict) -> str:
    """识别潜在风险"""
    risks = []

    if "high_concurrency" in analysis['complexity_indicators']:
        risks.append("高并发场景下的性能瓶颈")

    if "ai_integration" in analysis['complexity_indicators']:
        risks.append("AI模型服务的稳定性和响应时间")

    if len(analysis['key_features']) > 5:
        risks.append("功能复杂度过高，开发周期可能延长")

    if not risks:
        risks.append("项目风险较低，按计划实施即可")

    return "\n".join(f"- {risk}" for risk in risks)

def _save_architecture_design(design_focus: str, architecture_design: str):
    """保存架构设计"""
    architecture_entry = {
        "timestamp": datetime.now().isoformat(),
        "design_focus": design_focus,
        "content": architecture_design
    }

    current_requirements["architecture_designs"].append(architecture_entry)

    storage.save_history_entry("architecture_design", architecture_design, {"design_focus": design_focus})
    storage.save_requirements()

# 新增：导出最终文档工具
@mcp.tool()
def export_final_document() -> str:
    """导出完整的项目需求和架构文档"""

    export_path = storage.export_final_document()

    if export_path:
        # 统计信息
        total_clarifications = len(current_requirements.get("clarification_history", []))
        total_requirements = sum(len(current_requirements[key]) for key in [
            "project_overview", "functional_requirements", "technical_requirements",
            "design_requirements", "deployment_requirements", "ai_constraints"
        ])
        total_architectures = len(current_requirements.get("architecture_designs", []))

        result = f"""# 📄 项目文档导出完成

## ✅ 导出信息
- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **文件路径**: `{export_path}`
- **Markdown版本**: `{export_path.replace('.json', '.md')}`

## 📊 文档统计
- **需求澄清次数**: {total_clarifications}
- **需求条目总数**: {total_requirements}
- **架构设计方案**: {total_architectures}

## 📁 存储目录结构
```
{storage.storage_dir}/
├── requirements.json      # 实时需求文档
├── history.json          # 操作历史记录
├── final_document_*.json # 导出的完整文档
└── final_document_*.md   # Markdown格式报告
```

## 🎯 文档用途
- **requirements.json**: 实时更新的结构化需求数据
- **history.json**: 完整的操作历史，便于追溯
- **final_document_*.json**: 完整项目文档，包含所有信息
- **final_document_*.md**: 人类可读的Markdown报告

## 💡 使用建议
1. 将导出的文档保存到项目仓库中
2. 使用Markdown文件作为项目README的基础
3. JSON文件可用于后续的自动化处理

**🎉 项目文档已完整保存，可以开始开发了！**
"""
    else:
        result = """# ❌ 文档导出失败

请检查存储目录权限和磁盘空间。

**存储目录**: `{storage.storage_dir}`
"""

    return result

# 新增：查看当前需求状态工具
@mcp.tool()
def view_requirements_status() -> str:
    """查看当前需求文档的详细状态和内容"""

    # 统计信息
    total_clarifications = len(current_requirements.get("clarification_history", []))
    total_requirements = sum(len(current_requirements[key]) for key in [
        "project_overview", "functional_requirements", "technical_requirements",
        "design_requirements", "deployment_requirements", "ai_constraints"
    ])
    total_architectures = len(current_requirements.get("architecture_designs", []))

    # 构建状态报告
    status_report = f"""# 📋 当前需求文档状态

## 📊 总体统计
- **最后更新**: {current_requirements.get('last_updated', '未更新')}
- **需求澄清次数**: {total_clarifications}
- **需求条目总数**: {total_requirements}
- **架构设计方案**: {total_architectures}
- **存储位置**: `{storage.storage_dir}`

## 📝 需求分类详情

### 🎯 项目概述 ({len(current_requirements['project_overview'])} 条)
"""

    # 添加项目概述
    for i, item in enumerate(current_requirements['project_overview'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### ⚙️ 功能需求 ({len(current_requirements['functional_requirements'])} 条)
"""

    # 添加功能需求
    for i, item in enumerate(current_requirements['functional_requirements'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### 🔧 技术需求 ({len(current_requirements['technical_requirements'])} 条)
"""

    # 添加技术需求
    for i, item in enumerate(current_requirements['technical_requirements'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### 🏗️ 架构设计 ({len(current_requirements['architecture_designs'])} 个)
"""

    # 添加架构设计
    for i, design in enumerate(current_requirements['architecture_designs'], 1):
        focus = design.get('design_focus', '未指定') if isinstance(design, dict) else '未指定'
        timestamp = design.get('timestamp', '未知时间') if isinstance(design, dict) else '未知时间'
        status_report += f"{i}. 设计重点: {focus} (生成时间: {timestamp[:19]})\n"

    status_report += f"""
## 📁 文件信息
- **需求文档**: `{storage.requirements_file}`
- **历史记录**: `{storage.history_file}`
- **文件大小**: 需求文档 {storage.requirements_file.stat().st_size if storage.requirements_file.exists() else 0} 字节

## 🎯 下一步建议
"""

    if total_requirements < 3:
        status_report += "- 📝 需求信息较少，建议继续使用 requirement_clarifier 澄清更多需求\n"

    if total_architectures == 0:
        status_report += "- 🏗️ 尚未生成架构设计，建议使用 architecture_designer 生成技术方案\n"

    if total_requirements >= 3 and total_architectures >= 1:
        status_report += "- 📄 需求和架构已基本完善，可以使用 export_final_document 导出完整文档\n"
        status_report += "- 🚀 可以开始项目开发了！\n"

    status_report += """
## 🛠️ 可用工具
- `requirement_clarifier`: 澄清和分析需求
- `requirement_manager`: 管理和保存需求
- `architecture_designer`: 生成架构设计
- `export_final_document`: 导出完整文档
- `view_requirements_status`: 查看当前状态（当前工具）
"""

    return status_report

if __name__ == "__main__":
    logger.info("🚀 启动AI需求分析和设计助手")
    mcp.run()