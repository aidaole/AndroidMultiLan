import os
import json
import pandas as pd
from typing import Dict, List

def parse_arb_file(arb_path: str) -> Dict[str, str]:
    """
    解析单个ARB文件
    Args:
        arb_path: ARB文件路径
    Returns:
        Dict[str, str]: 包含(key, value)的字典
    """
    try:
        with open(arb_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 移除非翻译内容
            data.pop('@@locale', None)
            return data
    except Exception as e:
        print(f"解析ARB文件失败 {arb_path}: {str(e)}")
        return {}

def find_arb_files(project_path: str) -> Dict[str, str]:
    """
    在项目中查找所有intl_*.arb文件
    Args:
        project_path: 项目根目录路径
    Returns:
        Dict[str, str]: 语言代码到文件路径的映射
    """
    arb_files = {}
    l10n_path = os.path.join(project_path, 'lib', 'l10n')
    
    if not os.path.exists(l10n_path):
        print(f"多语言目录不存在: {l10n_path}")
        return arb_files

    for file_name in os.listdir(l10n_path):
        if file_name.startswith('intl_') and file_name.endswith('.arb'):
            # 从文件名中提取语言代码
            # 例如: intl_zh_CN.arb -> zh_CN, intl_en.arb -> en
            lang_code = file_name[5:-4]  # 移除 'intl_' 前缀和 '.arb' 后缀
            arb_files[lang_code] = os.path.join(l10n_path, file_name)
    
    return arb_files

def process_arb_files_to_excel(arb_files: Dict[str, str], output_path: str) -> None:
    """
    将ARB文件处理并导出为Excel
    Args:
        arb_files: 语言代码到文件路径的映射
        output_path: 输出文件路径
    """
    if 'zh_CN' not in arb_files:  # 修改这里，检查'zh_CN'
        raise Exception("未找到中文（zh_CN）的ARB文件作为默认语言")

    # 处理中文文件
    data = {'key': [], 'default': []}
    default_strings = parse_arb_file(arb_files['zh_CN'])  # 使用'zh_CN'作为key
    
    for key, value in default_strings.items():
        data['key'].append(key)
        data['default'].append(value)

    # 处理其他语言文件
    for lang_code, arb_path in arb_files.items():
        if lang_code == 'zh_CN':  # 修改这里，跳过'zh_CN'
            continue

        data[lang_code] = [''] * len(data['key'])
        strings = parse_arb_file(arb_path)
        
        for key, value in strings.items():
            try:
                index = data['key'].index(key)
                data[lang_code][index] = value
            except ValueError:
                print(f"警告：在{lang_code}中发现未知的key: {key}")

    # 创建输出目录
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存为Excel文件
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)
    print(f"已生成Excel文件: {output_path}")

def main(project_path: str, output_path: str) -> None:
    """
    主函数
    Args:
        project_path: Flutter项目根目录路径
        output_path: 输出Excel文件路径
    """
    try:
        arb_files = find_arb_files(project_path)
        process_arb_files_to_excel(arb_files, output_path)
        print(f"所有Excel文件已生成完毕，保存在: {output_path}")
    except Exception as e:
        print(f"处理失败: {str(e)}")

if __name__ == "__main__":
    project_path = "D:\\Codes\\xjsd\\myvu_flutter"
    output_path = ".\\excels\\flutter.xlsx"
    main(project_path, output_path)
