from dataflow.core import ReasonerFilter
# from math_verify import parse, verify, LatexExtractionConfig
import numpy as np
from dataflow.utils.registry import PROCESSOR_REGISTRY
#from math_verify import parse, verify, LatexExtractionConfig
import pandas as pd
from tqdm import tqdm
import logging
import re
from word2number import w2n
from dataflow.utils.utils import get_logger
from datasets import Dataset
from dataflow.data import TextDataset
import os


# Helper Class for String Processing
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

    def extract_answer(self, pred_str, data_name, use_last_number=True):
        """
        Extracts the final answer from the prediction string, processing various formats.
        """
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


@PROCESSOR_REGISTRY.register()
class AnswerGroundTruthFilter(ReasonerFilter):
    def __init__(self, args_dict: dict):
        super().__init__(args_dict)
        self.filter_name = 'AnswerGroundTruthFilter'
        unit_manager = UnitTextManager()
        string_cleaner = StringCleaner(unit_manager)
        self.answer_extractor = AnswerExtractor(string_cleaner)

        name2compare = {
            'exact': self.exact_compare,
            'math_verify': self.math_verify_compare
        }
        self.logger = get_logger()

        self.compare = name2compare[args_dict.get('compare_method', 'exact')]
        use_db = args_dict.get("use_db", False) or os.environ.get("USE_DB", "").lower() == "true"
        if use_db:
            self.read_min_score: list = args_dict['read_min_score']
            self.read_max_score: list = args_dict['read_max_score']
            self.eval_stage = args_dict['eval_stage']
            self.stage = args_dict["stage"]
            self.pipeline_id = args_dict["pipeline_id"]
            self.dataset = self._load_input()

    def _load_input(self):
        if hasattr(self, 'storage'):
            value_list = self.storage.read_json(
                [self.input_key], eval_stage=self.eval_stage, format=self.read_format, syn=self.read_syn,  maxmin_scores=[dict(zip(['min_score', 'max_score'], list(_))) for _ in list(zip(self.read_min_score, self.read_max_score))], stage=self.stage, pipeline_id=self.pipeline_id, category="reasoning"
            )
            value_list = [        
                {**item['data'], 'id': str(item['id'])}
                for item in value_list
            ]
            
            dataset = Dataset.from_list(value_list)
            return TextDataset(
                dataset=dataset,
                keys=value_list[0].keys(),
                metadata=None 
            )
        else:
            pass
        
    def _write_output(self, labels, ids):
        if hasattr(self, 'storage'):
            output_rows = []
            for _, label in zip(ids, labels):
                output_rows.append({
                    self.result_key: label,
                    'id': _
                })
            self.storage.write_eval(output_rows, algo_name=self.filter_name, score_key=self.result_key, stage=self.stage+1)
        else:
            pass


    def exact_compare(self, answer, ground_truth):
        return str(answer) == str(ground_truth)
    
    def math_verify_compare(self, answer, ground_truth):
        try:
            from math_verify import parse, verify
            return verify(parse(str(ground_truth)), parse(str(answer)))
        except:
            try:
                return verify(parse(ground_truth), parse(answer))
            except:
                return False

    def filter_func(self, dataset):
        indexes = np.zeros(len(dataset)).astype(int)
        for i in range(len(dataset)):
            final_answer =  self.answer_extractor.extract_answer(dataset[i][self.test_answer_key], dataset[i].get('data_name', None))
            if self.gt_answer_key in dataset[i]:
                # print("-------------------------------")
                # print(final_answer, dataset[i][self.gt_answer_key])
                if self.compare(final_answer, dataset[i][self.gt_answer_key]):
                    indexes[i] = 1
        return indexes

    @staticmethod
    def get_desc(lang):
        if lang == "zh":
            return (
                "该算子用于对比预测答案与标准答案的匹配度，支持精确匹配和数学验证两种方式。\n\n"
                "输入参数：\n"
                "- test_answer_key：预测答案字段名\n"
                "- gt_answer_key：标准答案字段名\n"
                "- compare_method：比较方法（exact/math_verify）\n\n"
                "输出参数：\n"
                "- 匹配成功返回1，否则返回0"
            )
        elif lang == "en":
            return (
                "This operator compares predicted answers against ground truth using exact or mathematical verification.\n\n"
                "Input Parameters:\n"
                "- test_answer_key: Predicted answer field\n"
                "- gt_answer_key: Ground truth field\n"
                "- compare_method: Comparison method (exact/math_verify)\n\n"
                "Output Parameters:\n"
                "- Returns 1 for matches, 0 otherwise"
            )
        else:
            return "AnswerGroundTruthFilter performs answer validation"