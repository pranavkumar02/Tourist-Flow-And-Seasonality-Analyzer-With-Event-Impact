# Title: Capstone_data_processing

# Set environment variables for sagemaker_studio imports

import os
os.environ['DataZoneProjectId'] = 'an2rli7o9oknmx'
os.environ['DataZoneDomainId'] = 'dzd-3rl11r46ek34rt'
os.environ['DataZoneEnvironmentId'] = '53w3lzg23g4hpl'
os.environ['DataZoneDomainRegion'] = 'us-east-2'

# create both a function and variable for metadata access
_resource_metadata = None

def _get_resource_metadata():
    global _resource_metadata
    if _resource_metadata is None:
        _resource_metadata = {
            "AdditionalMetadata": {
                "DataZoneProjectId": "an2rli7o9oknmx",
                "DataZoneDomainId": "dzd-3rl11r46ek34rt",
                "DataZoneEnvironmentId": "53w3lzg23g4hpl",
                "DataZoneDomainRegion": "us-east-2",
            }
        }
    return _resource_metadata
metadata = _get_resource_metadata()

"""
Logging Configuration

Purpose:
--------
This sets up the logging framework for code executed in the user namespace.
"""

from typing import Optional


def _set_logging(log_dir: str, log_file: str, log_name: Optional[str] = None):
    import os
    import logging
    from logging.handlers import RotatingFileHandler

    level = logging.INFO
    max_bytes = 5 * 1024 * 1024
    backup_count = 5

    # fallback to /tmp dir on access, helpful for local dev setup
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        log_dir = "/tmp/kernels/"

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger() if not log_name else logging.getLogger(log_name)
    logger.handlers = []
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Rotating file handler
    fh = RotatingFileHandler(filename=log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info(f"Logging initialized for {log_name}.")


_set_logging("/var/log/computeEnvironments/kernel/", "kernel.log")
_set_logging("/var/log/studio/data-notebook-kernel-server/", "metrics.log", "metrics")

import logging
from sagemaker_studio import ClientConfig, sqlutils, sparkutils, dataframeutils

logger = logging.getLogger(__name__)
logger.info("Initializing sparkutils")
spark = sparkutils.init()
logger.info("Finished initializing sparkutils")

def _reset_os_path():
    """
    Reset the process's working directory to handle mount timing issues.
    
    This function resolves a race condition where the Python process starts
    before the filesystem mount is complete, causing the process to reference
    old mount paths and inodes. By explicitly changing to the mounted directory
    (/home/sagemaker-user), we ensure the process uses the correct, up-to-date
    mount point.
    
    The function logs stat information (device ID and inode) before and after
    the directory change to verify that the working directory is properly
    updated to reference the new mount.
    
    Note:
        This is executed at module import time to ensure the fix is applied
        as early as possible in the kernel initialization process.
    """
    try:
        import os
        import logging

        logger = logging.getLogger(__name__)
        logger.info("---------Before------")
        logger.info("CWD: %s", os.getcwd())
        logger.info("stat('.'): %s %s", os.stat('.').st_dev, os.stat('.').st_ino)
        logger.info("stat('/home/sagemaker-user'): %s %s", os.stat('/home/sagemaker-user').st_dev, os.stat('/home/sagemaker-user').st_ino)

        os.chdir("/home/sagemaker-user")

        logger.info("---------After------")
        logger.info("CWD: %s", os.getcwd())
        logger.info("stat('.'): %s %s", os.stat('.').st_dev, os.stat('.').st_ino)
        logger.info("stat('/home/sagemaker-user'): %s %s", os.stat('/home/sagemaker-user').st_dev, os.stat('/home/sagemaker-user').st_ino)
    except Exception as e:
        logger.exception(f"Failed to reset working directory: {e}")

_reset_os_path()

import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
import os

session = sagemaker.Session()
region = session.boto_region_name

# Using the role successfully retrieved earlier
ROLE = sagemaker.get_execution_role() 
print(f"SageMaker SDK Version: {sagemaker.__version__}")
print(f"Using execution role: {ROLE}")

# --- 2. S3 PATHS ---
S3_CODE_FOLDER = 's3://capstone-data-pace/notebooks/' 
S3_INPUT_DATA_FOLDER = 's3://capstone-data-pace/Query builder files/' 
S3_OUTPUT_PATH = 's3://capstone-data-pace/processed/'

# --- 3. DOCKER IMAGE RETRIEVAL ---

# Using 'retrieve' to get the correct regional image URI
image_uri = sagemaker.image_uris.retrieve(
    framework='sklearn', 
    region=region, 
    version='1.2-1', 
    py_version='py3'
)
print(f"Dynamically retrieved Image URI: {image_uri}")

# --- 4. CREATE PROCESSOR AND RUN JOB (MANUAL DEPENDENCY INSTALL) ---

INSTANCE_TYPE = 'ml.t3.medium' 
print(f"\nCreating ScriptProcessor with instance type: {INSTANCE_TYPE}")


# 1. pip install -r installs requirements from the mounted folder.
# 2. && python3 runs the main script.
SCRIPT_INSIDE_CONTAINER_PATH = '/opt/ml/processing/input/code/nps_clean_merge.py'
REQUIREMENTS_PATH = '/opt/ml/processing/input/code/requirements.txt'

# The command will now be executed by a shell interpreter (sh)
EXECUTION_COMMAND = [
    'sh', 
    '-c', 
    f'pip install -r {REQUIREMENTS_PATH} && python3 {SCRIPT_INSIDE_CONTAINER_PATH}'
]

processor = ScriptProcessor(
    image_uri=image_uri, 
    command=EXECUTION_COMMAND, 
    role=ROLE,
    instance_count=1,
    instance_type=INSTANCE_TYPE   
)

print("\nStarting SageMaker Processing Job...")

# Launch the processing job
job = processor.run(
    # Use the S3 FOLDER path to download BOTH the script and requirements.txt.
    code=S3_CODE_FOLDER, 
    
    inputs=[
        # Data Input (Mounted to /opt/ml/processing/input/data)
        ProcessingInput(
            source=S3_INPUT_DATA_FOLDER,
            destination='/opt/ml/processing/input/data' 
        )
    ],
    outputs=[
        ProcessingOutput(
            source='/opt/ml/processing/output',
            destination=S3_OUTPUT_PATH
        )
    ],
    wait=False, 
    logs=True
)

job_name = processor.latest_job.job_name
print(f"\nProcessing job launched successfully!")
print(f"Job Name: {job_name}")
print("---")
print("ACTION REQUIRED: Run 'processor.latest_job.wait(logs=True)' in a new cell to monitor completion.")

processor.latest_job.wait(logs=True)

import sagemaker
print(f"SageMaker SDK Version: {sagemaker.__version__}")