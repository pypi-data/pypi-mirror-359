import json
import os
import sys
from typing import List, Optional

from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("critical_thinking2")


@mcp.tool()
def critical_thinking(
    fine: str = "",
    person: str = "",
    previous_events: str = "",
    screenplay_completed: str = "",
    story_beat: str = "",
    episode_summary: str = "",
) -> dict:
    """
    简介：
        能够实现从粗分场到细分场到提示词生成，模型能够通过这份提示词实现对细分场剧本的创作。
    功能：
        1. 生成结构化的创作提示词。你需要将生成的提示词作为真正的提示词。
        2. 你需要接收生成的提示词，然后依据生成的提示词进行回答。
    变量说明：
    
    - fine: 本场剧本粗分场内容，若为空则自动读取fine.txt
    - person: 核心人物小传内容，若为空则自动读取person.txt
    - previous_events: 本场前情内容，若为空则自动读取previous_events.txt
    - screenplay_completed: 已完成剧本内容，若为空则自动读取screenplay_completed.txt
    - story_beat: 本集情节点内容，若为空则自动读取story_beat.txt
    - episode_summary: 本集故事梗概内容，若为空则自动读取episode_summary.txt
    - context_content: 其它上下文内容
    若上述变量为空，上述txt文件可能在当前目录下，也可能在当前目录的Resource目录下，如果用户的提示词中没有具体给出，你需要去目录下自动尝试查找并读取。
    """
    # config = {
    #     "api_key": "",
    #     "base_url": ""
    # }

    def load_prompt(prompt_file: str) -> str:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prompt_file)
        if os.path.exists(prompt_file_path):
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"警告: 找不到Prompt文件 {prompt_file}，使用默认Prompt")
            return ""

    def load_var_from_file(var_name: str, value: str) -> str:
        if value:
            return value
        file_name = f"{var_name}.txt"
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def format_prompt(prompt_template: str, **kwargs) -> str:
        return prompt_template.format(**kwargs)

    # def get_llm(model_name):
    #     from langchain_openai import ChatOpenAI
    #     from langchain_core.utils import get_from_dict_or_env
    #     from pydantic import SecretStr
    #     api_key = get_from_dict_or_env(config, 'api_key', 'OPENAI_API_KEY')
    #     return ChatOpenAI(model=model_name,
    #                       temperature=1,
    #                       base_url=config['base_url'],
    #                       api_key=SecretStr(api_key) if api_key else None)

    # 自动填充变量
    fine = load_var_from_file('fine', fine)
    person = load_var_from_file('person', person)
    previous_events = load_var_from_file('previous_events', previous_events)
    screenplay_completed = load_var_from_file('screenplay_completed', screenplay_completed)
    story_beat = load_var_from_file('story_beat', story_beat)
    episode_summary = load_var_from_file('episode_summary', episode_summary)

    prompt_template = load_prompt('prompt.md')
    if not prompt_template:
        prompt_template = ""
    prompt = format_prompt(
        prompt_template,
        fine=fine,
        person=person,
        **{
            'screenplay_completed': screenplay_completed,
            'previous_events': previous_events,
            'story_beat': story_beat,
            'episode_summary': episode_summary
        }
    )
    # model = get_llm('qwen2.5-72b-instruct')
    # response = model.invoke(prompt)
    # return {"response": response.content}
    return {"response": prompt}


def main():
    """Entry point for the MCP server."""
    # Ensure UTF-8 encoding for stdin/stdout
    if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    if hasattr(sys.stdin, 'buffer') and sys.stdin.encoding != 'utf-8':
        import io
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', line_buffering=True)

    # Flush stdout to ensure no buffered content remains
    sys.stdout.flush()

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    # When running the script directly, ensure we're in the right directory
    import os
    import sys

    # Add the parent directory to sys.path if needed
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Run the server
    main()