# erd_generator/parsers/base_parser.py

from abc import ABC, abstractmethod
import pandas as pd

class BaseParser(ABC):
    @abstractmethod
    def parse(self) -> pd.DataFrame:
        """Parse data and return a standardized DataFrame."""
        pass