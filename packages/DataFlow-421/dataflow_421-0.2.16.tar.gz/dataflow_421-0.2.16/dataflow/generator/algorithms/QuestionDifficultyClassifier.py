import json
import os
import pandas as pd
from dataflow.generator.utils import APIGenerator_aisuite, APIGenerator_request
from dataflow.generator.utils.Prompts import QuestionDifficultyPrompt
import re
from dataflow.utils.registry import GENERATOR_REGISTRY
from dataflow.utils.utils import get_logger
from dataflow.data import MyScaleStorage, DatabaseConfig

@GENERATOR_REGISTRY.register()
class QuestionDifficultyClassifier():
    def __init__(self, args):
        """
        Initialize the QuestionCategoryClassifier with the provided configuration.
        """
        self.config = args
        self.prompts = QuestionDifficultyPrompt()
        use_db = args.get("use_db", False) or os.environ.get("USE_DB", "").lower() == "true"
        if use_db:
            db_config = DatabaseConfig(
                host=os.environ.get('MYSCALE_HOST', 'localhost'),
                port=int(os.environ.get('MYSCALE_PORT', '9000')),
                db_name=os.environ.get('MYSCALE_DATABASE', 'dataflow'),
                table_name=os.environ.get('MYSCALE_TABLE_NAME', ''),
                username=os.environ.get('MYSCALE_USER', ''),
                password=os.environ.get('MYSCALE_PASSWORD', '')
            )
            self.storage = MyScaleStorage(db_config)
            self.input_file = None
            self.output_file = None
            self.stage = args.get("stage",0)
            self.pipeline_id = args.get("pipeline_id","")
            self.read_min_score = self.config.get('read_min_score', 0.9)
            self.read_max_score = self.config.get('read_max_score', 2.0)
            self.eval_stage = self.config.get('eval_stage',1)
            self.read_format = self.config.get('read_format', '')
            self.read_syn = self.config.get('read_syn', '')
        else:
            self.input_file = args.get("input_file")
            self.output_file = args.get("output_file")
        self.input_key = self.config.get("input_key", "data")
        self.read_key = self.config.get("read_key", "question")  # default key for question input
        self.output_key = self.config.get("output_key", "classification_result")  # default output key
        self.logger = get_logger()
        
        # Ensure input_file and output_file are provided
        if not hasattr(self,'storage') and (not hasattr(self,'input_file') or not hasattr(self,'output_file')):
            raise ValueError("Both input_file and output_file must be specified in the config.")

        # Initialize the model
        self.model = self.__init_model__()
    
    def __init_model__(self):
        """
        Initialize the model generator based on the configuration.
        """
        generator_type = self.config.get("generator_type", "local").lower()
        
        if generator_type == "aisuite":
            return APIGenerator_aisuite(self.config)
        elif generator_type == "request":
            return APIGenerator_request(self.config)
        else:
            raise ValueError(f"Invalid generator type: {generator_type}")

    def _reformat_prompt(self, dataframe):
        """
        Reformat the prompts in the dataframe to generate questions.
        """
        # Check if read_key is in the dataframe
        if self.read_key not in dataframe.columns:
            key_list = dataframe.columns.tolist()
            raise ValueError(f"read_key: {self.read_key} not found in the dataframe. Available keys: {key_list}")

        formatted_prompts = []
        for i, text in enumerate(dataframe[self.read_key]):
            if text is not None:
                used_prompt = self.prompts.question_synthesis_prompt(text)
            else:
                used_prompt = None
            if used_prompt is not None:
                formatted_prompts.append(used_prompt.strip())
            else:
                # Handle the case where used_prompt is None (e.g., append an empty string or skip)
                # Assuming an empty string is acceptable for the downstream model
                formatted_prompts.append("")

        return formatted_prompts

    def _load_input(self):
        if hasattr(self, 'storage'):
            value_list = self.storage.read_json(
                [self.input_key], eval_stage=self.eval_stage, format=self.read_format, syn=self.read_syn, maxmin_scores=[{'max_score': self.read_max_score, 'min_score': self.read_min_score}], stage=self.stage, pipeline_id = self.pipeline_id, category="reasoning"
            )
            return pd.DataFrame([
                {**item['data'], 'id': str(item['id'])}
                for item in value_list
            ])
        else:
            return pd.read_json(self.input_file, lines=True)

    def _write_output(self, save_path, dataframe, extractions):
        if hasattr(self, 'storage'):
            output_rows = dataframe.where(pd.notnull(dataframe), None).to_dict(orient="records")
            output_rows = [
                {
                    "id": row.get("id"),
                    "difficulty_score": row.get("question_difficulty")
                }
                for row in output_rows
            ]
            self.storage.write_eval(output_rows, algo_name="QuestionDifficultyClassifier", score_key="difficulty_score", stage=self.stage+1)
        else:
            output_dir = os.path.dirname(self.output_file)
            os.makedirs(output_dir, exist_ok=True)
            dataframe.to_json(save_path, orient="records", lines=True)

    def run(self):
        # read input file : accept jsonl file only
        # dataframe = pd.read_json(self.input_file,lines=True)
        dataframe = self._load_input()

        # Check if the dataframe is empty
        if dataframe.empty:
            self.logger.info("Input DataFrame is empty, skipping classification.")
            return

        # model = self.__init_model__()
        formatted_prompts = self._reformat_prompt(dataframe)
        responses = self.model.generate_text_from_input(formatted_prompts)

        rating_scores = []
        for response in responses:
            # 修改后的正则表达式匹配数字和小数点，同时过滤非法结尾
            match = re.search(r'Rating:\s*((\d+\.\d+)|\d+)', response)
            if match:
                score_str = match.group(1).rstrip('.')  # 去除末尾可能的小数点
                try:
                    score = float(score_str)
                except ValueError:
                    score = -1
            else:
                score = -1
            rating_scores.append(score)

        #if self.output_key in dataframe.columns:
        #    key_list = dataframe.columns.tolist()
        #    raise ValueError(f"Found {self.output_text_key} in the dataframe, which leads to overwriting the existing column, please check the output_text_key: {key_list}")
        
        dataframe[self.output_key] = rating_scores
        
        
            # Save DataFrame to the output file
        # dataframe.to_json(self.output_file, orient="records", lines=True, force_ascii=False)
        self._write_output(self.output_file, dataframe, None)

    @staticmethod
    def get_desc(lang):
        if lang == "zh":
            return (
                "该算子用于评估问题的难度等级。"
                "通过大语言模型分析问题复杂度，输出1-10级的难度评分。\n\n"
                "输入参数：\n"
                "- eval_stage：评估阶段标识\n"
                "- read_min/max_score：分数过滤阈值\n"
                "- 其他参数同QuestionCategoryClassifier\n\n"
                "输出参数：\n"
                "- difficulty_score：数值型难度评分（1-10）"
            )
        elif lang == "en":
            return (
                "Evaluates question difficulty level using LLM analysis. "
                "Outputs numerical difficulty score from 1 to 10.\n\n"
                "Input Parameters:\n"
                "- eval_stage: Evaluation stage identifier\n"
                "- read_min/max_score: Score filtering thresholds\n"
                "- Other params same as QuestionCategoryClassifier\n\n"
                "Output Parameters:\n"
                "- difficulty_score: Numerical difficulty rating (1-10)"
            )