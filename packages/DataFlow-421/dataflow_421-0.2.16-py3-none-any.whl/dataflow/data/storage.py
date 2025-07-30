from abc import ABC, abstractmethod

# TODO: Abstract Storage

class DataFlowStorage(ABC):

    @abstractmethod
    def read_json(self, key_list: list, **kwargs) -> list:
        """Read code data from storage with JSON format

        Args:
            key_list: List of keys to read
            **kwargs: Additional parameters including:
                - stage: Current stage
                - format: Data format
                - syn: Synthetic flag
                - maxmin_scores: Optional list of score ranges
        """
        pass

    @abstractmethod
    def write_json(self, data: list, **kwargs) -> None:
        """Write code data to storage with JSON format

        Args:
            data: List of code data items
            **kwargs: Must include:
                - format: Data format
                - syn: Synthetic flag
        """
        pass

    @abstractmethod
    def write_data(self, data: list, **kwargs) -> None:
        """Write data to storage

        Args:
            data: List of data items to write
            **kwargs: Additional parameters to update
        """
        pass

    @abstractmethod
    def write_eval(self, data: list, **kwargs) -> None:
        """Write evaluation results to storage

        Args:
            data: List of evaluation results
            **kwargs: Must include:
                - algo_name: Algorithm name
                - score_key: Score field name
                - info_key: Optional info field name
        """
        pass

    @abstractmethod
    def read_code(self, key_list: list, **kwargs) -> list:
        """Read code data from storage

        Args:
            key_list: List of keys to read
            **kwargs: Additional parameters including:
                - stage: Current stage
                - format: Data format
                - syn: Synthetic flag
        """
        pass

    @abstractmethod
    def write_code(self, data: list, **kwargs) -> None:
        """Write code data to storage

        Args:
            data: List of code data items
            **kwargs: Must include:
                - format: Data format
                - syn: Synthetic flag
        """
        pass

    @abstractmethod
    def read_str(self, key_list: list, **kwargs) -> list:
        """Read string data from storage

        Args:
            key_list: List of keys to read
            **kwargs: Additional parameters including:
                - category: Data category
                - stage: Current stage
                - format: Data format
                - syn: Synthetic flag
                - pipeline_id: Pipeline identifier
                - eval_stage: Evaluation stage
        """
        pass

    @abstractmethod
    def write_str(self, data: list, **kwargs) -> None:
        """Write string data to storage

        Args:
            data: List of string data items
            **kwargs: Must include:
                - format: Data format
                - syn: Synthetic flag
        """
        pass
