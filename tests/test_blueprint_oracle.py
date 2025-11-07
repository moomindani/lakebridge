from pathlib import Path

from databricks.labs.lakebridge.assessments.pipeline import PipelineClass
from databricks.labs.lakebridge.assessments.profiler import Profiler
from databricks.labs.lakebridge.connections.database_manager import OracleConnector
from databricks.labs.lakebridge.connections.database_manager import DatabaseManager

pipeline_config_file="../src/databricks/labs/lakebridge/resources/assessments/oracle/pipeline_config.yml"
config=PipelineClass.load_config_from_yaml(pipeline_config_file)
print(config)

profiler = Profiler("oracle", None)
# supported_platforms = profiler.supported_platforms()
# print(supported_platforms)
profiler.profile(pipeline_config=config)
