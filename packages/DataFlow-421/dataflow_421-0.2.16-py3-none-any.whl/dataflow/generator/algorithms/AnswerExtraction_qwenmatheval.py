import pandas as pd
from tqdm import tqdm
import logging
import re
from word2number import w2n
from dataflow.utils.registry import GENERATOR_REGISTRY
from dataflow.utils.utils import get_logger
from dataflow.data import MyScaleStorage, DatabaseConfig
import os

class StringProcessor:
    """
    A class that encapsulates various string processing functions for mathematical expressions.
    """

    @staticmethod
    def _fix_fracs(string):
        """
        Fixes fraction expressions in the string, ensuring they are properly formatted as \frac{a}{b}.
        """
        substrs = string.split("\\frac")
        new_str = substrs[0]
        if len(substrs) > 1:
            for substr in substrs[1:]:
                new_str += "\\frac"
                if len(substr) > 0 and substr[0] == "{":
                    new_str += substr
                else:
                    if len(substr) >= 2:
                        a, b = substr[0], substr[1]
                        if b != "{":
                            new_str += f"{{{a}}}{{{b}}}{substr[2:]}" if len(substr) > 2 else f"{{{a}}}{{{b}}}"
                        else:
                            new_str += f"{{{a}}}{b}{substr[2:]}" if len(substr) > 2 else f"{{{a}}}{b}"
                    else:
                        return string
        return new_str

    @staticmethod
    def _fix_a_slash_b(string):
        """
        Fixes cases where a fraction is represented as a simple division (e.g., a/b) and converts it to \frac{a}{b}.
        """
        if len(string.split("/")) != 2:
            return string
        a, b = string.split("/")
        try:
            a, b = int(a) if "sqrt" not in a else a, int(b) if "sqrt" not in b else b
            assert string == f"{a}/{b}"
            return f"\\frac{{{a}}}{{{b}}}"
        except:
            return string

    @staticmethod
    def _fix_sqrt(string):
        """
        Ensures that square root expressions are properly formatted as \sqrt{...}.
        """
        return re.sub(r"\\sqrt(\w+)", r"\\sqrt{\1}", string)

    @staticmethod
    def convert_word_number(text: str) -> str:
        """
        Converts a word representation of a number to a digit.
        """
        try:
            return str(w2n.word_to_num(text))
        except:
            return text


# Unit Text Class to Manage Unit Texts
class UnitTextManager:
    """
    A class that encapsulates unit text management to remove unwanted unit terms from strings.
    """

    def __init__(self):
        """
        Initializes the unit texts and their plural forms.
        """
        self.unit_texts = [
            "east", "degree", "mph", "kmph", "ft", "m sqaure", "m east", "sq m", "deg", "mile", "q .", "monkey", "prime",
            "ratio", "profit of rs", "rd", "o", "gm", "p . m", "lb", "tile", "per", "dm", "lt", "gain", "ab", "way", "west",
            "a .", "b .", "c .", "d .", "e .", "f .", "g .", "h .", "t", "a", "h", "no change", "men", "soldier", "pie", "bc",
            "excess", "st", "inches", "noon", "percent", "by", "gal", "kmh", "c", "acre", "rise", "a . m", "th", "π r 2", "sq",
            "mark", "l", "toy", "coin", "sq . m", "gallon", "° f", "profit", "minw", "yr", "women", "feet", "am", "pm", "hr",
            "cu cm", "square", "v â € ™", "are", "rupee", "rounds", "cubic", "cc", "mtr", "s", "ohm", "number", "kmph", "day",
            "hour", "minute", "min", "second", "man", "woman", "sec", "cube", "mt", "sq inch", "mp", "∏ cm ³", "hectare",
            "more", "sec", "unit", "cu . m", "cm 2", "rs .", "rs", "kg", "g", "month", "km", "m", "cm", "mm", "apple", "liter",
            "loss", "yard", "pure", "year", "increase", "decrease", "d", "less", "Surface", "litre", "pi sq m", "s .", "metre",
            "meter", "inch",
        ]
        self.unit_texts.extend([t + "s" for t in self.unit_texts])

    def clean_units(self, string: str):
        """
        Cleans the string by removing unit terms from it.
        """
        for unit_text in self.unit_texts:
            string = re.sub(r"(^|\W)" + unit_text + r"($|\W)", r"\1\2", string)
        return string


# Main String Processing Class
class StringCleaner:
    """
    A class responsible for cleaning and formatting strings in mathematical expressions.
    """

    def __init__(self, unit_manager: UnitTextManager):
        """
        Initializes the StringCleaner class with a unit manager.
        """
        self.unit_manager = unit_manager

    def strip_string(self, string, skip_unit=False):
        """
        Strips unwanted characters and units from the string.
        """
        string = str(string).strip().replace("\n", "").rstrip(".").replace("\\!", "")
        string = re.sub(r"\\begin\{array\}\{.*?\}", r"\\begin{pmatrix}", string)
        string = re.sub(r"\\end\{array\}", r"\\end{pmatrix}", string).replace("bmatrix", "pmatrix")
        string = string.replace("tfrac", "frac").replace("dfrac", "frac").replace("\\neq", "\\ne").replace("\\leq", "\\le").replace("\\geq", "\\ge")
        string = string.replace("\\left", "").replace("\\right", "").replace("\\{", "{").replace("\\}", "}")
        
        # Clean unit texts if needed
        if not skip_unit:
            string = self.unit_manager.clean_units(string)

        string = string.replace("^{\\circ}", "").replace("^\\circ", "").replace("\\$", "").replace("$", "").replace("\\(", "").replace("\\)", "")
        string = StringProcessor.convert_word_number(string)
        string = re.sub(r"\\text\{(.*?)\}", r"\1", string)
        
        for key in ["x=", "y=", "z=", "x\\in", "y\\in", "z\\in", "x\\to", "y\\to", "z\\to"]:
            string = string.replace(key, "")
        
        string = string.replace("\\emptyset", r"{}").replace("(-\\infty,\\infty)", "\\mathbb{R}")
        string = string.replace("%", "").replace(" .", " 0.").replace("{.", "{0.")
        
        return string


# Core Answer Extraction Logic Class
class AnswerExtractor:
    """
    A class responsible for extracting the final answer from a prediction string.
    """

    def __init__(self, string_cleaner: StringCleaner):
        """
        Initializes the AnswerExtractor class with a string cleaner.
        """
        self.string_cleaner = string_cleaner
        self.logger = get_logger()

    def extract_answer(self, pred_str, data_name, use_last_number=True):
        """
        Extracts the final answer from the prediction string, processing various formats.
        """
        if not pred_str:
            pred_str = ""
        pred_str = pred_str.replace("\u043a\u0438", "")
        
        # Handle special cases based on data_name or pattern
        if "final answer is $" in pred_str and "$. I hope" in pred_str:
            pred = pred_str.split("final answer is $", 1)[1].split("$. I hope", 1)[0].strip()
        elif "boxed" in pred_str:
            pred = self._extract_boxed_answer(pred_str)
        elif "he answer is" in pred_str:
            pred = pred_str.split("he answer is")[-1].strip()
        else:
            pred = self._get_last_number_answer(pred_str, use_last_number)
        
        pred = self.string_cleaner.strip_string(pred, skip_unit=data_name in ["carp_en", "minerva_math"])
        return pred

    def _extract_boxed_answer(self, pred_str):
        """
        Extracts answers enclosed in 'boxed' notation.
        """
        ans = pred_str.split("boxed")[-1]
        if ans.startswith("{"):
            return self._extract_bracketed_answer(ans)
        else:
            return ans.split("$")[0].strip()

    def _extract_bracketed_answer(self, ans):
        """
        Handles answers that are enclosed within brackets.
        """
        stack = 1
        result = ""
        for c in ans[1:]:
            if c == "{":
                stack += 1
                result += c
            elif c == "}":
                stack -= 1
                if stack == 0:
                    break
                result += c
            else:
                result += c
        return result

    def _get_last_number_answer(self, pred_str, use_last_number):
        """
        Extracts the last number from the string if use_last_number is True.
        """
        if use_last_number:
            pattern = "-?\d*\.?\d+"
            pred = re.findall(pattern, pred_str.replace(",", ""))
            return pred[-1] if pred else ""
        return ""


# The main class to manage the entire extraction process
@GENERATOR_REGISTRY.register()
class AnswerExtraction_qwenmatheval:
    """
    A class to handle the process of extracting answers from a dataset.
    """

    def __init__(self, config: dict):
        """
        Initializes the AnswerExtraction_qwenmatheval class.
        """
        self.config = config
        self._check_config()
        use_db = config.get("use_db", False) or os.environ.get("USE_DB", "").lower() == "true"
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
        else:
            self.input_file = self.config['input_file']
            self.output_file = self.config['output_file']
        self.input_key = self.config['input_key']
        self.response_key = self.config['response_key']
        self.extraction_key = self.config['extraction_key']
        self.data_name = self.config.get('dataset_name', None)
        self.logger = get_logger()

        # Initialize helpers
        unit_manager = UnitTextManager()
        string_cleaner = StringCleaner(unit_manager)
        self.answer_extractor = AnswerExtractor(string_cleaner)

    def _check_config(self):
        """
        Ensures that the configuration contains all necessary keys.
        Must have either (input_file and output_file) or db_name.
        """
        config = self.config  # for brevity

        # Check general required keys
        required_keys = ['response_key', 'extraction_key']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Key {key} is missing in the config")

        # Check data source requirement
        has_file_io = 'input_file' in config and 'output_file' in config
        has_db = 'db_name' in config
        if not (has_file_io or has_db):
            raise ValueError("Config must contain either both 'input_file' and 'output_file', or 'db_name'")

    @staticmethod
    def get_desc(lang):
        if lang == "zh":
            return (
                "该算子用于从数学问题回答中提取规范化答案表达式，进行字符串清洗、单位处理和格式标准化。\n\n"
                "输入参数：\n"
                "- input_key：输入数据字段名\n"
                "- answer_key：原始答案字段名\n"
                "- output_key：处理后的答案字段名\n"
                "- unit_texts：需要过滤的单位文本列表\n\n"
                "输出参数：\n"
                "- output_key：标准化后的数学表达式字段"
            )
        elif lang == "en":
            return (
                "This operator extracts and normalizes mathematical expressions from answers, "
                "performing string cleaning, unit processing and format standardization.\n\n"
                "Input Parameters:\n"
                "- input_key: Input data field name\n"
                "- answer_key: Raw answer field name\n"
                "- output_key: Processed answer field name\n"
                "- unit_texts: List of unit texts to filter\n\n"
                "Output Parameters:\n"
                "- output_key: Standardized mathematical expression field"
            )
        else:
            return "AnswerExtraction_qwenmatheval performs mathematical answer normalization and standardization."
        
    def _load_input(self):
        if hasattr(self, 'storage'):
            value_list = self.storage.read_json(
                [self.input_key], stage=0, syn='syn_a', format='SFT_Single'
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
            self.storage.write_data(output_rows, format="SFT_Single")
        else:
            dataframe.to_json(save_path, orient='records', lines=True)

    def run(self):
        """
        Executes the answer extraction process.
        """
        raw_dataframe = self._load_input()
        key_list = raw_dataframe.columns.to_list()
        if self.response_key not in key_list:
            raise ValueError(f"response_key: {self.response_key} not found in dataframe columns.")

        self.logger.info(f"Found {len(raw_dataframe)} rows.")
        extractions = [
            self.answer_extractor.extract_answer(resp, self.data_name)
            for resp in tqdm(raw_dataframe[self.response_key], desc='Processing')
        ]
        raw_dataframe[self.extraction_key] = extractions
        self._write_output(self.output_file, raw_dataframe, None)
