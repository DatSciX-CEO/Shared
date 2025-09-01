
import pandas as pd
from adk.tools import Tool

class FileReaderTool(Tool):
    def __init__(self):
        super().__init__(
            name="file_reader",
            description="Reads a CSV or Excel file and returns its content as a string.",
        )

    def call(self, file_path: str) -> str:
        """Reads a CSV or Excel file and returns its content as a string.

        Args:
            file_path: The path to the CSV or Excel file.

        Returns:
            The content of the file as a string.
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                return "Unsupported file type. Please provide a CSV or Excel file."

            return df.to_string()
        except Exception as e:
            return f"Error reading file: {e}"
