import os
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Dict, List, Tuple

def parse_xml_file(xml_path: str) -> List[Tuple[str, str, bool]]:
    """
    解析单个XML文件
    Args:
        xml_path: XML文件路径
    Returns:
        List[Tuple[str, str, bool]]: 包含(key, value, is_translatable)的列表
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        result = []
        
        for string in root.findall('string'):
            key = string.get('name', '')
            value = string.text or ''
            translatable = string.get('translatable', 'true').lower() != 'false'
            result.append((key, value, translatable))
            
        return result
    except Exception as e:
        print(f"解析XML文件失败 {xml_path}: {str(e)}")
        return []

def get_language_code_from_path(path: str) -> str:
    """
    从values目录名称中提取语言代码
    Args:
        path: 资源目录路径
    Returns:
        str: 语言代码
    """
    dir_name = os.path.basename(os.path.dirname(path))
    if dir_name == 'values':
        return 'default'
    return dir_name.replace('values-', '')

def find_strings_xml_files(module_path: str, flavor: str = None, include_res_intl: bool = False) -> Dict[str, str]:
    """
    在模块中查找所有strings.xml文件
    Args:
        module_path: 模块根目录路径
        flavor: 可选的flavor名称
        include_res_intl: 是否包含res_intl目录下的文件
    Returns:
        Dict[str, str]: 语言代码到文件路径的映射
    """
    xml_files = {}
    
    # 定义需要搜索的目录列表
    if include_res_intl:
        # 搜索res_intl目录（与res同级）
        search_paths = [
            os.path.join(module_path, 'src', 'main', 'res_intl'),
        ]
        if flavor:
            search_paths.append(os.path.join(module_path, 'src', flavor, 'res_intl'))
    else:
        # 搜索普通res目录
        search_paths = [
            os.path.join(module_path, 'src', 'main', 'res'),
        ]
        if flavor:
            search_paths.append(os.path.join(module_path, 'src', flavor, 'res'))
    
    for res_path in search_paths:
        if not os.path.exists(res_path):
            print(f"资源目录不存在: {res_path}")
            continue

        for root, dirs, files in os.walk(res_path):
            if 'strings.xml' in files:
                dir_name = os.path.basename(root)
                if dir_name.startswith('values'):
                    if dir_name == 'values':
                        lang_code = 'default'
                    else:
                        lang_code = dir_name.replace('values-', '')
                    xml_files[lang_code] = os.path.join(root, 'strings.xml')
    
    return xml_files

def process_module(module_path: str, output_dir: str, flavor: str = None) -> None:
    """
    处理单个模块的strings.xml文件
    Args:
        module_path: 模块根目录路径
        output_dir: 输出目录路径
        flavor: 可选的flavor名称
    """
    try:
        module_name = os.path.basename(module_path)
        
        # 处理主要的strings.xml文件
        xml_files = find_strings_xml_files(module_path, flavor, include_res_intl=False)
        if xml_files:
            process_strings_to_excel(xml_files, module_name, output_dir)
        else:
            print(f"模块 {module_name} 中未找到主要的strings.xml文件")

        # 处理res_intl目录下的strings.xml文件
        res_intl_files = find_strings_xml_files(module_path, flavor, include_res_intl=True)
        if res_intl_files:
            process_strings_to_excel(res_intl_files, f"{module_name}-intl", output_dir)
        
    except Exception as e:
        print(f"处理模块 {module_path} 失败: {str(e)}")

def process_strings_to_excel(xml_files: Dict[str, str], output_name: str, output_dir: str) -> None:
    """
    将strings.xml文件处理并导出为Excel
    Args:
        xml_files: 语言代码到文件路径的映射
        output_name: 输出文件名（不含扩展名）
        output_dir: 输出目录路径
    """
    if 'default' not in xml_files:
        raise Exception(f"{output_name} 中未找到默认语言的strings.xml文件")

    # 处理默认语言文件
    data = {'key': [], 'default': []}
    default_strings = parse_xml_file(xml_files['default'])
    
    for key, value, translatable in default_strings:
        data['key'].append(f"#notranslation#{key}" if not translatable else key)
        data['default'].append(value)

    # 处理其他语言文件
    for lang_code, xml_path in xml_files.items():
        if lang_code == 'default':
            continue

        data[lang_code] = [''] * len(data['key'])
        strings = parse_xml_file(xml_path)
        
        for key, value, _ in strings:
            try:
                index = data['key'].index(key)
            except ValueError:
                try:
                    index = data['key'].index(f"#notranslation#{key}")
                except ValueError:
                    print(f"警告：在{lang_code}中发现未知的key: {key}")
                    continue
            
            data[lang_code][index] = value

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为Excel文件
    df = pd.DataFrame(data)
    output_path = os.path.join(output_dir, f"{output_name}.xlsx")
    df.to_excel(output_path, index=False)
    print(f"已生成Excel文件: {output_path}")

def parse_settings_gradle(project_path: str) -> List[str]:
    """
    解析settings.gradle文件以获取所有模块路径
    Args:
        project_path: Android项目根目录路径
    Returns:
        List[str]: 模块路径列表
    """
    settings_file = os.path.join(project_path, 'settings.gradle')
    if not os.path.exists(settings_file):
        settings_file = os.path.join(project_path, 'settings.gradle.kts')
        if not os.path.exists(settings_file):
            raise Exception("未找到settings.gradle或settings.gradle.kts文件")

    modules = []
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 匹配include语句，支持单引号和双引号的写法
        import re
        # 匹配 include ':app', ':module1', ':module2' 这样的写法
        includes = re.findall(r"include\s+['\"]([^'\"]+)['\"]", content)
        # 匹配 include(":app", ":module1", ":module2") 这样的写法
        includes.extend(re.findall(r'include\([\'"]([^\'"]+)[\'"]\)', content))
        
        for module in includes:
            # 将 :app 或 :modules:xxx 转换为实际路径
            module_path = module.replace(':', os.sep).strip()
            if module_path.startswith(os.sep):
                module_path = module_path[1:]
            modules.append(module_path)
            
    except Exception as e:
        print(f"解析settings.gradle文件失败: {str(e)}")
        return []
        
    return modules

def main(project_path: str, output_dir: str = "output", flavor: str = None) -> None:
    """
    主函数
    Args:
        project_path: Android项目根目录路径
        output_dir: 输出目录路径
        flavor: 可选的flavor名称
    """
    try:
        # 自动识别所有模块
        modules = parse_settings_gradle(project_path)
        if not modules:
            print("未找到任何模块，请检查settings.gradle文件")
            return
            
        print(f"找到以下模块: {modules}")
        
        for module in modules:
            module_path = os.path.join(project_path, module)
            if not os.path.isdir(module_path):
                print(f"警告：模块目录不存在: {module_path}")
                continue
            process_module(module_path, output_dir, flavor)

        print(f"所有Excel文件已生成完毕，保存在目录: {output_dir}")
    except Exception as e:
        print(f"处理失败: {str(e)}")

if __name__ == "__main__":
    project_path = "D:\\Codes\\demos\\MultiLanAndroidTest"
    output_directory = ".\\output"
    flavor_name = "intl"  # 指定flavor名称
    main(project_path, output_directory, flavor_name)
