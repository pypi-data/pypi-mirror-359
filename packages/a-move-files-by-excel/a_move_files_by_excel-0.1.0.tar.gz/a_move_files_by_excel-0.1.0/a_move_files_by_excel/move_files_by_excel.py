#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简批量移动文件脚本（保留原始路径结构）
- 将本脚本和Excel放在同一文件夹，双击或运行即可。
- 自动读取Excel中"文件名"列（全路径），在to_move_files下还原完整路径结构并移动文件。
- 无需任何参数，适合所有用户。
"""
import os
import sys
import shutil
import glob
import traceback
import re

# 检查pandas依赖
try:
    import pandas as pd
except ImportError:
    print("未检测到pandas库，正在尝试自动安装...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
        import pandas as pd
        print("pandas安装成功！")
    except Exception as e:
        print("自动安装pandas失败，请手动安装后重试。错误：", e)
        sys.exit(1)

# 获取当前脚本所在目录
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 自动查找Excel文件
excel_files = glob.glob(os.path.join(BASE_DIR, '*.xlsx'))
print(f"[调试] 当前目录：{BASE_DIR}")
print(f"[调试] 检测到的Excel文件列表：{[os.path.basename(f) for f in excel_files]}")
if not excel_files:
    print("当前目录下未找到Excel文件，请将Excel和脚本放在同一目录！")
    sys.exit(1)
if len(excel_files) == 1:
    excel_path = excel_files[0]
else:
    print("检测到多个Excel文件，请选择要处理的文件：")
    for idx, f in enumerate(excel_files):
        print(f"[{idx+1}] {os.path.basename(f)}")
    while True:
        try:
            choice = int(input("请输入序号："))
            if 1 <= choice <= len(excel_files):
                excel_path = excel_files[choice-1]
                break
        except Exception:
            pass
        print("输入有误，请重新输入！")

print(f"正在处理Excel文件：{os.path.basename(excel_path)}")

# 自动创建目标文件夹
target_dir = os.path.join(BASE_DIR, 'to_move_files')
os.makedirs(target_dir, exist_ok=True)

# 日志文件
total, moved, failed = 0, 0, 0
log_path = os.path.join(BASE_DIR, 'move_files_log.txt')
with open(log_path, 'w', encoding='utf-8') as log:
    try:
        df = pd.read_excel(excel_path)
        if '文件名' not in df.columns:
            print('Excel中未找到"文件名"列，请检查文件格式！')
            log.write('Excel中未找到"文件名"列，请检查文件格式！\n')
            sys.exit(1)
        for idx, row in df.iterrows():
            file_path = str(row['文件名']).strip()
            total += 1
            # 实时进度条和当前文件名
            percent = (total / len(df)) * 100
            bar_len = 30
            filled_len = int(bar_len * total // len(df))
            bar = '█' * filled_len + '-' * (bar_len - filled_len)
            print(f"\r[{bar}] {percent:5.1f}%  正在处理({total}/{len(df)}): {file_path[:60]}", end='', flush=True)
            if not file_path or not os.path.isabs(file_path):
                log.write(f"[跳过] 第{idx+2}行，文件路径无效：{file_path}\n")
                failed += 1
                continue
            if not os.path.exists(file_path):
                log.write(f"[未找到] 第{idx+2}行，文件不存在：{file_path}\n")
                failed += 1
                continue
            try:
                # 构造to_move_files下的完整路径结构（盘符作为一级目录，去掉冒号）
                drive, rest = os.path.splitdrive(file_path)
                drive = drive.replace(':', '')  # D: -> D
                rel_path = os.path.join(drive, rest.lstrip('\\/'))
                dest_path = os.path.join(target_dir, rel_path)
                dest_folder = os.path.dirname(dest_path)
                os.makedirs(dest_folder, exist_ok=True)
                shutil.move(file_path, dest_path)
                log.write(f"[成功] 第{idx+2}行，已移动：{file_path} -> {dest_path}\n")
                moved += 1
            except Exception as e:
                log.write(f"[失败] 第{idx+2}行，移动失败：{file_path}，错误：{e}\n")
                failed += 1
        print()  # 换行
        print(f"处理完成！共{total}个文件，成功移动{moved}个，失败/未找到{failed}个。详细见move_files_log.txt。")
        log.write(f"\n处理完成！共{total}个文件，成功移动{moved}个，失败/未找到{failed}个。\n")

        # === 全类型核查与报告输出优化 ===
        # 1. 报告始终输出到py/exe同目录，避免PyInstaller临时目录问题
        # 2. 支持对所有日志类型（成功、未找到、跳过、失败）自动核查
        # 3. 报告首行加UTF-8说明，内容全中文、无乱码
        # 4. 每条输出包含文件名、目录、核查结论，表达友好专业
        # 5. 保证日志与报告条数、顺序100%一致，异常行也输出，绝不遗漏
        # 6. 权限失败高亮，结尾统计自查
        if getattr(sys, 'frozen', False):
            report_base_dir = os.path.dirname(sys.executable)
        else:
            report_base_dir = os.path.abspath(os.path.dirname(__file__))
        output_path = os.path.join(report_base_dir, 'move_files_check_report.txt')
        # 日志类型正则
        pattern_success = re.compile(r"\[成功\] 第(\d+)行，已移动：(.*?) -> (.*)")
        pattern_not_found = re.compile(r"\[未找到\] 第(\d+)行，文件不存在：(.*)")
        pattern_skip = re.compile(r"\[跳过\] 第(\d+)行，文件路径无效：(.*)")
        pattern_fail = re.compile(r"\[失败\] 第(\d+)行，移动失败：(.*)，错误：(.*)")
        results = []
        abnormal_count = 0  # 统计未能自动核查的条数
        perm_fail_count = 0 # 统计权限失败条数
        if not os.path.exists(log_path):
            print(f"未找到日志文件: {log_path}")
        else:
            with open(log_path, 'r', encoding='utf-8') as logf:
                lines = logf.readlines()
            # 保证每一行日志都输出一行报告，顺序一致
            for i, line in enumerate(lines):
                raw_line = line.rstrip('\n')
                line = line.strip()
                # 空行也要输出
                if not line:
                    results.append('[空行]')
                    continue
                # 统计行（如"处理完成！"等）
                if line.startswith('处理完成') or line.startswith('Excel中未找到'):
                    results.append(f'[统计] {raw_line}')
                    continue
                # 成功移动核查
                m = pattern_success.match(line)
                if m:
                    idx, src, dst = m.group(1), m.group(2).strip(), m.group(3).strip()
                    file_name = os.path.basename(dst)
                    dir_path = os.path.dirname(dst)
                    if os.path.exists(dst):
                        results.append(f"[确认] 第{idx}行，文件 {file_name} 已成功移动到 {dir_path}，目标文件存在。")
                    else:
                        results.append(f"[警告] 第{idx}行，文件 {file_name} 标记为已移动，但目标目录 {dir_path} 下未找到该文件！")
                    continue
                # 未找到核查
                m = pattern_not_found.match(line)
                if m:
                    idx, file_path = m.group(1), m.group(2).strip()
                    file_name = os.path.basename(file_path)
                    dir_path = os.path.dirname(file_path)
                    if os.path.exists(file_path):
                        results.append(f"[警告] 第{idx}行，文件 {file_name} 在目录 {dir_path} 下实际还存在，建议复查！")
                    else:
                        results.append(f"[确认] 第{idx}行，文件 {file_name} 在目录 {dir_path} 下经过实际核查，确实已经不存在。")
                    continue
                # 跳过核查
                m = pattern_skip.match(line)
                if m:
                    idx, file_path = m.group(1), m.group(2).strip()
                    file_name = os.path.basename(file_path)
                    dir_path = os.path.dirname(file_path)
                    results.append(f"[跳过] 第{idx}行，文件 {file_name} 路径无效（{file_path}），未做移动操作。")
                    continue
                # 失败核查
                m = pattern_fail.match(line)
                if m:
                    idx, file_path, err = m.group(1), m.group(2).strip(), m.group(3).strip()
                    file_name = os.path.basename(file_path)
                    dir_path = os.path.dirname(file_path)
                    # 检查是否为权限失败
                    if ('拒绝访问' in err) or ('Permission denied' in err):
                        perm_fail_count += 1
                        results.append(f"[权限失败] 第{idx}行，文件 {file_name} 移动失败，原路径 {dir_path} 下文件仍存在，错误信息：{err}。原因：权限不足，建议用管理员权限运行。")
                    else:
                        if os.path.exists(file_path):
                            results.append(f"[失败] 第{idx}行，文件 {file_name} 移动失败，原路径 {dir_path} 下文件仍存在，错误信息：{err}")
                        else:
                            results.append(f"[失败] 第{idx}行，文件 {file_name} 移动失败，且原路径 {dir_path} 下文件已不存在，错误信息：{err}")
                    continue
                # === 未能正则匹配的日志，输出异常提示，便于人工复查 ===
                abnormal_count += 1
                results.append(f"[异常] 原始日志：{raw_line}，未能自动核查，请人工复查！")
            # 写入报告，首行加UTF-8说明
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write('# 本文件为UTF-8编码，建议用支持UTF-8的编辑器（如Notepad++、VSCode）打开\n')
                for r in results:
                    out.write(r + '\n')
                # 报告结尾输出统计信息
                out.write(f'\n# 本报告与日志一一对应，日志{len(lines)}条，报告{len(results)}条。\n')
                out.write(f'# 其中未能自动核查{abnormal_count}条，权限失败{perm_fail_count}条。\n')
                if len(lines) != len(results):
                    out.write(f'# [警告] 日志与报告条数不一致，请检查实现逻辑！\n')
            # 终端输出闭环自查结果
            print(f"核查完成，结果已保存到: {output_path}\n共核查{len(results)}条记录，其中{abnormal_count}条未能自动核查，权限失败{perm_fail_count}条。\n")
            if len(lines) != len(results):
                print(f"[警告] 日志与报告条数不一致！日志{len(lines)}条，报告{len(results)}条，请检查实现逻辑！")
    except Exception as e:
        print("处理过程中发生错误：", e)
        log.write(f"处理过程中发生错误：{e}\n{traceback.format_exc()}\n") 