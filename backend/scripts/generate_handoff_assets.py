from pathlib import Path

BASE = Path(".")
context_runtime = BASE / ".ai" / "context_runtime"
checkpoints = BASE / ".ai" / "checkpoints"

def ensure_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")

def main():
    ensure_file(
        context_runtime / "session_summary.md",
        "# 会话摘要\n\n本轮主题：\n- \n\n本轮已完成：\n- \n\n本轮未完成：\n- \n\n关键决策：\n- \n\n影响文件：\n- \n\n下一步：\n- \n",
    )
    ensure_file(
        checkpoints / "latest-checkpoint.md",
        "# checkpoint: latest\n\n已验证：\n- \n\n未验证：\n- \n\n风险点：\n- \n\n当前结论：\n- \n",
    )
    print("handoff assets initialized")

if __name__ == "__main__":
    main()
