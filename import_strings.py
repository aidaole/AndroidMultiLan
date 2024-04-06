# -*- coding: utf-8 -*-

import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import os

excel_file = ""
xml_folder = ""
arguments = sys.argv
notranslation_flag = "#notranslation#"


# 主程序入口
def main():
    print("导入语言, 生成strings.xml脚本开始")
    global excel_file
    global xml_folder
    if not check_arguments():
        print("输入错误")
        print(f"> python import_strings.py excel文件地址 xml生成文件夹地址")
        return False

    print(f"导入excel路径：{excel_file}")
    excel_map = get_exel_map(excel_file)
    default_keys = excel_map['key']
    excel_map.pop('key')
    print(f"使用excel中 Key列包含的key，一共{len(default_keys)} 条")

    for name, content in excel_map.items():
        xml_file_name = f"./{xml_folder}/strings-{name}/strings.xml"
        xml_map = dict(zip(default_keys, content))
        write_map_to_xml(xml_map, xml_file_name)


def get_xml_map(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    xml_data = {}

    for string_elem in root.findall('.//string'):
        name = string_elem.get('name')
        value = string_elem.text.strip()  # 获取文本内容，并去除首尾的空白字符
        xml_data[name] = value

    return xml_data


# 读取excel内容到dict中
def get_exel_map(excel_path):
    try:
        df = pd.read_excel(excel_path)
        print(f"一共{df.shape[0]}行, {df.shape[1]}列")
        all_data = {}
        for col in df.columns:
            all_data[col] = df[col].tolist()
        return all_data
    except Exception as e:
        print("读取 Excel 文件时出错:", e)
        return {}


def write_map_to_xml(xml_map, xml_path):
    global notranslation_flag
    root = ET.Element("resources")
    for key, value in xml_map.items():
        if isinstance(value, float) or isinstance(key, float):
            # 空数据
            print(f"空数据：{key}: {value}")
            pass
        else:
            translatable = notranslation_flag not in key
            if translatable:
                string_elem = ET.SubElement(root, "string", attrib={"name": key})
            else:
                key = key.replace(notranslation_flag, "")
                string_elem = ET.SubElement(root, "string", attrib={"name": key, "translatable": "false"})
            string_elem.text = value

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")

    dir_name = os.path.dirname(xml_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(xml_path, "w", encoding='utf-8') as xml_file:
        real_txt = xml_str.replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('&#160;', ' ')
        xml_file.write(real_txt)
    print(f"生成 {xml_path} 成功")


# 检查参数
def check_arguments():
    global excel_file
    global xml_folder
    if len(arguments) != 3:
        return False
    excel_file = arguments[1]
    if (len(excel_file) == 0):
        print("参数错误")
        return False
    xml_folder = arguments[2]
    return True


if __name__ == "__main__":
    main()
