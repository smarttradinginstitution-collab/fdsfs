# app/Router/file_analysis.py

from fastapi import APIRouter, status
from app.Controllers.file_analysis_controller import FileAnalysisController

# Instantiate the controller
file_analyzer = FileAnalysisController()

# Create the router for file analysis
router_file_analysis = APIRouter(
    prefix="/api/v1/analyze",
    tags=["File Analysis"],
    # You might want to add security dependencies here in the future
    # dependencies=[Depends(require_roles(["user"]))],
)

# Define the routes for CSV and XML analysis
# The response_model can be defined more strictly if the output structure is always the same
# For now, we leave it open as the columns can vary.
router_file_analysis.post(
    "/csv",
    summary="Analyze a CSV file",
    description="Upload a CSV file to receive a JSON representation of its data.",
    status_code=status.HTTP_200_OK,
)(file_analyzer.analyze_csv)

router_file_analysis.post(
    "/xml",
    summary="Analyze an XML file",
    description="Upload an XML file to receive a JSON representation of its data.",

    status_code=status.HTTP_200_OK,
)(file_analyzer.analyze_xml)
