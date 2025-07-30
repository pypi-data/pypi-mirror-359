import json
import logging
from tqdm import tqdm
import pandas as pd
from tree_sitter import Language, Parser
from tree_sitter_languages import get_language
from dataflow.utils.registry import GENERATOR_REGISTRY
from dataflow.utils.utils import get_logger
from dataflow.data import MyScaleStorage

# import tree_sitter_bash as tsbash
# import tree_sitter_c as tsc
# import tree_sitter_c_sharp as tscsharp
# import tree_sitter_cpp as tscpp
# import tree_sitter_css as tscss
# import tree_sitter_go as tsgo
# import tree_sitter_haskell as tshaskell
# import tree_sitter_html as tshtml
# import tree_sitter_java as tsjava
# import tree_sitter_javascript as tsjs
# import tree_sitter_json as tsjson
# import tree_sitter_kotlin as tskotlin
# import tree_sitter_lua as tslua
# import tree_sitter_markdown as tsmarkdown
# import tree_sitter_ocaml as tsocaml
# import tree_sitter_php as tsphp
# import tree_sitter_python as tspython
# import tree_sitter_ruby as tsruby
# import tree_sitter_rust as tsrust
# import tree_sitter_sql as tssql
# import tree_sitter_toml as tstoml
# import tree_sitter_typescript as tstypescript
# import tree_sitter_yaml as tsyaml

@GENERATOR_REGISTRY.register()
class TreeSitterParser:
    
    def __init__(self, config, args=None):
        self.args = args
        self.input_file = config.get('input_file')
        self.output_file = config.get('output_file')
        self.input_key = config.get('input_key', 'code')
        # self.output_key = config.get('output_key', 'answer')
        self.logger = get_logger()
        self.logger.info("Initializing TreeSitterParser...")
        if 'db_name' in config.keys():
            self.storage = MyScaleStorage(config['db_port'], config['db_name'], config['table_name'])
            self.pipeline_id = config['pipeline_id']
            self.stage = config.get('stage', 1)
            self.eval_stage = config.get('eval_stage', 0)
            self.read_min_score = config.get('read_min_score', [])
            self.read_max_score = config.get('read_max_score', [])
        if not self.input_file or not self.output_file:
            self.logger.error("Both input_file and output_file must be specified in the config.")
            raise ValueError("Both input_file and output_file must be specified in the config.")
        self.lang_parsers = {}
        # 初始化语言模块
        # self.language_modules = {
        #     'bash': tsbash,
        #     'c': tsc,
        #     'c_sharp': tscsharp,
        #     'cpp': tscpp,
        #     'css': tscss,
        #     'go': tsgo,
        #     'haskell': tshaskell,
        #     'html': tshtml,
        #     'java': tsjava,
        #     'javascript': tsjs,
        #     'json': tsjson,
        #     'kotlin': tskotlin,
        #     'lua': tslua,
        #     'markdown': tsmarkdown,
        #     # 'ocaml': tsocaml,
        #     # 'php': tsphp,
        #     'python': tspython,
        #     'ruby': tsruby,
        #     'rust': tsrust,
        #     'sql': tssql,
        #     'toml': tstoml,
        #     # 'typescript': tstypescript,
        #     'yaml': tsyaml,
        # }
    
    @staticmethod
    def get_desc(lang):
        return "对代码进行AST等级检查" if lang == "zh" else "Perform AST-level checks on the code"    
    
    @staticmethod
    def print_tree_errors(source_code: bytes, tree):
        """
        打印 Tree-sitter 语法树中所有错误节点的位置和内容片段。
        """
        err_info = ""
        def recurse(node):
            nonlocal err_info
            if node.has_error or node.is_error:
                start = node.start_byte
                end = node.end_byte
                start_point = node.start_point  # (row, column)
                end_point = node.end_point
                error_snippet = source_code[start:end].decode('utf-8', errors='replace')
                
                err_info += f"[Error] {node.type} at lines {start_point[0]+1}:{start_point[1]+1} to {end_point[0]+1}:{end_point[1]+1}\n"
                err_info += f"--> Code: {error_snippet!r}\n"
                err_info += "-" * 40 + "\n"
            for child in node.children:
                recurse(child)

        root = tree.root_node
        recurse(root)
        return err_info

    def _get_parser(self, lang):
        if lang not in self.lang_parsers.keys():
            try:
                if lang == 'typescript':
                    parser = Parser()
                    parser.set_language(get_language('tsx'))
                    self.lang_parsers[lang] = parser
                else:
                    parser = Parser()
                    parser.set_language(get_language(lang))
                    self.lang_parsers[lang] = parser
            except AttributeError as e:
                self.logger.debug(f"Unsupported Language: {lang}")
                self.logger.debug(f"Error {e}")
                return None
        return self.lang_parsers[lang]
    
    def _load_input(self):
        if hasattr(self, 'storage'):
            value_list = self.storage.read_json(['data'], category='code', format='PT', syn='', pipeline_id=self.pipeline_id, stage=self.stage, eval_stage=self.eval_stage, maxmin_scores=[dict(zip(['min_score', 'max_score'], list(_))) for _ in list(zip(self.read_min_score, self.read_max_score))])
            return pd.DataFrame([{'id': _['id']} | _['data'] for _ in value_list])
        else:
            return pd.read_json(self.input_file, lines=True)
    
    def _write_output(self, save_path, data):
        if hasattr(self, 'storage'):
            self.storage.write_eval(data, score_key='ast_error', info_key='ast_error_info', algo_name=self.__class__.__name__, stage=self.stage+1)
        else:
            with open(save_path, 'w', encoding='utf-8') as f:
                for item in data:
                    for k,v in item.items():
                        if pd.isna(v):
                            item[k] = None
                    json.dump(item, f)
                    f.write('\n')

    def run(self):
        self.logger.info("Start running TreeSitterParser...")
        self.logger.info(f"Reading input file: {self.input_file}...")
        df = self._load_input()
        data = df.to_dict(orient='records')
        self.logger.info(f"Read Success!")
        for item in tqdm(data):
                parser = self._get_parser(item['lang'])
                if parser is not None:
                    tree = parser.parse(item[self.input_key].encode('utf-8'))
                    item['ast_error'] = int(tree.root_node.has_error)
                    if item['ast_error'] == 1:
                        item['ast_error_info'] = self.print_tree_errors(item[self.input_key].encode('utf-8'), tree)
                    else:
                        item['ast_error_info'] = ''
                    self.logger.debug(f"Processed lang: {item['lang']}")                
                else:
                    item['ast_error'] = -1
                    item['ast_error_info'] = ''
        self._write_output(self.output_file, data)
        self.logger.info(f"Saving Result into")
        # with open(self.output_file, 'w') as f:
        #     for item in data:
        #         for k,v in item.items():
        #             if isinstance(v, list):
        #                 continue
        #             if pd.isna(v):
        #                 item[k] = None
        #         json.dump(item, f)
        #         f.write('\n')
        self.logger.info(f"Save Success!")
        self.logger.info("Shutting down TreeSitterParser...")


        
