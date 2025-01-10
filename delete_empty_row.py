# 打开源代码文件
with open('1.py', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 去除空行
non_empty_lines = [line for line in lines if line.strip() != '']

# 将修改后的内容写回文件
with open('1.py', 'w', encoding='utf-8') as file:
    file.writelines(non_empty_lines)
