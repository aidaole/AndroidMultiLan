# -*- coding: utf-8 -*-

import pandas as pd
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

export_file_path = "output.xlsx"
lan_map = {}
notranslation_flag = "#notranslation#"
arguments = sys.argv


# 主程序入口
def main():
    global export_file_path
    print("从xml导出excel")

    if not check_arguments():
        print("参数错误,格式如下，按任意键退出：")
        print("> python export_excel.py excel保存地址 xml语言文件地址 语言名称 xml语言文件地址 语言名称 ...")
        return

    print(f"\n总共需要生成{len(lan_map)}个语言列表: ")
    for name, path in lan_map.items():
        print(f"{name} -> {path}")

    default_key = "default"
    default_path = lan_map[default_key]
    lan_map.pop(default_key)
    default_xml_map = get_xml_map(default_path)
    default_data = {}
    default_data["key"] = default_xml_map.keys()
    default_data["default"] = default_xml_map.values()

    for name, path in lan_map.items():
        arr = []
        content = get_xml_map(path)
        for key in default_data["key"]:
            if key in content.keys():
                arr.append(content[key])
            else:
                arr.append("")
        default_data[f"{name}"] = arr

    input_path = export_file_path
    if len(input_path) > 0:
        export_file_path = input_path

    df = pd.DataFrame(default_data)
    df.to_excel(export_file_path, index=False)
    print(f"生成成功，请查看文件: {export_file_path}")


def get_xml_map(xml_path):
    global notranslation_flag
    tree = ET.parse(xml_path)
    root = tree.getroot()
    xml_data = {}

    for string_elem in root.findall('.//string'):
        name = string_elem.get('name')
        value = ""
        translatable = string_elem.get("translatable")
        if string_elem.text is not None:
            value = string_elem.text
        else:
            value = ""
        if translatable is not None and translatable == "false":
            print(f"{string_elem.text} -> 不需要翻译")
            name = name + notranslation_flag
        xml_data[name] = value

    return xml_data


# 检查输入参数
def check_arguments():
    global export_file_path
    if len(arguments) <= 1:
        return False
    export_file_path = arguments[1]

    i = 2
    try:
        while i < len(arguments):
            lan_map[f"{arguments[i]}"] = f"{arguments[i + 1]}"
            i += 2
    except IndexError:
        return False

    if len(lan_map) == 0:
        return False
    return True


if __name__ == "__main__":
    main()
