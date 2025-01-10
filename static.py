def count_lines_of_code(file_path):
    total_lines = 0

    if not file_path:
        print("文件路径不能为空")
        return total_lines

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 如果这一行只包含空白字符，跳过
                if line.strip():
                    total_lines += 1
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在")

    return total_lines

if __name__ == "__main__":
    file_path = input("请输入要统计的 Python 文件路径：")
    lines = count_lines_of_code(file_path)
    print(f"在文件 {file_path} 中共计 {lines} 行代码。")
