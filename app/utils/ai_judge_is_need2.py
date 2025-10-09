"""AI判断是否需要深入了解联合运营"""
# app/utils/ai_judge_is_need2.py
import requests

from app.core.config import settings

PROMPT = """

 **[TRANSCENDENT_ROLE]**

你是一个专业的通话质量分析专家。你的使命是根据提供的对话记录，分析客户意向度并生成通话总结。你需要客观分析客户的需求意向和通话质量。



 **[CORE_DIRECTIVE]**

分析以下提供的 `{{chat_log}}`，评估客户意向度并生成通话总结。客户意向度评分范围为1-100分，分数越高表示客户意向越强烈。

**[SCORING_RULES]**

1. **高意向（80-100分）**：  
   - 客户明确表示对产品有迫切需求，提出具体使用场景、功能痛点
   - 主动询问深度细节（如价格方案、配置对比、体验方式、售后保障等）
   - 主动提出约见、体验或要求添加微信/手机号等直接联系
   - 表现出强烈的购买意愿和决策能力

2. **中意向（50-79分）**：  
   - 客户表现出一定兴趣，愿意先了解产品信息
   - 愿意接受资料或进一步沟通
   - 对产品有基本认知但需要更多教育
   - 没有明确拒绝，保持开放态度

3. **低意向（20-49分）**：  
   - 客户礼貌回应但没有表现出强烈兴趣
   - 表示暂时不需要或有其他选择
   - 接通电话但不积极回应
   - 保持礼貌但缺乏参与度

4. **无意向（1-19分）**：  
   - 客户明确拒绝或表现出强烈负面情绪
   - 出现拒绝关键词（如"不需要/没兴趣/别打了/不考虑"等）
   - 直接挂断或拒绝沟通
   - 表现出明显的排斥态度

**[CALL_SUMMARY_RULES]**

通话总结应包含以下要素：
- 客户基本信息（如行业、公司规模等）
- 客户主要需求和痛点
- 产品匹配度分析
- 后续跟进建议
- 关键决策因素
- 客户态度和参与度

**[OUTPUT_FORMAT]**

输出必须是严格的 JSON 格式，示例如下：  

{
    "call_quality_score": 85,
    "call_summary": "客户是某科技公司CTO，对AI眼镜在会议场景的应用很感兴趣，主动询问了价格和配置，表示希望安排产品演示，意向度较高。建议安排技术团队对接，重点介绍会议记录和实时翻译功能。"
}

### 输出规则说明

1. **call_quality_score**：  
   - 1-100分的整数评分，代表客户意向度
   - 80-100分：高意向客户
   - 50-79分：中意向客户  
   - 20-49分：低意向客户
   - 1-19分：无意向客户

2. **call_summary**：  
   - 简洁的通话总结，包含客户需求、产品匹配度、跟进建议
   - 文字应专业、客观，便于后续跟进
   - 突出关键信息和决策因素

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
