#python3 -m pip install semgrep

import re
import json
import subprocess
import tempfile
import os
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataflow.utils.utils import get_logger
from dataflow.utils.registry import GENERATOR_REGISTRY
from dataflow.data import MyScaleStorage

ext_map = {
    "groovy": ".groovy",
    "objective-c": ".m",
    "css": ".css",
    "go": ".go",
    "c": ".c",
    "swift": ".swift",
    "javascript": ".js",
    "kotlin": ".kt",
    "typescript": ".ts",
    "r": ".r",
    "sql": ".sql",
    "c_sharp": ".cs",
    "php": ".php",
    "scala": ".scala",
    "markdown": ".md",
    "cpp": ".cpp",
    "python": ".py",
    "yaml": ".yaml",    
    "tex": ".tex",
    "java": ".java",
    "matlab": ".m",
    "html": ".html",
    "ini": ".ini",
    "dockerfile": ".dockerfile",  
    "assembly": ".asm",
    "julia": ".jl"
}

def extract_findings(stdout):
    # 只在 "Scan completed successfully." 后查找 Findings
    scan_and_findings_match = re.search(r"Scan completed successfully\.\s*• Findings:\s*(\d+)", stdout)
    
    if scan_and_findings_match:
        findings_count = int(scan_and_findings_match.group(1))
        if findings_count > 0:
            # 提取 "Code Finding" 和 "Scan Summary" 之间的内容
            detail_match = re.search(r"┌────────────────┐.*?└────────────────┘\s*(.*?)┌──────────────┐", stdout, re.DOTALL)
            if detail_match:
                # 提取到的内容并去掉代码地址
                bug_description = detail_match.group(1).strip()
                bug_description = re.sub(r"/.*\.py", "", bug_description)  # 去除代码文件路径
                return findings_count, bug_description
    return 0, ""  # 如果没有发现问题，返回 0 和空字符串

@GENERATOR_REGISTRY.register()
class StaticCodeChecker:
    
    def __init__(self, config, args=None):
        self.args = args
        self.input_file = config.get('input_file')
        self.output_file = config.get('output_file')
        self.input_key = config.get('input_key', 'content') # "code" for 100_data_lang.jsonl and "content" for 100_data.jsonl
        self.output_key = config.get('output_key', 'static_checked_content')
        self.logger = get_logger()
        self.logger.info("Initializing StaticCodeChecker...")
        if 'db_name' in config.keys():
            self.storage = MyScaleStorage(config['db_port'], config['db_name'], config['table_name'])
            self.pipeline_id = config['pipeline_id']
            self.stage = config.get('stage', 1)
            self.eval_stage = config.get('eval_stage', 0)
        if not self.input_file or not self.output_file:
            raise ValueError("Both input_file and output_file must be specified in the config.")

    @staticmethod
    def get_desc(lang):
        return "对代码进行静态类型检查" if lang == "zh" else "Perform static type checking on the code"

    def static_check_code_with_semgrep(self, lang, code):
        """
        使用 semgrep 进行静态代码检查，返回检查结果。
        
        参数：
          - lang: 代码所属的语言（例如 "python", "c", "java" 等）。
          - code: 原始代码。
        
        返回：
          - check_result: 0 表示无错误，1 表示有错误。
          - detail: semgrep 检查的详细输出信息。
        """
        # 在当前文件夹下创建临时文件夹用于存储临时代码文件
        temp_dir = os.path.join(os.getcwd(), "temp_files_semgrep")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # 创建一个临时文件，并将其存储在 temp_files_semgrep 文件夹中
        with tempfile.NamedTemporaryFile(mode="w", suffix=ext_map.get(lang.lower(), ".py"), delete=False, encoding="utf-8", dir=temp_dir) as tmp_file:
            tmp_file.write(code)
            tmp_filename = tmp_file.name

        try:
            # 通过 subprocess 调用 semgrep 对临时文件进行检查
            # 命令：semgrep --config=auto <filename>
            # result = subprocess.run(
            #     ["semgrep", "--config=auto", tmp_filename, "--error"],
            #     capture_output=True,
            #     text=True
            # )
            result = subprocess.run(
                ["semgrep", "--config", "p/default", tmp_filename, "--error"],
                capture_output=True,
                text=True
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            # 如果返回码为 0，表示没有问题
            if result.returncode == 0:
                check_result = 0
                detail = "No issues found."
   #             detail = "No issues found."
            else:
                check_result = 1
                detail = stdout


        except Exception as e:
            check_result = 1
            detail = f"执行 semgrep 时发生异常：{e}"

        # 注释掉删除临时文件的代码，便于你检查这些文件
        finally:
            # 删除临时文件
            os.remove(tmp_filename)

        return check_result, detail

    def _load_input(self):
        if hasattr(self, 'storage'):
            value_list = self.storage.read_json(['data'], category='code', format='PT', syn='', pipeline_id=self.pipeline_id, stage=self.stage, eval_stage=self.eval_stage)
            return pd.DataFrame([{'id': _['id']} | _['data'] for _ in value_list])
        else:
            return pd.read_json(self.input_file, lines=True)
    
    def _write_output(self, save_path, data):
        if hasattr(self, 'storage'):
            self.storage.write_eval(data, score_key='check_result', info_key='detail', algo_name=self.__class__.__name__, stage=self.stage+1)
        else:
            with open(save_path, 'w', encoding='utf-8') as f:
                for item in data:
                    for k,v in item.items():
                        if pd.isna(v):
                            item[k] = None
                    json.dump(item, f)
                    f.write('\n')

    
    def run(self):
        """
        读取 JSONL 文件，逐行进行静态检查，添加检查结果（check_result）和详细信息（detail）到每行，
        然后将更新后的数据写入到输出文件。
        """
        self.logger.info("Start running StaticCodeChecker...")
        self.logger.info(f"Reading input file: {self.input_file}...")

        # 读取 JSONL 文件到 DataFrame
        df = self._load_input()
        data = df.to_dict(orient='records')  # 转换为字典列表
        
        self.logger.info(f"Read Success!")

        # 使用 ThreadPoolExecutor 并行处理检查
        with ThreadPoolExecutor(max_workers=64) as executor:
            future_to_item = {}
            for item in tqdm(data):
                code = item.get(self.input_key, "")
                lang = item.get("lang", "python")
                if code:
                    future = executor.submit(self.static_check_code_with_semgrep, lang, code)
                    future_to_item[future] = item

            # 收集任务返回结果并更新记录
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    check_result, detail = future.result()
                except Exception as exc:
                    check_result, detail = 1, f"异常：{exc}"
                item["check_result"] = check_result
                item["detail"] = detail
                
        self.logger.info(f"Saving Result")
        self._write_output(self.output_file, data)
        # 将更新后的数据保存到输出文件
        # with open(self.output_file, 'w', encoding='utf-8') as f:
        #     for item in data:
        #         for k,v in item.items():
        #             if pd.isna(v):
        #                 item[k] = None
        #         json.dump(item, f)
        #         f.write('\n')
        
        self.logger.info(f"Save Success!")
        self.logger.info("Shutting down StaticCodeChecker...")

                

        
