import os
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from typing import Dict, List, Tuple
from export_excel import parse_settings_gradle

def read_excel(file_path: str) -> pd.DataFrame:
    """
    读取Excel文件
    Args:
        file_path: Excel文件路径
    Returns:
        DataFrame: 包含翻译内容的数据框
    """
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        raise Exception(f"读取Excel文件失败: {str(e)}")

def unescape_html(text: str) -> str:
    """
    还原HTML转义字符
    Args:
        text: 包含转义字符的文本
    Returns:
        str: 还原后的文本
    """
    replacements = {
        '&quot;': '"',
        '&gt;': '>',
        '&lt;': '<',
        '&amp;': '&',
        '&apos;': "'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def create_string_element(root: ET.Element, key: str, value: str, translatable: bool = True) -> None:
    """
    创建XML字符串元素
    Args:
        root: XML根元素
        key: 字符串标识符
        value: 字符串值
        translatable: 是否可翻译
    """
    string = ET.SubElement(root, "string")
    string.set("name", key.replace('#notranslation#', '').strip())
    
    # 直接设置文本，不进行转义
    string.text = str(value)
    
    if not translatable:
        string.set("translatable", "false")

def read_original_xml(file_path: str) -> Tuple[ET.Element, Dict[str, ET.Element]]:
    """
    读取原始XML文件
    Args:
        file_path: XML文件路径
    Returns:
        Tuple[ET.Element, Dict[str, ET.Element]]: XML根元素和字符串元素字典
    """
    if os.path.exists(file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            # 创建key到element的映射
            string_map = {
                elem.get('name'): elem
                for elem in root.findall('string')
            }
            return root, string_map
        except ET.ParseError:
            print(f"警告：无法解析原始XML文件 {file_path}")
    
    # 如果文件不存在或解析失败，返回新的根元素
    return ET.Element("resources"), {}

def generate_xml(data: Dict[str, str], output_path: str) -> None:
    """
    生成XML文件，保留原有文件的结构和顺序
    Args:
        data: 包含key-value对的字典
        output_path: 输出文件路径
    """
    # 读取原始XML文件
    root, original_strings = read_original_xml(output_path)
    
    # 更新现有的字符串
    for elem in root.findall('string'):
        key = elem.get('name')
        if key in data:
            new_value = str(data[key])
            if new_value != 'nan' and new_value.strip():
                elem.text = new_value
            del data[key]  # 从待处理数据中移除已处理的项
    
    # 添加新的字符串
    for key, value in data.items():
        if value != 'nan' and str(value).strip():
            if '#notranslation#' in key:
                if 'default' in output_path:
                    create_string_element(root, key, str(value), False)
            else:
                create_string_element(root, key, str(value))

    # 自定义XML格式化输出
    def format_xml(elem, level=0):
        indent = "    " * level
        result = []
        result.append(f'{indent}<resources>\n')
        
        for string in elem:
            attrs = ' '.join([f'{k}="{v}"' for k, v in string.attrib.items()])
            result.append(f'{indent}    <string {attrs}>{string.text}</string>\n')
            
        result.append(f'{indent}</resources>\n')
        return ''.join(result)

    # 保存文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(format_xml(root))

def process_translations(df: pd.DataFrame, output_dir: str) -> None:
    """
    处理翻译数据并生成XML文件
    Args:
        df: 包含翻译的DataFrame
        output_dir: 输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有列名
    columns = df.columns.tolist()
    
    # 从第二列开始处理
    for col in columns[1:]:
        # 创建key-value字典
        translations = {
            str(row['key']): str(row[col])
            for _, row in df.iterrows()
        }
        
        # 生成XML文件
        output_path = os.path.join(output_dir, f"{col}.xml")
        generate_xml(translations, output_path)
        print(f"已生成文件: {output_path}")

def determine_output_path(module_path: str, lang_code: str, is_intl: bool = False) -> str:
    """
    确定XML文件的输出路径
    Args:
        module_path: 模块路径
        lang_code: 语言代码
        is_intl: 是否为res_intl目录下的文件
    Returns:
        str: 输出路径
    """
    # 确定基础目录
    if is_intl:
        # res_intl 放到 intl 目录下
        base_path = os.path.join(module_path, 'src', 'intl', 'res_intl')
    else:
        # 检查main和intl目录
        main_res = os.path.join(module_path, 'src', 'main', 'res')
        intl_res = os.path.join(module_path, 'src', 'intl', 'res')
        
        # 检查对应语言的strings.xml是否存在
        main_lang_path = os.path.join(main_res, 'values' if lang_code == 'default' else f'values-{lang_code}', 'strings.xml')
        intl_lang_path = os.path.join(intl_res, 'values' if lang_code == 'default' else f'values-{lang_code}', 'strings.xml')
        
        # 优先使用已存在的目录，如果都不存在则使用main
        if os.path.exists(intl_lang_path):
            base_path = intl_res
        else:
            base_path = main_res

    # 确定values目录名
    values_dir = 'values' if lang_code == 'default' else f'values-{lang_code}'
    
    return os.path.join(base_path, values_dir, 'strings.xml')

def main(project_path: str, excel_dir: str):
    """
    主函数
    Args:
        project_path: Android项目根目录路径
        excel_dir: 包含Excel文件的目录路径
    """
    try:
        # 自动识别所有模块
        modules = parse_settings_gradle(project_path)
        if not modules:
            print("未找到任何模块，请检查settings.gradle文件")
            return
            
        print(f"找到以下模块: {modules}")
        
        # 创建模块名到路径的映射
        module_path_map = {}
        for module in modules:
            # 获取最后一级目录名作为模块名
            module_name = os.path.basename(module)
            module_path_map[module_name] = module
        
        # 遍历Excel目录下的所有xlsx文件
        for excel_file in os.listdir(excel_dir):
            if not excel_file.endswith('.xlsx'):
                continue
                
            # 获取模块名和类型（普通/intl）
            module_name = os.path.splitext(excel_file)[0]
            is_intl = module_name.endswith('-intl')
            if is_intl:
                module_name = module_name[:-5]  # 移除'-intl'后缀
            
            # 检查该模块是否在项目中存在
            if module_name not in module_path_map:
                print(f"警告：Excel文件 {excel_file} 对应的模块在项目中不存在，跳过处理")
                continue
                
            excel_path = os.path.join(excel_dir, excel_file)
            # 使用完整的模块路径
            module_path = os.path.join(project_path, module_path_map[module_name])
            
            # 读取Excel文件
            df = read_excel(excel_path)
            
            # 处理每种语言的翻译
            for lang_code in df.columns[1:]:  # 跳过'key'列
                # 创建translations字典
                translations = {
                    row['key'].replace('#notranslation#', ''): str(row[lang_code])
                    for _, row in df.iterrows()
                    if pd.notna(row[lang_code]) and str(row[lang_code]).strip()
                }
                
                if translations:  # 只在有翻译内容时生成文件
                    # 确定输出路径
                    output_path = determine_output_path(module_path, lang_code, is_intl)
                    
                    # 确保输出目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # 生成XML文件
                    generate_xml(translations, output_path)
                    print(f"已生成文件: {output_path}")
                
        print("所有XML文件已生成完毕")
    except Exception as e:
        print(f"处理失败: {str(e)}")

if __name__ == "__main__":
    # 示例用法
    project_path = "D:\\Codes\\demos\\MultiLanAndroidTest"
    excel_dir = ".\\output"
    main(project_path, excel_dir)
