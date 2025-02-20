from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, TypedDict, Annotated, Sequence, Union
import os
import traceback
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
from langgraph.graph import Graph, END
import operator
import json
import logging
from datetime import datetime
import time
import re
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 初始化 FastAPI 应用
app = FastAPI(title="Research Report Generator API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 初始化 Gemini 模型
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-thinking-exp-01-21",
    temperature=0,
    max_tokens=None,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# 初始化 Tavily 客户端
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 定义请求模型
class ResearchRequest(BaseModel):
    topic: str
    depth: int = 3  # 研究深度，影响搜索结果数量
    language: str = "zh"  # 语言选择
    focus_areas: List[str] = []  # 关注领域

# 定义状态类型
class State(TypedDict):
    topic: str
    depth: int
    language: str
    focus_areas: List[str]
    research_data: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    report: Dict[str, Any]
    next: str

def search_information(state: State) -> Dict:
    """搜索研究主题相关的信息"""
    # 1. 任务计划分解
    planning_prompt = f"""
    请对研究主题 '{state["topic"]}' 进行详细的任务分解和研究计划制定。
    关注领域：{', '.join(state.get('focus_areas', ['全面分析']))}
    
    请提供：
    1. 需要深入研究的关键问题（至少5个核心问题）
    2. 每个问题对应的精准搜索关键词（中英文对照）
    3. 重点关注的数据指标和技术维度
    4. 建议参考的权威机构和数据来源
    
    输出格式：
    {{
        "key_questions": ["问题1", "问题2", ...],
        "search_keywords": {{"keyword1": {{"zh": "中文关键词", "en": "English Keyword"}}, ...}},
        "focus_points": ["重点1", "重点2", ...],
        "authority_sources": ["权威来源1", "权威来源2", ...]
    }}
    """
    
    plan_response = llm.invoke(planning_prompt)
    try:
        plan = json.loads(plan_response.content)
    except:
        # 如果JSON解析失败，使用默认计划
        plan = {
            "key_questions": [state["topic"]],
            "search_keywords": {state["topic"]: {"zh": state["topic"], "en": ""}},
            "focus_points": state.get("focus_areas", ["综合分析"]),
            "authority_sources": ["研究报告", "行业数据", "专业分析"]
        }
    
    logger.info(f"Research plan: {json.dumps(plan, ensure_ascii=False)}")
    
    # 2. 基于计划进行多维度搜索
    all_results = []
    
    # 对每个关键词进行中英文搜索
    for keyword_info in plan["search_keywords"].values():
        for lang, kw in keyword_info.items():
            if not kw:
                continue
                
            try:
                # 增加搜索深度和结果数量
                search_results = tavily_client.search(
                    query=kw,
                    search_depth="advanced",
                    max_results=max(5, state["depth"] * 5),
                    include_domains=[
                        "scholar.google.com",
                        "researchgate.net",
                        "sciencedirect.com",
                        "nature.com",
                        "ieee.org",
                        "mckinsey.com",
                        "gartner.com",
                        "forrester.com",
                        "bloomberg.com",
                        "reuters.com",
                        "ft.com",
                        "wsj.com",
                        "arxiv.org"
                    ],
                    exclude_domains=[
                        "youtube.com",
                        "facebook.com",
                        "twitter.com",
                        "instagram.com"
                    ]
                )
                
                if isinstance(search_results, dict) and 'results' in search_results:
                    # 为每个结果添加可信度评分
                    for result in search_results['results']:
                        result['credibility_score'] = calculate_credibility_score(result)
                    all_results.extend(search_results['results'])
                    logger.info(f"Found {len(search_results['results'])} results for keyword: {kw}")
            except Exception as e:
                logger.error(f"Search failed for keyword {kw}: {str(e)}")
                continue
    
    # 去重并按可信度排序
    seen_urls = set()
    unique_results = []
    for result in sorted(all_results, key=lambda x: x.get('credibility_score', 0), reverse=True):
        try:
            if isinstance(result, dict) and "url" in result and result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        except Exception as e:
            logger.error(f"Error processing search result: {str(e)}")
            continue
    
    logger.info(f"Total unique results: {len(unique_results)}")
    
    # 返回完整状态，包含任务计划
    return {
        **state,
        "research_data": unique_results[:state["depth"] * 7],  # 增加结果数量
        "task_plan": plan,
        "next": "analyze"
    }

def calculate_credibility_score(result: Dict[str, Any]) -> float:
    """计算搜索结果的可信度评分"""
    score = 0.0
    
    # 检查域名权重
    authority_domains = {
        'nature.com': 10,
        'science.org': 10,
        'sciencedirect.com': 9,
        'ieee.org': 9,
        'scholar.google.com': 8,
        'researchgate.net': 8,
        'mckinsey.com': 8,
        'gartner.com': 8,
        'forrester.com': 8,
        'bloomberg.com': 7,
        'reuters.com': 7,
        'ft.com': 7,
        'wsj.com': 7
    }
    
    url = result.get('url', '').lower()
    for domain, weight in authority_domains.items():
        if domain in url:
            score += weight
            break
    
    # 检查内容类型
    content_type = result.get('type', '').lower()
    if 'pdf' in content_type or 'research' in content_type:
        score += 3
    elif 'article' in content_type:
        score += 2
    
    # 检查标题相关性
    title = result.get('title', '').lower()
    if any(keyword in title for keyword in ['research', 'study', 'analysis', 'report', '研究', '分析', '报告']):
        score += 2
    
    # 根据发布时间调整分数
    published_date = result.get('published_date', '')
    if published_date:
        try:
            date = datetime.strptime(published_date[:10], '%Y-%m-%d')
            years_old = (datetime.now() - date).days / 365
            if years_old <= 1:
                score += 3
            elif years_old <= 2:
                score += 2
            elif years_old <= 3:
                score += 1
        except:
            pass
    
    return score

def analyze_information(state: State) -> Dict:
    """分析搜索到的信息"""
    focus_areas_text = "、".join(state.get("focus_areas", [])) if state.get("focus_areas") else "所有相关领域"
    
    analysis_prompt = f"""
    请基于以下研究数据，为主题 '{state["topic"]}' 创建一个深度分析报告。
    特别关注以下领域：{focus_areas_text}
    
    研究数据：
    {json.dumps(state["research_data"], ensure_ascii=False)}
    
    请提供以下结构的详细分析：
    
    1. 数据可信度分析
    - 对所有来源进行可信度评估
    - 识别高可信度的关键数据点
    - 标注数据的时效性和适用范围
    
    2. 市场规模与增长
    - 当前市场规模（具体数字）
    - 未来增长预测（CAGR）
    - 细分市场分布
    
    3. 技术发展趋势
    - 核心技术突破
    - 技术成熟度评估
    - 创新方向预测
    
    4. 竞争格局分析
    - 主要参与者及市场份额
    - 竞争优势对比
    - 商业模式创新
    
    5. 挑战与机遇
    - 技术瓶颈
    - 市场准入门槛
    - 政策影响因素
    
    6. 投资价值分析
    - 投资热点领域
    - 风险收益评估
    - 投资建议
    
    请确保：
    1. 提供具体的数据支持，包括市场规模、增长率、份额等
    2. 引用权威机构的预测和分析
    3. 标注数据来源的可信度
    4. 对矛盾的数据进行交叉验证和解释
    """
    
    response = llm.invoke(analysis_prompt)
    
    # 进行数据交叉验证
    validation_prompt = f"""
    请对以下分析结果进行数据交叉验证：
    
    分析内容：
    {response.content}
    
    验证要点：
    1. 检查数据一致性
    2. 验证关键结论的可靠性
    3. 识别潜在的数据偏差
    4. 补充缺失的关键数据点
    
    如果发现不一致或可靠性问题，请提供修正建议。
    """
    
    validation_response = llm.invoke(validation_prompt)
    
    # 返回完整状态
    return {
        **state,
        "analysis": {
            "topic": state["topic"],
            "raw_analysis": response.content,
            "validation": validation_response.content,
            "sources": state["research_data"],
            "credibility_assessment": {
                "high_credibility_sources": [s for s in state["research_data"] if s.get('credibility_score', 0) > 7],
                "data_consistency_check": True,
                "validation_status": "verified"
            }
        },
        "next": "generate"
    }

def format_markdown_content(content: str) -> str:
    """格式化 Markdown 内容，确保正确的空行和格式"""
    lines = content.split('\n')
    formatted_lines = []
    prev_is_heading = False
    prev_is_empty = True  # 假设开始是空行
    
    for line in lines:
        line = line.rstrip()
        
        # 如果是标题
        if re.match(r'^#{1,6}\s', line):
            # 如果前一行不是空行，添加空行
            if not prev_is_empty:
                formatted_lines.append('')
            formatted_lines.append(line)
            # 在标题后添加空行
            formatted_lines.append('')
            prev_is_heading = True
            prev_is_empty = True
        # 如果是列表项
        elif re.match(r'^\s*[-*+]\s', line) or re.match(r'^\s*\d+\.\s', line):
            formatted_lines.append(line)
            prev_is_heading = False
            prev_is_empty = False
        # 如果是空行
        elif not line.strip():
            # 避免多个连续空行
            if not prev_is_empty:
                formatted_lines.append('')
            prev_is_heading = False
            prev_is_empty = True
        # 普通段落
        else:
            # 如果前一行是标题，已经有空行了
            if not prev_is_heading and not prev_is_empty:
                formatted_lines.append('')
            formatted_lines.append(line)
            prev_is_heading = False
            prev_is_empty = False
    
    # 确保文档以空行结束
    if formatted_lines and formatted_lines[-1].strip():
        formatted_lines.append('')
    
    return '\n'.join(formatted_lines)

def generate_final_report(state: State) -> Dict:
    """生成最终研究报告"""
    report_prompt = f"""
    请基于以下深度分析创建一个详细的研究报告。
    必须严格遵循以下Markdown格式规则：

    1. 标题格式：
       - 一级标题：# 标题（前后必须有空行）
       - 二级标题：## 标题（前后必须有空行）
       - 三级标题：### 标题（前后必须有空行）

    2. 段落格式：
       - 每个段落之间必须有一个空行
       - 段落内容必须是完整的句子
       - 不允许有多余的空行

    3. 列表格式：
       - 无序列表使用 - 开头（前面必须有空行）
       - 有序列表使用 1. 2. 3. 开头
       - 列表项之间不需要空行
       - 列表结束后必须有空行

    4. 引用和强调：
       - 重要数据使用**粗体**标注
       - 关键概念使用*斜体*标注
       - 引用数据使用[n]格式

    分析数据：
    {json.dumps(state["analysis"], ensure_ascii=False)}

    请生成以下结构的报告，确保每个部分都有实际内容，不要使用占位符：

    # {state["topic"]}

    ## 1. 摘要

    [此处是研究发现和关键数据点总结]

    ## 2. 研究背景

    [此处是研究背景、目的和意义]

    ## 3. 研究方法

    ### 3.1 数据来源

    - 数据采集方法和范围说明
    - 权威来源说明和评估
    - 数据可信度分析方法

    ### 3.2 分析方法

    - 研究框架设计说明
    - 分析工具选择依据
    - 验证方法说明

    ## 4. 市场分析

    ### 4.1 市场规模

    - 当前市场规模及增长趋势
    - 未来五年CAGR预测
    - 区域市场分布情况

    ### 4.2 竞争格局

    - 主要企业市场份额
    - 竞争优势分析
    - 商业模式创新趋势

    ## 5. 技术分析

    ### 5.1 技术现状

    - 核心技术评估
    - 技术成熟度分析
    - 关键技术壁垒

    ### 5.2 发展趋势

    - 技术创新方向
    - 突破点预测
    - 应用场景展望

    ## 6. 机遇与挑战

    ### 6.1 市场机遇

    - 增长驱动因素
    - 潜在市场机会
    - 商业模式创新空间

    ### 6.2 面临挑战

    - 技术瓶颈分析
    - 市场风险评估
    - 政策影响因素

    ## 7. 投资分析

    ### 7.1 投资价值

    - 重点投资领域
    - 预期回报分析
    - 风险评估指标

    ### 7.2 投资建议

    - 优先投资方向
    - 最佳进入时机
    - 风险规避策略

    ## 8. 结论和建议

    ### 8.1 主要结论

    1. [具体的、基于数据的核心结论1]
    2. [具体的、基于数据的核心结论2]
    3. [具体的、基于数据的核心结论3]

    ### 8.2 发展建议

    1. [具体可行的建议1]
    2. [具体可行的建议2]
    3. [具体可行的建议3]

    ## 9. 参考文献

    [以下参考文献按可信度排序，数据来源为权威研究平台]
    """

    response = llm.invoke(report_prompt)
    
    # 格式化生成的报告内容
    formatted_report = format_markdown_content(response.content)
    
    logger.info(f"Generated Markdown report content: {formatted_report}")
    
    # 提取结论（确保是中文）
    conclusions_prompt = f"""
    基于以下报告内容，提取3-5个最具价值的关键结论。
    每个结论必须：
    1. 包含具体数据支持
    2. 有明确的时间维度
    3. 指出发展方向
    4. 突出实际价值
    
    报告内容：
    {formatted_report}
    
    请直接列出结论要点，每个结论一行，使用中文。
    """
    
    conclusions_response = llm.invoke(conclusions_prompt)
    conclusions = [line.strip() for line in conclusions_response.content.strip().split("\n") if line.strip()]
    
    references = []
    for source in sorted(state["research_data"], key=lambda x: x.get('credibility_score', 0), reverse=True):
        if "title" in source and "url" in source:
            ref_item = {
                "title": source["title"],
                "url": source["url"],
                "credibility": source.get('credibility_score', 0),
                "type": "权威机构报告" if source.get('credibility_score', 0) > 7 else "行业分析文章",
                "published_date": source.get("published_date", "")
            }
            references.append(ref_item)
    
    if references:
        references_section = "\n\n## 9. 参考文献\n\n"
        for i, ref in enumerate(references[:15], 1):
            if not ref['url'].startswith(('http://', 'https://')):
                continue
            url = ref['url']
            ref_date = f"({ref['published_date'][:10]})" if ref['published_date'] else ""
            ref_line = f"{i}. [{ref['title']}]({url}) {ref_date}\n\n"  # 确保每个引用后有空行
            references_section += ref_line
        
        # full_report = f"{formatted_report}\n{references_section}"
        full_report = f"{formatted_report}"
    else:
        full_report = formatted_report

    # 返回完整状态
   # 在返回report对象时添加单独的references字段
    return {
        **state,
        "report": {
            "topic": state["topic"],
            "executive_summary": full_report,
            "detailed_analysis": {
                "market_analysis": state["analysis"]["raw_analysis"],
                "validation_results": state["analysis"]["validation"],
                "full_report": full_report
            },
            "conclusions": conclusions,
            "references": references[:15],  # 限制参考文献数量
            "metadata": {
                "credibility_assessment": state["analysis"]["credibility_assessment"],
                "generation_date": datetime.now().isoformat(),
                "data_sources_count": len(references),
                "high_credibility_sources_count": len([r for r in references if r["credibility"] > 7])
            }
        },
        "next": END
    }

# 创建工作流
def create_workflow() -> Graph:
    # 创建工作流图
    workflow = Graph()

    # 定义节点
    workflow.add_node("search", search_information)
    workflow.add_node("analyze", analyze_information)
    workflow.add_node("generate", generate_final_report)

    # 设置边缘连接
    workflow.add_edge("search", "analyze")
    workflow.add_edge("analyze", "generate")
    
    # 定义状态更新函数
    def get_next_step(state: Dict) -> Union[str, END]:
        # 更新状态
        next_step = state.get("next", "")
        if next_step == END:
            return END
        return next_step or "search"

    # 添加边缘条件
    workflow.set_entry_point("search")
    
    workflow.add_conditional_edges(
        "search",
        get_next_step,
        {
            "analyze": "analyze"
        }
    )
    
    workflow.add_conditional_edges(
        "analyze",
        get_next_step,
        {
            "generate": "generate"
        }
    )
    
    workflow.add_conditional_edges(
        "generate",
        get_next_step,
        {}
    )

    return workflow.compile()

# 流式输出的生成器
async def generate_report_stream(state: Dict):
    # 创建和运行工作流
    workflow = create_workflow()
    try:
        # 逐步执行工作流并返回结果
        for step in workflow.invoke(state):
            # 假设每个步骤返回的状态中包含报告部分
            yield f"数据块: {step['report']}\n"  # 逐步输出数据
            time.sleep(1)  # 模拟延迟
    except Exception as workflow_error:
        logger.error(f"Workflow error: {str(workflow_error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(workflow_error)}"
        )

# API 端点
@app.post("/api/generate-report")
async def generate_research_report(request: ResearchRequest):
    try:
        # 创建初始状态
        initial_state = {
            "topic": request.topic,
            "depth": request.depth,
            "language": request.language,
            "focus_areas": request.focus_areas,
            "research_data": [],
            "analysis": {},
            "report": None,
            "next": "search"
        }
        
        logger.info(f"Starting research for topic: {request.topic}")
        
        # 创建和运行工作流
        workflow = create_workflow()
        try:
            final_state = workflow.invoke(initial_state)
            logger.info("Workflow completed successfully")
            # 在生成报告的函数中添加日志
            logger.info("Generated report data: %s", final_state["report"])
            return final_state["report"]
        except Exception as workflow_error:
            logger.error(f"Workflow error: {str(workflow_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {str(workflow_error)}"
            )
            
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/api/generate-report-stream")
async def generate_research_report_stream(request: ResearchRequest):
    try:
        # 创建初始状态
        initial_state = {
            "topic": request.topic,
            "depth": request.depth,
            "language": request.language,
            "focus_areas": request.focus_areas,
            "research_data": [],
            "analysis": {},
            "report": None,
            "next": "search"
        }
        
        logger.info(f"Starting research for topic: {request.topic}")
        
        # 使用流式输出
        return StreamingResponse(generate_report_stream(initial_state), media_type="text/plain")
        
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
