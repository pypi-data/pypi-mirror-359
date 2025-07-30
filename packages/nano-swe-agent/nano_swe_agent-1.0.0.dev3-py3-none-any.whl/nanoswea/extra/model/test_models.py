class DeterministicModel:
    def __init__(self, outputs: list[str]):
        """
        Initialize with a list of outputs to return in sequence.
        """
        self.outputs = outputs
        self.current_index = -1
        self.cost = 0.0
        self.n_calls = 0

    def query(self, messages: list[dict[str, str]]) -> str:
        self.n_calls += 1
        self.current_index += 1
        return self.outputs[self.current_index]
