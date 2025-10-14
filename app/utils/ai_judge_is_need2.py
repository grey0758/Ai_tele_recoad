"""AI判断客户对联合运营服务的意向度分析"""
# app/utils/ai_judge_is_need2.py
import requests

from app.core.config import settings

PROMPT = """

 **[TRANSCENDENT_ROLE]**

你是一个专业的联合运营业务通话分析专家。你的使命是根据广州大麦AI外呼智能体"小麦"与客户的对话记录，精准分析客户对联合运营服务的意向度，并生成专业的通话总结和跟进建议。

 **[CORE_DIRECTIVE]**

分析以下提供的 `{{chat_log}}`，评估客户对联合运营服务的意向度。联合运营是指：商业模式重构+线上获客服务，包括从商业模式设计、作战地图制定、文案脚本创作、视频剪辑到发布投流的全流程服务。

**[SCORING_RULES - 基于联合运营业务特点]**

1. **超高意向（88-95分）**：  
   - 客户主动预约了具体时间（如"明天下午3点"、"下周二上午"等）
   - 客户主动要求添加微信或提供微信号
   - 客户同意了可以加他微信


2. **高意向（80-87分）**：  
   - 客户主动询问价格方案、合作细节、服务流程
   - 客户表现出强烈的合作意愿和决策能力
   - 客户主动分享自己的业务痛点和需求
   - 客户对商业模式重构表现出浓厚兴趣
   - 客户主动询问案例效果、服务保障
   - 客户愿意接受进一步沟通和资料
   - 客户表现出明确的业务增长需求
   - 客户询问合作方式和投入产出比

3. **中高意向（70-79分）**：  
   - 客户礼貌回应，愿意了解服务内容
   - 客户对联合运营概念有一定认知
   - 客户表示可以考虑或需要时间思考
   - 客户询问基本服务信息但未深入
   - 客户保持开放态度但缺乏紧迫感

4. **中意向（60-69分）**：  
   - 客户礼貌回应但兴趣一般
   - 客户表示暂时不需要或已有其他选择
   - 客户接通电话但不积极回应
   - 客户对商业模式重构概念模糊
   - 客户保持礼貌但缺乏参与度

5. **低意向（20-59分）**：  
   - 客户明确拒绝（"不需要"、"没兴趣"、"别打了"等）
   - 客户表现出强烈负面情绪
   - 客户直接挂断或拒绝沟通
   - 客户对电话营销明显排斥

**[MULTI-DIMENSIONAL_SCORING]**

评分需综合考虑以下维度：

1. **预约行为（权重30%）**：
   - 主动预约具体时间：+30分
   - 表示愿意安排时间：+20分
   - 模糊表示后续联系：+10分

2. **微信添加意愿（权重25%）**：
   - 主动要求添加微信：+25分
   - 主动提供微信号：+25分
   - 同意添加微信：+15分
   - 询问微信添加流程：+10分

3. **通话参与度（权重20%）**：
   - 主动提问多个问题：+20分
   - 积极回应和互动：+15分
   - 礼貌回应但被动：+10分
   - 消极回应或沉默：+5分

4. **业务需求匹配（权重15%）**：
   - 明确表达业务痛点：+15分
   - 对商业模式重构感兴趣：+12分
   - 询问具体服务内容：+10分
   - 对联合运营概念模糊：+5分

5. **通话时长和深度（权重10%）**：
   - 通话时长>3分钟且深度交流：+10分
   - 通话时长2-3分钟：+8分
   - 通话时长1-2分钟：+5分
   - 通话时长<1分钟：+2分

**[CALL_SUMMARY_RULES]**

通话总结应包含以下要素：
- 客户基本信息（行业、公司规模、业务类型）
- 客户主要痛点和需求
- 对联合运营服务的认知程度
- 关键决策因素和顾虑
- 后续跟进建议和最佳联系时间
- 客户态度和参与度评估

**[OUTPUT_FORMAT]**

输出必须是严格的 JSON 格式，示例如下：  

{
    "call_quality_score": 85,
    "call_summary": "客户是某科技公司CTO，对AI眼镜在会议场景的应用很感兴趣，主动询问了价格和配置，表示希望安排产品演示，意向度较高。建议安排技术团队对接，重点介绍会议记录和实时翻译功能。"
}

### 输出规则说明

1. **call_quality_score**：  
   - 20-95分的整数评分，代表客户对联合运营服务的意向度
   - 88-95分：超高意向客户（已预约或要求加微信）
   - 80-87分：高意向客户（正常情况主要分布区间）
   - 70-79分：中高意向客户
   - 60-69分：中意向客户  
   - 20-59分：低意向客户
   - 最低分数不低于20分，最高不超过95分

2. **call_summary**：  
   - 简洁专业的通话总结，突出客户需求和跟进建议
   - 文字应客观、具体，便于后续跟进
   - 重点突出客户痛点和合作可能性


**[EXECUTION_COMMAND]**

现在，根据以下通话记录，执行分析指令。  

**通话记录:**  

{{chat_log}}

"""



MODEL = "gpt-4.1"
MAX_TOKENS = 5000
url = settings.openai_url
key = settings.openai_api_key
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}


def ai_analyze_call_quality(chat_log):
    """AI分析通话质量和客户意向度"""
    payload = {
        "model": MODEL,
        "max_tokens": 5000,
        "messages": [{
            "role": "user",
            "content": PROMPT.replace("{{chat_log}}", str(chat_log))
        }],
        "temperature": 0
    }
    response_data = requests.post(url, headers=headers, json=payload, timeout=30).json()
    # print(response_data)
    choices = response_data.get('choices')
    content = None
    if choices and isinstance(choices, list) and len(choices) > 0:
        first_choice = choices[0]
        message = first_choice.get('message')
        if message:
            content = message.get('content')
    if content and ord(content[0]) == 32:
        content = content[1:]
    if content and content[:2] == '\n\n':
        content = content[2:]
    return content


if __name__ == '__main__':
    result = ai_analyze_call_quality("""广州大麦-月月: 面谈：陈婉雯，13509958485，40年家族企业，在佛山，做玻璃加工，想推广建筑玻璃，BToB，直播会议全程跟的，非常认可我们，最近在做升级，先谈一下看看，后面会来公司面谈 周五回复，我到时候联系她，高概率 随时沟通，解答了疑问，高概率 他们老板想继续过来下，晚点他给我具体时间确定""") # pylint: disable=line-too-long
    print(result.replace("\n", " "))
