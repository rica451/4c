import json
from openai import OpenAI
from typing import List, Dict

def generate_character(client: OpenAI, model: str, existing_names: List[str]) -> Dict[str, str]:
    """生成单个人物数据（增强版）"""
    prompt = f"""请严格按以下格式生成一个中国古人JSON对象：
{{
    "name": "姓名（中文）",
    "desc": "50字内描述，包含时代、流派/身份、风格特征、重要经历等要素"
}}

要求：
1. 生成的人物必须不在以下已生成名单中：{existing_names}
2. 生成的人物种类包括，中国小说中的，电视剧中的，神话里的或是真实存在的，随机选一种
3. 生成的人物男女比例为6:4
3. 不要使用markdown格式
4. 描述需包含独特识别特征
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个精通中国历史文化的助手，擅长生成多样化人物"},
            {"role": "user", "content": prompt}
        ],
        temperature=2.0,  # 提高随机性
        response_format={"type": "json_object"},
        max_tokens=200
    )
    
    try:
        data = json.loads(response.choices[0].message.content)
        # 强制校验关键字段
        if "name" not in data or "desc" not in data:
            raise ValueError("Invalid format")
        return data
    except:
        return {"name": "生成失败", "desc": "请重试"}

def generate_role_data(num_characters: int = 5) -> List[Dict]:
    """生成指定数量的人物数据（增强版）"""
    base_url = "https://api.ppinfra.com/v3/openai"
    api_key = "sk_3IwzOCr3JVfLtDyfkFqf3-kidlfJp3wxzko9w38BSH0"
    model = "deepseek/deepseek-v3-0324"
    
    client = OpenAI(base_url=base_url, api_key=api_key)
    
    characters = []
    existing_names = []
    
    while len(characters) < num_characters:
        char = generate_character(client, model, existing_names)
        # 强化校验逻辑
        if (
            char["name"] not in existing_names 
            and len(char["desc"]) <= 50 
            and char["name"] not in ["生成失败"]  # 黑名单机制
        ):
            characters.append(char)
            existing_names.append(char["name"])
            print(f"已生成 {len(characters)}/{num_characters}：{char['name']}")

            # 每隔5个角色保存一次
            if len(characters) % 5 == 0:
                with open("role_data1.json", "w", encoding="utf-8") as f:
                    json.dump(characters, f, ensure_ascii=False, indent=2)
    
    # 最终保存剩余数据（如果总数不是5的倍数）
    if len(characters) % 5 != 0:
        with open("role_data.json", "w", encoding="utf-8") as f:
            json.dump(characters, f, ensure_ascii=False, indent=2)
    
    return characters

if __name__ == "__main__":
    role_data = generate_role_data(1000)
    print("生成结果示例：")
    print(json.dumps(role_data, ensure_ascii=False, indent=2))