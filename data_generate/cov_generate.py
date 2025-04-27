from openai import OpenAI
import json
import time
import random
from tqdm import tqdm

# 配置API参数
base_url = "https://api.ppinfra.com/v3/openai"
api_key = "sk_3IwzOCr3JVfLtDyfkFqf3-kidlfJp3wxzko9w38BSH0"
model = "deepseek/deepseek-v3-0324"

# 初始化客户端
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

# 预定义角色库（可扩展）
with open('role_data.json', 'r', encoding='utf-8') as f:
    ROLE_LIBRARY = json.load(f)


def generate_single_dialogue():
    """生成单条对话数据（含错误重试机制）"""
    max_retries = 3
    retry_delay = 5  # 秒
    
    # 随机选择两个不同角色
    role1, role2 = random.sample(ROLE_LIBRARY, 2)
    system_desc = f"{role1['name']}，{role1['desc']}"
    user_role = f"{role2['name']}，{role2['desc']}"

    prompt = f"""
    请生成一个包含5-7轮对话的中文古人交流数据集，严格遵循以下要求：
    
    角色配置：
    - 系统角色({role2['name']}): {{
        "from": "system",
        "value": "你扮演{user_role}"
    }}
    - 用户角色(不扮演任何人): 使用"from":"human"标签
    - 系统角色({role2['name']}): 使用"from":"assistant"标签

    对话要求：
    1. {role2['name']}的说话语言风格符合{role2['name']}的历史背景
    2. 对话主题包含：日常闲聊、人生际遇、诗词创作、时局评论、自然咏叹
    3. human那一方是用户，要符合跟AI聊天的特点，保持口语化现代风格，说话通俗易懂需求明确
    4. 每轮对话长度15-40字，对话要前后贯通，不要忽然切换话题
    5. 输出严格使用以下JSON格式：
    {{
        "conversations": [
            {{系统角色配置}},
            {{"from":"human", "value":"..."}},
            {{"from":"assistant", "value":"..."}},
            // 后续对话轮次...
        ]
    }}
    """

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是专业的历史对话数据集生成器"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # 验证数据格式
            data = json.loads(response.choices[0].message.content)
            assert isinstance(data, dict)
            assert "conversations" in data
            assert len(data["conversations"]) >= 5
            return data
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"请求失败，{retry_delay}秒后重试... (错误: {str(e)})")
                time.sleep(retry_delay)
            else:
                print(f"生成失败，跳过该条数据 (最终错误: {str(e)})")
                return None

def generate_batch_data(total=1000, batch_size=20):
    """批量生成对话数据集"""
    all_data = []
    
    # 进度条显示
    with tqdm(total=total, desc="生成进度") as pbar:
        while len(all_data) < total:
            # 批量生成
            batch = []
            for _ in range(batch_size):
                if len(all_data) >= total:
                    break
                
                data = generate_single_dialogue()
                if data:
                    batch.append(data)
                    pbar.update(1)
            
            # 分块保存
            if batch:
                timestamp = int(time.time())
                filename = f"ancient_dialogues_{timestamp}_part{(len(all_data)//batch_size)+380}.json"
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(batch, f, ensure_ascii=False, indent=2)
                
                all_data.extend(batch)
            
            # 遵守速率限制（根据API调整）
            time.sleep(10)  # 每批请求间隔10秒

    print(f"\n成功生成{len(all_data)}条对话数据！")

if __name__ == "__main__":
    generate_batch_data(total=2400)