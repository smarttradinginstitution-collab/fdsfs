# app/Controllers/file_analysis_controller.py

from fastapi import File, UploadFile, HTTPException, status
import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileAnalysisController:
    """
    Controller to handle file analysis operations for CSV and XML files.
    """
    def __init__(self):
        """
        Initializes the controller. Currently stateless.
        """
        pass

    async def analyze_csv(self, file: UploadFile = File(...)):
        """
        Analyzes a CSV file and returns its content as a JSON array of objects.
        Each object represents a row, with column headers as keys.
        """
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload a CSV file."
            )

        try:
            # Read the file content into a bytes buffer
            contents = await file.read()
            # Use StringIO to treat the bytes as a file for pandas
            string_io = StringIO(contents.decode('utf-8'))

            # Read the CSV data into a pandas DataFrame
            df = pd.read_csv(string_io)

            # Convert the DataFrame to a list of dictionaries (JSON objects)
            json_output = df.to_dict(orient='records')

            return json_output

        except pd.errors.ParserError as e:
            logger.error(f"CSV parsing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing CSV file: The file is malformed. Details: {e}"
            )
        except UnicodeDecodeError as e:
            logger.error(f"CSV encoding error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error decoding file. Please ensure the file is UTF-8 encoded."
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred during CSV analysis: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {e}"
            )

    async def analyze_xml(self, file: UploadFile = File(...)):
        """
        Analyzes an XML file and returns its content as a JSON array of objects.
        It assumes a simple XML structure where root contains multiple child elements,
        and each child's tags and text are converted to key-value pairs.
        """
        if not file.filename.endswith('.xml'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an XML file."
            )

        try:
            # Read the file content into a bytes buffer
            contents = await file.read()
            bytes_io = BytesIO(contents)

            # Parse the XML data
            tree = ET.parse(bytes_io)
            root = tree.getroot()

            # Convert XML elements to a list of dictionaries
            json_output = []
            for item in root:
                record = {}
                for child in item:
                    record[child.tag] = child.text
                if record:
                    json_output.append(record)

            return json_output

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing XML file: The file is malformed. Details: {e}"
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred during XML analysis: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {e}"
            )
