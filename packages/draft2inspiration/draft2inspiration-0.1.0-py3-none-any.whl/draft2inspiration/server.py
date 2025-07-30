import json
import os
import sys
from typing import List, Optional
import random
from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("critical_thinking2")



# 灵感条目数据结构

def new_inspiration(content, tags=None, source=None):
    import time
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    unique_id = f"{int(time.time() * 1000)}_{random.randint(1000,9999)}"
    return {
        "id": unique_id,
        "content": content,
        "tags": tags or [],
        "source": source,
        "created_at": now,
        "updated_at": now
    }

class InspirationLibrary:
    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            base = Path(__file__).parent / "storage"
            self.storage_dir = base
        else:
            self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.file = self.storage_dir / "inspiration_entries.json"
        self._load()

    def _load(self):
        if self.file.exists():
            with open(self.file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = data.get("entries", [])
        else:
            self.entries = []

    def _save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump({"entries": self.entries}, f, ensure_ascii=False, indent=2)

    def add_entry(self, entry: dict):
        self.entries.append(entry)
        self._save()

    def get_all(self) -> List[dict]:
        return list(self.entries)

    def get_by_tag(self, tag: str) -> List[dict]:
        return [e for e in self.entries if tag in e.get("tags", [])]

    def delete(self, entry_id: str):
        self.entries = [e for e in self.entries if e.get("id") != entry_id]
        self._save()

    def clear(self):
        self.entries = []
        self._save()

    def import_entries(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        imported = data.get("entries", [])
        self.entries.extend(imported)
        self._save()

    def export_entries(self, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"entries": self.entries}, f, ensure_ascii=False, indent=2)

    def tag_stats(self):
        from collections import Counter
        tags = []
        for e in self.entries:
            tags.extend(e.get("tags", []))
        return Counter(tags)


def get_library():
    return InspirationLibrary()

library = get_library()

@mcp.tool()
def add_inspiration(content: str, tags: Optional[List[str]] = None, source: Optional[str] = None) -> dict:
    """
    该工具用于对灵感库进行操作：添加一条新的灵感条目。
    参数：
        content：灵感内容。
        tags：可选，标签列表。
        source：可选，灵感来源。
    返回：
        包含操作状态和新灵感条目的唯一ID。
    """
    entry = new_inspiration(content, tags, source)
    library.add_entry(entry)
    return {"status": "success", "id": entry["id"]}

@mcp.tool()
def list_inspirations(tag: Optional[str] = None) -> dict:
    """
    该工具用于对灵感库进行操作：列出所有灵感条目，或根据标签筛选灵感条目。
    参数：
        tag：可选，指定标签时只返回包含该标签的灵感条目。
    返回：
        灵感条目列表。
    """
    if tag:
        entries = library.get_by_tag(tag)
    else:
        entries = library.get_all()
    return {"entries": entries}

@mcp.tool()
def delete_inspiration(entry_id: str) -> dict:
    """
    该工具用于对灵感库进行操作：根据ID删除指定的灵感条目。
    参数：
        entry_id：要删除的灵感条目的唯一ID。
    返回：
        操作状态。
    """
    library.delete(entry_id)
    return {"status": "success"}

@mcp.tool()
def clear_inspirations() -> dict:
    """
    该工具用于对灵感库进行操作：清空所有灵感条目。
    返回：
        操作状态。
    """
    library.clear()
    return {"status": "success"}

@mcp.tool()
def tag_statistics() -> dict:
    """
    该工具用于对灵感库进行操作：获取所有灵感条目的标签统计信息。
    返回：
        每个标签及其对应的条目数量。
    """
    stats = library.tag_stats()
    return {"tagStats": dict(stats)}

@mcp.tool()
def import_inspirations(file_path: str) -> dict:
    """
    该工具用于对灵感库进行操作：从指定的JSON文件导入灵感条目。
    参数：
        file_path：要导入的JSON文件路径。
    返回：
        操作状态。
    """
    library.import_entries(file_path)
    return {"status": "success"}

@mcp.tool()
def export_inspirations(file_path: str) -> dict:
    """
    该工具用于对灵感库进行操作：将所有灵感条目导出到指定的JSON文件。
    参数：
        file_path：导出目标JSON文件路径。
    返回：
        操作状态。
    """
    library.export_entries(file_path)
    return {"status": "success"}



@mcp.tool()
def critical_thinking(context_content: str) -> dict:
    """
    当用户需要查找灵感时，请务必通过该工具得到提示词，然后使用该提示词进行创作。
    从给定的上下文文件中获取资料，生成结构化的创作提示词。
    注意：如果当前的工具中有灵感存储相关的工具，可以请示用户是否进行灵感存储。
    
    
    输入：context_content - 从上下文文件中提取的内容资料
    输出：返回一个格式化的提示词，你应使用该提示词作为要求进行回复
    
    该工具会：
    1. 加载灵感处理模板
    2. 将上下文内容注入模板
    3. 生成完整的创作提示词
    4. 返回给你执行
    """
    config = {
    "api_key": "",
    "base_url": ""
}

    def load_prompt(prompt_file: str) -> str:
        """从项目根目录加载Prompt文件"""
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), prompt_file)
        if os.path.exists(prompt_file_path):
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"警告: 找不到Prompt文件 {prompt_file}，使用默认Prompt")
            return ""

    def format_prompt(prompt_template: str, **kwargs) -> str:
        """格式化Prompt模板"""
        return prompt_template.format(**kwargs)

    def get_llm(model_name):
        from langchain_openai import ChatOpenAI
        from langchain_core.utils import get_from_dict_or_env
        from pydantic import SecretStr
        
        api_key = get_from_dict_or_env(config, 'api_key', 'OPENAI_API_KEY')
        return ChatOpenAI(model=model_name,
                          temperature=1,
                          base_url=config['base_url'],
                          api_key=SecretStr(api_key) if api_key else None)
    prompt_template = load_prompt('prompt.md')
    if not prompt_template:
        prompt_template = ""
    prompt = format_prompt(prompt_template, docs1=context_content)
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