import json
import os
import re
import hashlib


def extract_json_object(content, error_line):
    lines = content.splitlines()
    max_lines = len(lines)

    # 从错误行向上找到 '{'
    start = error_line - 1
    while start >= 0 and '{' not in lines[start]:
        start -= 1
    if start < 0:
        return None

    # 从错误行向下找到 '}'
    end = error_line - 1
    brace_count = 0
    found_start = False
    obj_lines = []
    for i in range(start, max_lines):
        line = lines[i]
        obj_lines.append(line)
        brace_count += line.count('{')
        brace_count -= line.count('}')
        if brace_count == 0 and found_start:
            break
        if line.count('{') > 0:
            found_start = True

    if brace_count!= 0:
        # 如果括号不匹配，尝试更复杂的处理逻辑（这里只是示例，可以根据实际情况扩展）
        # 比如，从下一行开始继续查找匹配的 '}'
        if brace_count > 0:
            end += 1
            while end < max_lines and brace_count > 0:
                line = lines[end]
                brace_count += line.count('{')
                brace_count -= line.count('}')
                end += 1
            if brace_count!= 0:
                return None
            else:
                return '\n'.join(lines[start:end])
        else:
            start -= 1
            while start >= 0 and brace_count < 0:
                line = lines[start]
                brace_count += line.count('{')
                brace_count -= line.count('}')
                start -= 1
            if brace_count!= 0:
                return None
            else:
                return '\n'.join(lines[start + 1:error_line])
    return '\n'.join(obj_lines) if brace_count == 0 else None


def check_json_format(file_path, output_file):
    errors = []
    initial_hash = None
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf - 8') as f:
            content = f.read()
            initial_hash = hashlib.sha256(content.encode('utf - 8')).hexdigest()

    if not os.path.exists(file_path):
        errors.append("错误: 2024.json文件不存在。")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            try:
                json.loads(content)
                errors.append("2024.json格式正确，无错误。")
            else:
                raise json.JSONDecodeError("", "", 0)
            # except json.JSONDecodeError as e:
            #     error_msg = str(e)
            #     line_num = e.lineno
            #     col_num = e.colno
            #     char_pos = e.pos

            #     errors.append(f"行 {line_num} 列 {col_num}: {error_msg}。可能是缺少逗号或数组/对象未正确闭合，建议检查结构。")

            #     # 尝试提取并修复对象
            #     obj_text = extract_json_object(content, line_num)
            #     if obj_text:
            #         errors.append("原始出错对象：")
            #         errors.extend(obj_text.splitlines())

            #         try:
            #             obj = json.loads(obj_text)
            #         except Exception as inner_e:
            #             # 轻微修复：替换中文冒号、非法控制字符等
            #             fixed_text = obj_text.replace('：', ':').replace('\u2028', '').replace('\u2029', '')
            #             try:
            #                 obj = json.loads(fixed_text)
            #                 errors.append("尝试自动修复：替换了中文冒号或控制字符")
            #             except Exception:
            #                 errors.append("对象依然无法解析，请手动修复。")
            #                 obj = None

            #         if obj:
            #             obj["name"] = "更新日期: 25.04.18"
            #             formatted = json.dumps(obj, ensure_ascii=False, indent=4)
            #             compact = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            #             errors.append("修正后的对象（格式化）:")
            #             errors.extend(formatted.splitlines())
            #             errors.append("修正后的对象（紧凑单行）:")
            #             errors.append(compact)
            #     else:
            #         errors.append("无法定位到错误对象，请检查对应行附近。")

    final_hash = None
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf - 8') as f:
            content = f.read()
            final_hash = hashlib.sha256(content.encode('utf - 8')).hexdigest()
    if initial_hash!= final_hash:
        errors.append("警告: 在处理过程中2024.json文件可能被修改，结果可能不准确。")

    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(errors))
    print(f"✅ 生成 {output_file} 完成。")


if __name__ == "__main__":
    json_file = "2024.json"
    output_file = "错误状态.txt"
    check_json_format(json_file, output_file)
