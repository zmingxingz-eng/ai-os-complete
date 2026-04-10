from pathlib import Path
import sys

TEMPLATE_CONTEXT = """# 模块上下文

模块名称：
- {module}

模块职责：
- 

当前状态：
- 

关键约束：
- 

已知风险：
- 

禁止破坏点：
- 

后续扩展点：
- 
"""

TEMPLATE_CHANGELOG = """# 模块变更记录

日期：
- 

变更主题：
- 初始化模块上下文

变更原因：
- 为模块建立可持续接续能力

影响文件：
- 

影响范围：
- 

是否有兼容风险：
- 否

后续动作：
- 后续重大变更后持续补充
"""

def main():
    if len(sys.argv) < 2:
        print("usage: python bootstrap_module_context.py <module_path>")
        return
    module_path = Path(sys.argv[1])
    ai_dir = module_path / ".ai"
    ai_dir.mkdir(parents=True, exist_ok=True)
    module_name = module_path.name

    context_file = ai_dir / "module_context.md"
    changelog_file = ai_dir / "change_log.md"

    if not context_file.exists():
        context_file.write_text(TEMPLATE_CONTEXT.format(module=module_name), encoding="utf-8")
    if not changelog_file.exists():
        changelog_file.write_text(TEMPLATE_CHANGELOG, encoding="utf-8")

    print(f"module context initialized for {module_path}")

if __name__ == "__main__":
    main()
