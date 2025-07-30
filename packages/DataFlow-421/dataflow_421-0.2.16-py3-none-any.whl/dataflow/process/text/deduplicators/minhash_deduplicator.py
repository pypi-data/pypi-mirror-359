from dataflow.core import TextDeduplicator
from dataflow.utils.registry import PROCESSOR_REGISTRY
from datasketch import MinHash, MinHashLSH  # use datasketch-1.6.5
from tqdm import tqdm
from collections.abc import Sequence
from dataflow.utils.utils import get_logger


@PROCESSOR_REGISTRY.register()
class MinHashDeduplicator(TextDeduplicator):
    def __init__(self, args_dict: dict):
        super().__init__(args_dict)
        self.deduplicator_name = 'MinHashDeduplicator'
        self.logger = get_logger()
        # Initialize parameters
        self.logger.info(f"Initializing {self.deduplicator_name}...")
        self.num_perm = args_dict.get('num_perm', 128)
        self.threshold = args_dict.get('threshold', 0.9)
        self.use_n_gram = args_dict.get('use_n_gram', True)
        self.n_gram = args_dict.get('n_gram', 5)
    
    @staticmethod
    def get_desc(lang):
        return "使用MinHash算法进行文本去重" if lang == "zh" else "Deduplicate text using the MinHash algorithm."

    def create_minhash(self, data):
        minhash = MinHash(num_perm=self.num_perm)
        if self.use_n_gram:
            for i in range(len(data) - self.n_gram + 1):
                minhash.update(data[i:i + self.n_gram].encode('utf8'))
        else:
            for d in data:
                minhash.update(d.encode('utf8'))
        return minhash

    def dedup_func(self, dataset):
        self.logger.info(f"Start running {self.dedupliactor_name}...")
        lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)

        labels = [0] * len(dataset)
        with lsh.insertion_session() as session:  
            for idx, sample in tqdm(enumerate(dataset), desc=f"Implementing {self.deduplicator_name}", total=len(dataset)):
                text = str(sample[dataset.keys])
                minhash = self.create_minhash(text)
                result = lsh.query(minhash)
                
                if len(result) == 0:
                    labels[idx] = 1
                    session.insert(idx, minhash)
                    self.logger.debug(f"Inserted item {idx} into LSH with minhash.")

        self.logger.info(f"Deduplication completed. Total unique items: {sum(labels)}")
        return labels
        
        

        
        

