import os
import json
import pandas as pd
from typing import Dict, List
from collections import OrderedDict

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

def read_original_arb(file_path: str) -> OrderedDict:
    """
    读取原始ARB文件，保留顺序
    Args:
        file_path: ARB文件路径
    Returns:
        OrderedDict: 保持原有顺序的ARB内容
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # 使用object_pairs_hook=OrderedDict来保持顺序
                return json.load(file, object_pairs_hook=OrderedDict)
        except Exception as e:
            print(f"警告：无法解析原始ARB文件 {file_path}: {str(e)}")
    
    return OrderedDict()

def generate_arb(data: Dict[str, str], original_arb: OrderedDict, output_path: str, lang_code: str) -> None:
    """
    生成ARB文件，保留原有文件的结构和顺序
    Args:
        data: 包含key-value对的字典
        original_arb: 原始ARB文件的内容
        output_path: 输出文件路径
        lang_code: 语言代码
    """
    # 创建新的有序字典
    new_arb = OrderedDict()
    
    # 添加@@locale
    new_arb['@@locale'] = lang_code
    
    # 如果有原始文件，按原始文件的顺序更新内容
    if original_arb:
        for key in original_arb.keys():
            if key == '@@locale':
                continue
            if key in data and str(data[key]) != 'nan' and str(data[key]).strip():
                new_arb[key] = str(data[key])
            elif key in original_arb:
                new_arb[key] = original_arb[key]
    
    # 添加原始文件中没有的新翻译内容
    for key, value in data.items():
        if key not in new_arb and str(value) != 'nan' and str(value).strip():
            new_arb[key] = str(value)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存文件，使用4个空格缩进，不添加末尾换行
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_arb, f, ensure_ascii=False, indent=2)
    print(f"已生成ARB文件: {output_path}")

def process_translations(df: pd.DataFrame, project_path: str) -> None:
    """
    处理翻译数据并生成ARB文件
    Args:
        df: 包含翻译的DataFrame
        project_path: Flutter项目根目录路径
    """
    l10n_path = os.path.join(project_path, 'lib', 'l10n')
    
    # 确保l10n目录存在
    os.makedirs(l10n_path, exist_ok=True)
    
    # 获取所有列名
    columns = df.columns.tolist()
    
    # 从第二列开始处理（跳过'key'列）
    for col in columns[1:]:
        # 处理default列的特殊情况
        if col == 'default':
            lang_code = 'zh_CN'
            file_name = 'intl_zh_CN.arb'
        else:
            # 直接使用列名作为语言代码和文件名
            lang_code = col
            file_name = f'intl_{col}.arb'
        
        # 创建key-value字典
        translations = {
            str(row['key']): str(row[col])
            for _, row in df.iterrows()
            if pd.notna(row[col]) and str(row[col]).strip()
        }
        
        # 读取原始ARB文件
        original_arb_path = os.path.join(l10n_path, file_name)
        original_arb = read_original_arb(original_arb_path)
        
        # 生成新的ARB文件
        generate_arb(translations, original_arb, original_arb_path, lang_code)

def main(project_path: str, excel_path: str) -> None:
    """
    主函数
    Args:
        project_path: Flutter目根目录路径
        excel_path: Excel文件路径
    """
    try:
        # 读取Excel文件
        df = read_excel(excel_path)
        
        # 处理翻译并生成ARB文件
        process_translations(df, project_path)
        
        print("所有ARB文件已生成完毕")
    except Exception as e:
        print(f"处理失败: {str(e)}")

if __name__ == "__main__":
    project_path = "D:\\Codes\\xjsd\\myvu_flutter"
    excel_path = ".\\excels\\flutter.xlsx"
    main(project_path, excel_path)
