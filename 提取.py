import os

# ===== 配置 =====
EXTENSIONS = {
    ".py", ".cpp", ".h", ".c", ".hpp",
    ".js", ".ts", ".java", ".go", ".rs"
}

IGNORE_DIRS = {
    ".git", "__pycache__", "build", "dist", ".idea", ".vscode"
}

OUTPUT_FILE = "all_code.txt"


def count_lines(filepath):
    total = 0
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for _ in f:
                total += 1
    except Exception:
        return 0
    return total


def scan_and_merge(root):
    total_files = 0
    total_lines = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for dirpath, dirnames, filenames in os.walk(root):
            # 过滤目录
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

            for file in filenames:
                ext = os.path.splitext(file)[1]
                if ext not in EXTENSIONS:
                    continue

                filepath = os.path.join(dirpath, file)

                lines = count_lines(filepath)
                total_lines += lines
                total_files += 1

                # 写入文件头（路径标识）
                out.write("\n" + "=" * 80 + "\n")
                out.write(f"FILE: {filepath}\n")
                out.write("=" * 80 + "\n")

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        out.write(f.read())
                except Exception:
                    out.write("[ERROR: Cannot read file]\n")

                out.write("\n")  # 文件间隔

    return total_files, total_lines


if __name__ == "__main__":
    import sys

    # if len(sys.argv) < 2:
    #     print("Usage: python code_counter_and_merge.py <project_path>")
    #     exit(1)

    # root = sys.argv[1]
    root = './'
    total_files, total_lines = scan_and_merge(root)

    print("=" * 50)
    print(f"Total Files : {total_files}")
    print(f"Total Lines : {total_lines}")
    print(f"Output File : {OUTPUT_FILE}")
    print("=" * 50)