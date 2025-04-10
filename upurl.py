import json
import requests
import warnings
import re
import os
import time
from urllib3.exceptions import InsecureRequestWarning
from copy import deepcopy

# 全局变量
last_site = None
successful_urls = []

# 日志函数保持不变
def log_message(message, site_name=None, step="", max_error_length=80):
    global last_site
    status_emojis = {
        '[开始]': '🚀', '[成功]': '✅', '[完成]': '🎉', '[失败]': '❌',
        '[超时]': '⏳', '[警告]': '⚠️', '[错误]': '🚨', '[信息]': 'ℹ️',
        '[选择]': '🔍', '[连接失败]': '🔌'
    }
    if site_name and site_name != last_site:
        print(f"\n{'✨ ' + '=' * 38 + ' ✨'}")
        print(f"🌐 [站点: {site_name}]")
        print(f"{'✨ ' + '=' * 38 + ' ✨'}")
        last_site = site_name
    for status, emoji in status_emojis.items():
        if status in message:
            message = message.replace(status, f"{status} {emoji}")
            break
    else:
        message = f"{message} 📢"
    if "[连接失败]" in message or "[错误]" in message:
        if len(message) > max_error_length:
            message = message[:max_error_length] + "..."
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{step}] {message}") if step else print(message)

# 修改后的站点映射
site_mappings = {
    '立播': 'libo', '闪电': 'shandian', '欧哥': 'ouge', '小米': 'xiaomi', '多多': 'duoduo',
    '蜡笔': 'labi', '至臻': 'zhizhen', '木偶': 'mogg', '六趣': 'liuqu', '虎斑': 'huban',
    '下饭': 'xiafan', '玩偶': 'wogg', '星剧社': 'star2'
}

# 修改后的 JSM 映射
jsm_mapping = {
    "Libvio": "libo", "Xiaomi": "xiaomi", "yydsys": "duoduo", "蜡笔网盘": "labi",
    "玩偶 | 蜡笔": "labi", "至臻|网盘": "zhizhen", "Huban": "huban", "Wogg": "wogg",
    "Mogg": "mogg", "玩偶 | 闪电uc": "shandian",
    "玩偶 | 小米": "xiaomi", "玩偶 | 多多": "duoduo", "玩偶 | 木偶": "mogg",
    "玩偶gg": "wogg", "星剧社": "star2", "夸克至臻弹幕": "zhizhen",
    "玩偶": "wogg"
}

# 修改后的兜底 URL 配置
fallback_url_config = {
    "立播": [
        "https://libvio.mov", "https://www.libvio.cc", "https://libvio.la",
        "https://libvio.pro", "https://libvio.fun", "https://libvio.me",
        "https://libvio.in", "https://libvio.site", "https://libvio.art",
        "https://libvio.com", "https://libvio.vip", "https://libvio.pw",
        "https://libvio.link"
    ],
    "闪电": ["http://1.95.79.193", "http://1.95.79.193:666"],
    "欧哥": ["https://woog.nxog.eu.org"],
    "小米": [
        "http://www.54271.fun", "https://www.milvdou.fun", "http://www.54271.fun",
        "https://www.mucpan.cc", "https://mucpan.cc", "http://milvdou.fun"
    ],
    "多多": [
        "https://tv.yydsys.top", "https://tv.yydsys.cc", "https://tv.214521.xyz",
        "http://155.248.200.65"
    ],
    "蜡笔": ["http://feimaoai.site", "https://feimao666.fun", "http://feimao888.fun"],
    "至臻": [
        "https://mihdr.top", "http://www.miqk.cc", "https://xiaomiai.site"
    ],
    "六趣": ["https://wp.0v.fit"],
    "虎斑": ["http://103.45.162.207:20720"],
    "下饭": ["http://txfpan.top", "http://www.xn--ghqy10g1w0a.xyz"],
    "玩偶": [
        "https://wogg.xxooo.cf", "https://wogg.333232.xyz", "https://www.wogg.one",
        "https://www.wogg.lol", "https://www.wogg.net"
    ],
    "木偶": [
        "https://tv.91muou.icu", "https://mo.666291.xyz", "https://mo.muouso.fun",
        "https://aliii.deno.dev", "http://149.88.87.72:5666"
    ],
    "星剧社": ["https://mlink.cc/520TV"]
}

# 其余函数保持不变
# 文件路径处理
def get_file_path(filename):
    return f"./{filename}"

# 加载 2024.json
def load_jsm_config():
    jsm_path = get_file_path('2024.json')
    if os.path.exists(jsm_path):
        try:
            with open(jsm_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                log_message(f"[成功] 读取 2024.json: {jsm_path}", step="配置加载")
                return data
        except Exception as e:
            log_message(f"[错误] 读取 2024.json 失败: {str(e)}", step="配置加载")
            return {}
    else:
        log_message(f"[错误] 2024.json 不存在: {jsm_path}", step="配置加载")
        return {}

# 加载现有 url.json
def load_existing_config():
    url_path = get_file_path('url.json')
    if os.path.exists(url_path):
        try:
            with open(url_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                log_message(f"[成功] 读取 url.json: {url_path}", step="配置加载")
                return data
        except Exception as e:
            log_message(f"[错误] 读取 url.json 失败: {str(e)}", step="配置加载")
            return {}
    return {}

# 测试 URL 并记录成功结果
def test_url(url, site_name=None):
    global successful_urls
    try:
        response = requests.get(
            url,
            timeout=7,
            verify=False,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        if response.status_code == 200:
            latency = response.elapsed.total_seconds()
            log_message(f"[成功] {url} | 延迟: {latency:.2f}s", site_name, "URL测试")
            successful_urls.append(f"{site_name}: {url} (延迟: {latency:.2f}s)")
            return latency
        log_message(f"[失败] HTTP状态码 {response.status_code}", site_name, "URL测试")
    except Exception as e:
        log_message(f"[连接失败] {str(e)}", site_name, "URL测试")
    return None

# 获取最佳 URL
def get_best_url(urls, site_name=None, existing_url=None):
    if not isinstance(urls, list):
        return urls
    for url in urls:
        latency = test_url(url, site_name)
        if latency is not None:
            log_message(f"[选择] 选中 {url}", site_name, "URL选择")
            return url
    log_message(f"[警告] 无可用URL，使用现有: {existing_url}", site_name, "URL选择")
    return existing_url

# 星剧社特殊处理
def get_star2_real_url(source_url):
    try:
        response = requests.get(
            source_url,
            timeout=8,
            verify=False,
            headers={'Referer': 'https://mlink.cc/'}
        )
        if response.status_code == 200:
            match = re.search(r'(?:href|src|data-?url)=["\'](https?://[^"\']*?star2\.cn[^"\']*)["\']', response.text, re.I)
            if match:
                real_url = match.group(1).strip().rstrip('/')
                log_message(f"[成功] 提取真实链接: {real_url}", "星剧社", "链接解析")
                return real_url
        log_message("[失败] 未找到有效链接", "星剧社", "链接解析")
    except Exception as e:
        log_message(f"[错误] 解析失败: {str(e)}", "星剧社", "链接解析")
    return None

# 数据合并去重
def merge_url_data(*dicts):
    merged = {}
    for d in dicts:
        if not d: continue
        for site, urls in d.items():
            merged.setdefault(site, []).extend(urls if isinstance(urls, list) else [urls])
    return {k: list(dict.fromkeys(v)) for k, v in merged.items()}

# 替换 URL
def replace_urls(data, urls):
    if not isinstance(data, dict) or 'sites' not in data:
        log_message("[错误] 2024.json 缺少 'sites' 字段", step="URL替换")
        return data

    api_urls = {jsm_key: urls.get(jsm_value) for jsm_key, jsm_value in jsm_mapping.items()}
    sites = data['sites']
    replaced_count = 0

    for item in sites:
        if not isinstance(item, dict):
            continue
        key = item.get('key')
        ext = item.get('ext')
        new_url = api_urls.get(key)

        if not new_url:
            log_message(f"[警告] 未找到 {key} 的新 URL", step="URL替换")
            continue

        if isinstance(ext, dict):
            old_url = ext.get('siteUrl') or ext.get('site')
            target_key = 'siteUrl' if 'siteUrl' in ext else 'site'
            if old_url and old_url != new_url:
                ext[target_key] = new_url
                replaced_count += 1
                log_message(f"[成功] 替换 {key} 的 {target_key}: {old_url} -> {new_url}", step="URL替换")
            elif not old_url:
                ext[target_key] = new_url
                replaced_count += 1
                log_message(f"[成功] 添加 {key} 的 {target_key}: {new_url}", step="URL替换")
        elif isinstance(ext, str):
            parts = ext.split('$$$')
            if len(parts) > 1 and parts[1].strip().startswith('http'):
                old_url = parts[1]
                if old_url != new_url:
                    parts[1] = new_url
                    item['ext'] = '$$$'.join(parts)
                    replaced_count += 1
                    log_message(f"[成功] 替换 {key}: {old_url} -> {new_url}", step="URL替换")
            else:
                if ext != new_url:
                    item['ext'] = new_url
                    replaced_count += 1
                    log_message(f"[成功] 设置 {key} 的 ext: {new_url}", step="URL替换")
        elif ext is None:
            item['ext'] = {'site': new_url}
            replaced_count += 1
            log_message(f"[成功] 添加 {key} 的 site: {new_url}", step="URL替换")
        if 'url' in item:
            del item['url']

    log_message(f"[完成] 总共替换了 {replaced_count} 个链接", step="URL替换")
    return data

# 更新 2024.json，保留原始格式
def update_jsm_config(urls):
    jsm_path = get_file_path('2024.json')
    if not os.path.exists(jsm_path):
        log_message(f"[错误] 2024.json 不存在: {jsm_path}", step="配置更新")
        return False

    # 备份原始文件
    backup_path = f"{jsm_path}.bak"
    try:
        with open(jsm_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            if not original_content.strip():
                log_message("[错误] 2024.json 文件为空，不进行操作", step="配置更新")
                return False
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(original_content)
        log_message(f"[成功] 备份 2024.json 到 {backup_path}", step="配置更新")
    except Exception as e:
        log_message(f"[错误] 备份失败: {str(e)}", step="配置更新")
        return False

    # 加载原始 JSON 数据
    try:
        with open(jsm_path, 'r', encoding='utf-8') as f:
            jsm_data = json.load(f)
    except Exception as e:
        log_message(f"[错误] 解析 2024.json 失败: {str(e)}", step="配置更新")
        return False

    # 确保 jsm_data 包含 sites 字段
    if not isinstance(jsm_data, dict) or 'sites' not in jsm_data:
        log_message("[错误] 2024.json 缺少 'sites' 字段，不进行操作", step="配置更新")
        return False

    if not jsm_data['sites']:
        log_message("[错误] 2024.json 中 'sites' 字段为空，不进行操作", step="配置更新")
        return False

    # 替换 URL
    updated_data = replace_urls(deepcopy(jsm_data), urls)
    if not updated_data or not updated_data.get('sites'):
        log_message("[错误] 更新后数据为空或缺少 'sites' 字段，不覆盖文件", step="配置更新")
        return False

    # 读取原始文件内容（逐行）
    try:
        with open(jsm_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        log_message(f"[错误] 读取原始文件内容失败: {str(e)}", step="配置更新")
        return False

    # 构建更新后的内容，保留原始格式
    formatted_lines = []
    site_index = 0
    sites = updated_data['sites']
    in_sites = False

    for line in lines:
        line = line.rstrip()
        if '"sites": [' in line:
            in_sites = True
            formatted_lines.append(line)
            continue
        if in_sites and site_index < len(sites):
            if line.strip().startswith('{'):
                # 使用替换后的 item 构造新行
                item = sites[site_index]
                # 提取原始行的缩进
                indent = len(line) - len(line.lstrip())
                # 构造新行，保留原始格式
                new_line = ' ' * indent + '{'
                # 按字段顺序构造，保持原始顺序
                fields = []
                for key in item:
                    if key == 'ext':
                        # 特殊处理 ext 字段
                        if isinstance(item[key], dict):
                            fields.append(f'"ext": {json.dumps(item[key], ensure_ascii=False)}')
                        elif isinstance(item[key], str):
                            fields.append(f'"ext": "{item[key]}"')
                        else:
                            fields.append(f'"ext": {json.dumps(item[key], ensure_ascii=False)}')
                    else:
                        if isinstance(item[key], (int, bool)):
                            fields.append(f'"{key}": {item[key]}')
                        elif isinstance(item[key], (dict, list)):
                            fields.append(f'"{key}": {json.dumps(item[key], ensure_ascii=False)}')
                        else:
                            fields.append(f'"{key}": "{item[key]}"')
                new_line += ' ' + ', '.join(fields) + ' }'
                if site_index < len(sites) - 1:
                    new_line += ','
                formatted_lines.append(new_line)
                site_index += 1
            else:
                formatted_lines.append(line)
        else:
            in_sites = False
            formatted_lines.append(line)

    # 调试：输出生成的 formatted_lines
    log_message(f"[调试] 生成的 formatted_lines: {formatted_lines}", step="配置更新")

    # 写入更新后的文件
    try:
        with open(jsm_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(formatted_lines))
        log_message(f"[完成] 2024.json 更新成功: {jsm_path}", step="配置更新")
        return True
    except Exception as e:
        log_message(f"[错误] 2024.json 更新失败: {str(e)}", step="配置更新")
        return False

# 保存成功的 URL 到文件
def save_successful_urls():
    path = get_file_path('URL_sucsses.txt')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(successful_urls))
        log_message(f"[成功] 保存成功 URL 到: {path}", step="数据持久化")
    except Exception as e:
        log_message(f"[错误] 保存 URL_sucsses.txt 失败: {str(e)}", step="数据持久化")

# 主流程
def process_urls():
    global successful_urls
    successful_urls = []
    log_message("[开始] 启动URL更新流程", step="主流程")

    existing_config = load_existing_config()
    reverse_site_mapping = {v: k for k, v in site_mappings.items()}

    data_sources = []
    try:
        remote_data = requests.get(
            'https://github.catvod.com/https://raw.githubusercontent.com/celin1286/xiaosa/main/yuan.json',
            timeout=10
        ).json()
        data_sources.append(remote_data)
        log_message("[成功] 远程数据加载完成", step="数据收集")
    except Exception as e:
        log_message(f"[错误] 远程数据获取失败: {str(e)}", step="数据收集")

    local_path = get_file_path('yuan.json')
    if os.path.exists(local_path):
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                data_sources.append(json.load(f))
                log_message("[成功] 本地数据加载完成", step="数据收集")
        except Exception as e:
            log_message(f"[错误] 本地数据读取失败: {str(e)}", step="数据收集")

    data_sources.append(fallback_url_config)
    merged_data = merge_url_data(*data_sources)

    result = {'url': {}}
    stats = {'total': 0, 'success': 0, 'failed': [], 'changed': []}

    for cn_name, urls in merged_data.items():
        stats['total'] += 1
        site_key = site_mappings.get(cn_name)
        existing_url = existing_config.get(site_key, '')

        if cn_name == '星剧社':
            best_source = get_best_url(urls, cn_name, existing_url)
            final_url = get_star2_real_url(best_source) if best_source else existing_url
        else:
            final_url = get_best_url(urls, cn_name, existing_url) or existing_url

        if final_url:
            result['url'][site_key] = final_url
            if existing_url and existing_url != final_url:
                stats['changed'].append(f"{cn_name}: {existing_url} -> {final_url}")
                log_message(f"[更新] 配置变更检测", cn_name, "结果处理")
            stats['success'] += 1
        else:
            stats['failed'].append(cn_name)
            log_message("[警告] 无可用URL", cn_name, "结果处理")

    output_files = {
        'yuan.json': merged_data,
        'url.json': result['url']
    }
    for filename, data in output_files.items():
        path = get_file_path(filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            log_message(f"[成功] 保存文件: {path}", step="数据持久化")
        except Exception as e:
            log_message(f"[错误] 文件保存失败: {str(e)}", step="数据持久化")

    save_successful_urls()

    log_message("[开始] 启动jsm配置更新", step="主流程")
    update_success = update_jsm_config(result['url'])
    log_message(f"[{'成功' if update_success else '失败'}] jsm配置更新完成", step="主流程")

    log_message(
        f"[完成] 处理结果: {stats['success']}/{stats['total']} 成功\n"
        f"url.json变更项 ({len(stats['changed'])}): {', '.join(stats['changed']) if stats['changed'] else '无'}\n"
        f"url.json失败项 ({len(stats['failed'])}): {', '.join(stats['failed']) if stats['failed'] else '无'}",
        step="统计报告"
    )
    return stats['success'] > 0

# 主函数
def main():
    warnings.simplefilter('ignore', InsecureRequestWarning)
    process_urls()

if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed = time.time() - start_time
    print(f"总耗时: {elapsed:.2f}秒")
