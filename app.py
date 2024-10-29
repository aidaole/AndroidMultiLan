from flask import Flask, render_template, request, send_file
import os
from export_excel import main as android_excel_main
from export_xml import main as android_xml_main
from export_excel_flutter import main as flutter_excel_main
from export_arb_flutter import main as flutter_arb_main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/export_excel', methods=['POST'])
def export_excel():
    project_path = request.form['project_path']
    output_dir = request.form['output_dir']
    flavor = request.form.get('flavor', '').strip() or None
    
    if not os.path.exists(project_path):
        return '项目路径不存在', 400
        
    try:
        # 直接调用新的main函数，不需要手动扫描模块
        android_excel_main(project_path, output_dir, flavor)
        return f'导出成功！文件保存在: {output_dir}'
    except Exception as e:
        print(f"导出失败: {str(e)}")
        return f'导出失败：{str(e)}', 500

@app.route('/export_xml', methods=['POST'])
def export_xml():
    project_path = request.form['project_path']
    excel_dir = request.form['excel_dir']
    
    if not os.path.exists(project_path):
        return '项目路径不存在', 400
        
    try:
        # 执行XML导入
        android_xml_main(project_path, excel_dir)
        return '导入成功！XML文件已生成'
    except Exception as e:
        print(f"导入失败: {str(e)}")
        return f'导入失败：{str(e)}', 500

@app.route('/export_excel_flutter', methods=['POST'])
def export_excel_flutter():
    project_path = request.form['project_path']
    output_path = request.form['output_path']
    
    if not os.path.exists(project_path):
        return '项目路径不存在', 400
        
    try:
        # 执行Flutter Excel导出
        flutter_excel_main(project_path, output_path)
        return f'导出成功！文件保存在: {output_path}'
    except Exception as e:
        print(f"导出失败: {str(e)}")
        return f'导出失败：{str(e)}', 500

@app.route('/export_arb', methods=['POST'])
def export_arb():
    project_path = request.form['project_path']
    excel_path = request.form['excel_path']
    
    if not os.path.exists(project_path):
        return '项目路径不存在', 400
        
    try:
        # 执行ARB导入
        flutter_arb_main(project_path, excel_path)
        return '导入成功！ARB文件已生成'
    except Exception as e:
        print(f"导入失败: {str(e)}")
        return f'导入失败：{str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
