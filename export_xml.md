需求:
    我有一个多语言翻译的excel文件, 在当前目录下的 output.xlsx 文件.
    这个表格中有一个sheet, 然后可能有很多列. 每一列的第一行是标题. 
    第一列标题是: key
    第二列标题是: default, 里面的内容是中文
    然后从第三列开始可能是: 英文, 法语, 德语, 意大利语等等
    我需要将从第二列开始, 每一列的内容生成一个单独的文件. 文件名为: 列标题.xml
    xml的内容是按照 android的string.xml的格式. 每一行是: <string name="key">value</string>, 其中name是key列对应行的值, value是当前列对应行的值. 如果value的内容是`nan`, 则不生成该行
    如果key列的内容中包含`#notranslation#`表示不需要翻译, 只需要生成第二列的内容, 并且添加 `translatable="false"` 属性
    如果翻译的列中内容为空, 则不生成该行
    你作为一名非常优秀的工程师, 帮我使用python代码实现这个需求.


