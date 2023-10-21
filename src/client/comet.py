import os
from comet_ml import Experiment
from dotenv import load_dotenv
load_dotenv()


def start_experiment(project_name = ""):
    project_name = project_name or os.getenv('PROJECT_NAME')
    return Experiment(
        api_key=os.getenv('COMET_API_KEY'),
        project_name=project_name,
    )
