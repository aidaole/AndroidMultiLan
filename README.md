# AndroidMultiLan

android中我们适配多语言是在 `values-xxx` 目录中创建对应语言的 `string.xml`

大公司有自己成熟的多语言适配工具，但是对于小公司可能没有资源来建立一套完整的多语言系统。

下文中提供了一个简洁的多语言适配工具，其功能包括:

1. 将我们项目中的 `string.xml` 整合到一个 `excel` 表格中（此时可以拿表格去给翻译公司翻译）
2. 将 `excel` 文件导出对应国家语言的 `string.xml`

工具的优势:

1. 要适配一个完整国家语言时, 可以非常快捷的知道哪些 `key` 需要翻译, 一键导出列表
2. 翻译完成之后, 不需要手动一个一个根据 `key` 替换到对应的 `string.xml` 中, 避免出错

## 

项目地址: [https://github.com/aidaole/AndroidMultiLan](https://github.com/aidaole/AndroidMultiLan)

## 使用说明

### 脚本功能主要分为2个部分:

1. `strings.xml` 导出excel: **export_excel.py**
2. excel 导出对应国家语言列表 `strings.xml`: **import_strings.py**

### 需要提前安装一些python的package：

```
pip install pandas
pip install openpyxl
```

### 使用命令

```shell
python export_excel.py excel地址.xlsx 语言名称 xml地址 语言名称 xml地址 ...
```

会将多种语言合并生成到同一个excel文件中


![](https://aidaole.github.io/other/images/multi_language/2024-04-06-11-08-16.png ':size=300')

```shell
python ./import_strings.py excel地址.xlsx 生成语言存放目录
```

将excel中每一个作为一种语言生成一个xml文件，方便直接导入到项目中

![](https://aidaole.github.io/other/images/multi_language/2024-04-06-11-11-38.png ':size=200')

生成的内容

default.xml
```xml
<resources>
    <string name="app_name">EasyPermission</string>
    <string name="navi_permission">navigation permission</string>
    <string name="call_permission">call permission</string>
    <string name="no_tras_sample" translatable="false">not need to translate text</string>
    <string name="more_text">default more sample</string>
</resources>
```

zh.xml
```xml
<resources>
    <string name="app_name">EasyPermission</string>
    <string name="navi_permission">导航权限</string>
    <string name="call_permission">通话权限</string>
</resources>
```