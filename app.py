# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

SYSTEM_PROMPT = """分析下面的英文文章，做成一份个人学习笔记。只输出最终结果，不要任何开场白或结语。

### 要求概览
- 文章展示 → 脚注解析 → 句子赏析 → 写作手法 → 背诵速查表，五个板块缺一不可。
- 所有板块内容尽量详尽，不要人为限制数量，把文中值得学习的地方都挖掘出来。
- 行文简洁清晰，像自己写给自己的笔记，不要导师口吻。

## 一、文章展示
- 用二级标题“## 文章”开头，然后给出整理后的文章全文。
- 将所有地道、精彩的词汇和词组用 **加粗** 标记，并紧接其后添加脚注标记 [^n]（n从1开始递增）。重复词汇只标注首次出现。
- 用 *斜体* 标记文中特别精彩的句子（不限数量，只要是觉得好就标）。

## 二、脚注解析
二级标题“## 📖 词汇词组精析”，按顺序解析每一个脚注，一个不能少。格式：

[^n]: **词/词组** (词性)
核心释义 + 为什么地道。
📖 联动：(具体影视台词或外刊句子，必须完整)
💡 仿写：(完整的英文仿写句)

- 脚注内部使用 <br> 换行。
- 脚注之间空一行。

## 三、句子赏析
二级标题“## 🖋️ 精彩句子赏析”。逐一赏析前面用 *斜体* 标出的每一个句子，每个句子包含：
- 原句
- 妙处（结构、修辞、用词、节奏等，简明点出）
- 仿写（模仿其特点写一个完整英文句）

## 四、写作手法分析
二级标题“## ✍️ 写作手法仿写”。选出文中突出的写作技巧，每个技巧包含：
- 技巧名称
- 原文呈现（引用文中句子）
- 效用分析（它为什么好）
- 实战仿写（用不同主题写一个英文段落，真正用上该技巧）

## 五、背诵速查表
二级标题“## 📋 背诵速查表”。用表格列出所有加粗词汇/词组，列：表达 | 释义 | 场景。

整份笔记用 Markdown 输出。"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    article = data.get('article', '').strip()
    api_key = data.get('api_key', '').strip()
    model = data.get('model', 'deepseek-chat').strip() or 'deepseek-chat'

    if not article:
        return jsonify({'error': '文章不能为空'}), 400
    if not api_key:
        return jsonify({'error': '请输入您的 DeepSeek API Key'}), 400

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    try:
        response = client.chat.completions.create(
            model=data.get('model', 'deepseek-chat'),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": article}
            ],
            temperature=0.7,
            max_tokens=16384
        )
        result = response.choices[0].message.content
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
