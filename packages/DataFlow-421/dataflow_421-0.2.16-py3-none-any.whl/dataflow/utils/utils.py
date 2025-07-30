import numpy as np
import subprocess
import torch
import logging
import colorlog

def download_model_from_hf(model_name, model_cache_dir):
    logging.info(f"Downloading {model_name} to {model_cache_dir}.")
    command = ['huggingface-cli', 'download', '--resume-download', model_name, '--local-dir', model_cache_dir]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Failed to download {model_name}.")
        logging.error(result.stderr)
        return False
    logging.info(f"Successfully downloaded {model_name} to {model_cache_dir}.")
    return True

def round_to_sigfigs(num, sigfigs):
    import math
    if isinstance(num, np.float32):
        num = float(num)
    if num == 0:
        return 0
    else:
        return round(num, sigfigs - int(math.floor(math.log10(abs(num)))) - 1)


def recursive_insert(ds_scores_dict, scores: dict, idx_list):
    for k, v in scores.items():
        if isinstance(v, dict):
            recursive_insert(ds_scores_dict[k], v, idx_list)
        elif isinstance(v, torch.Tensor):
            ds_scores_dict[k][idx_list] = v.cpu().detach().numpy()
        elif isinstance(v, np.ndarray):
            ds_scores_dict[k][idx_list] = v
        elif isinstance(v, list):
            ds_scores_dict[k][idx_list] = np.array(v)
        elif isinstance(v, float):
            ds_scores_dict[k][idx_list] = np.array(v)
        else:
            raise ValueError(f"Invalid scores type {type(v)} returned")

def recursive_func(scores: dict, func, output: dict):
    for k, v in scores.items():
        if isinstance(v, dict):
            if k not in output.keys():
                output[k] = {}
            recursive_func(scores[k], func, output[k])
        elif isinstance(v, (np.float64, np.float32, np.ndarray)):
            if isinstance(v, np.ndarray) and np.isnan(v).all():
                output[k] = v
            elif isinstance(v, (np.float64, np.float32)) and np.isnan(v):
                output[k] = v
            else:
                output[k] = func(v)
        elif isinstance(v, str):
            output[k] = v  
        else:
            raise ValueError(f"Invalid scores type {type(v)} returned")




def recursive_len(scores: dict):
    import numpy as np
    for _, v in scores.items():
        if isinstance(v, dict):
            return recursive_len(v)
        elif isinstance(v, np.ndarray):
            return v.shape[0]
        elif isinstance(v, list):
            return len(v)
        else:
            raise ValueError(f"Invalid scores type {type(v)} returned")
        
def recursive_idx(scores: dict, index, output: dict):
    for k, v in scores.items():
        if isinstance(v, dict):
            if k not in output.keys():
                output[k] = {}
            recursive_idx(scores[k], index, output[k])
        elif isinstance(v, np.ndarray):
            output[k] = v[index]
        elif isinstance(v, list): 
            output[k] = v[index] 
        else:
            raise ValueError(f"Invalid scores type {type(v)} returned")

def recursive(scores: dict, output: dict):
    for k, v in scores.items():
        if isinstance(v, dict):
            if k not in output.keys():
                output[k] = {}
            recursive(scores[k], output[k])
        else:
            output[k] = v

def list_image_eval_metrics():
    from dataflow.config import init_config
    import pyiqa

    cfg = init_config()
    metric_dict = {}
    metric_dict['image']=pyiqa.list_models(metric_mode="NR")

    for k, v in cfg.image.items():
        if v['data_type'] in metric_dict:
            metric_dict[v['data_type']].append(k)
        else:
            metric_dict[v['data_type']] = [k]
    for k, v in metric_dict.items():
        logging.info(f"metric for {k} data:")
        logging.info(v)


def get_scorer(metric_name, device):
    from dataflow.config import init_config
    from dataflow.utils.registry import MODEL_REGISTRY
    import pyiqa

    cfg = init_config()
    if metric_name in cfg.image:
        model_args = cfg.image[metric_name]
        model_args['model_cache_dir'] = cfg.model_cache_path
        model_args['num_workers'] = cfg.num_workers
        scorer = MODEL_REGISTRY.get(model_args['class_name'])(device=device, args_dict=model_args)
    elif metric_name in pyiqa.list_models(metric_mode="NR"):
        # model_args={}
        model_args = cfg.image['pyiqa']
        model_args['model_cache_dir'] = cfg.model_cache_path
        model_args['num_workers'] = cfg.num_workers
        scorer = MODEL_REGISTRY.get(model_args['class_name'])(device=device, metric_name=metric_name, args_dict=model_args)
    elif metric_name in cfg.video:
        model_args = cfg.video[metric_name]
        scorer = MODEL_REGISTRY.get(metric_name)(model_args)
    else:
        raise ValueError(f"Metric {metric_name} is not supported.")
    
    assert scorer is not None, f"Scorer for {metric_name} is not found."
    return scorer

def new_get_scorer(scorer_name, model_args):
    from dataflow.utils.registry import MODEL_REGISTRY
    logging.info(scorer_name, model_args)
    scorer = MODEL_REGISTRY.get(scorer_name)(args_dict=model_args)
    
    assert scorer is not None, f"Scorer for {scorer_name} is not found."
    return scorer


def calculate_score():
    from ..config import new_init_config
    from dataflow.utils.registry import FORMATTER_REGISTRY
    from dataflow.core import ScoreRecord

    cfg = new_init_config()
    
    # for x in cfg['dependencies']:
    #     if x == 'text':
    #         import dataflow.Eval.Text
    #     elif x == 'image':
    #         import dataflow.Eval.image
    #     elif x == 'video':
    #         import dataflow.Eval.video
    #     else:
    #         raise ValueError('Please Choose Dependencies in text, image, video!')
        

    dataset_dict = {}
    score_record = ScoreRecord()
    for scorer_name, model_args in cfg.scorers.items():
        if "num_workers" in cfg:
            model_args["num_workers"] = cfg.num_workers
        if "model_cache_path" in cfg:
            model_args["model_cache_dir"] = cfg.model_cache_path
        scorer = new_get_scorer(scorer_name, model_args)
        if scorer.data_type not in dataset_dict:
            formatter = FORMATTER_REGISTRY.get(cfg['data'][scorer.data_type]['formatter'])(cfg['data'][scorer.data_type])
            datasets = formatter.load_dataset()
            dataset_dict[scorer.data_type] = datasets
            dataset = datasets[0] if type(datasets) == tuple else datasets
            dataset.set_score_record(score_record)
        else:
            datasets = dataset_dict[scorer.data_type]
        _, score = scorer(datasets)
    save_path = cfg['save_path']
    score_record.dump_scores(save_path)

def get_processor(processor_name, config=None, args=None):
    from dataflow.utils.registry import PROCESSOR_REGISTRY
    if config is not None:
        args = config
    logger = get_logger()
    # print(processor_name, args, flush=True)
    processor = PROCESSOR_REGISTRY.get(processor_name)(args)
    if processor is not None:
        logger.info(f"Successfully get processor {processor_name}, args {args}")
    else:
        logger.error(f"Processor {processor} is not found")
    assert processor is not None
    return processor

def get_generator(generator_name, args):
    from dataflow.utils.registry import GENERATOR_REGISTRY
    # print(generator_name, args)
    generator = GENERATOR_REGISTRY.get(generator_name)(args)
    logger = get_logger()
    if generator is not None:
        logger.info(f"Successfully get generator {generator_name}, args {args}")
    else:
        logger.error(f"Generator {generator} is not found")
    assert generator is not None
    return generator

def get_logger(level=logging.INFO):
    # 创建logger对象
    logger = logging.getLogger()
    logger.setLevel(level)
    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    # 定义颜色输出格式
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s %(asctime)s | %(filename)-20s- %(module)-20s- %(funcName)-20s- %(lineno)5d - %(name)-10s | %(levelname)8s | Processno %(process)5d - Threadno %(thread)-15d : %(message)s', 
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    # 将颜色输出格式添加到控制台日志处理器
    console_handler.setFormatter(color_formatter)
    # 移除默认的handler
    for handler in logger.handlers:
        logger.removeHandler(handler)
    # 将控制台日志处理器添加到logger对象
    logger.addHandler(console_handler)
    return logger

def pipeline_step(yaml_path, step_name, step_type):
    import yaml
    logger = get_logger()
    logger.info(f"Loading yaml {yaml_path} ......")
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)
    config = merge_yaml(config)
    logger.info(f"Load yaml success, config: {config}")
    if step_type == "process":
        algorithm = get_processor(step_name, config)
    elif step_type == "generator":
        algorithm = get_generator(step_name, config)
    logger.info("Start running ...")
    algorithm.run()
    

def process():
    from ..config import new_init_config
    from dataflow.data import DataFlowDSDict
    from dataflow.utils.registry import FORMATTER_REGISTRY
    from dataflow.core import ScoreRecord
    cfg = new_init_config()
    dataset_dict = DataFlowDSDict()
    for scorer_name, args in cfg.processors.items():
        if "num_workers" in cfg:
            args["num_workers"] = cfg.num_workers
        if "model_cache_path" in cfg:
            args["model_cache_dir"] = cfg.model_cache_path
        processor = get_processor(scorer_name, args)
        if processor.data_type not in dataset_dict.keys():
            formatter = FORMATTER_REGISTRY.get(cfg['data'][processor.data_type]['formatter'])(cfg['data'][processor.data_type])
            datasets = formatter.load_dataset()
            dataset_dict[processor.data_type] = datasets
            dataset = datasets[0] if type(datasets) == tuple else datasets
        else:
            datasets = dataset_dict[processor.data_type]
        processed_dataset = processor(datasets)
        dataset_dict[processor.data_type] = processed_dataset
    save_path = cfg['save_path']
    for dataset in dataset_dict.values():
        dataset.dump(save_path)

def merge_yaml(config):
    if not config.get("vllm_used"):
        return config
    else:
        vllm_args_list = config.get("vllm_args", [])
        if isinstance(vllm_args_list, list) and len(vllm_args_list) > 0 and isinstance(vllm_args_list[0], dict):
            vllm_args = vllm_args_list[0]
            config.update(vllm_args)  # 合并进顶层
        return config