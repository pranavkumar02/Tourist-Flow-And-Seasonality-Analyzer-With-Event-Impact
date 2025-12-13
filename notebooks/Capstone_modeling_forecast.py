# Title: Capstone_modeling_forecast

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
import os

# Your confirmed S3 bucket and script location
BUCKET_NAME = 'capstone-data-pace'
S3_SCRIPT_URI = f's3://{BUCKET_NAME}/notebooks/model_forecast_capstone.py'
LOCAL_SCRIPT_NAME = 'model_forecast_capstone.py'
LOCAL_PATH = '.' # Downloads to the current notebook directory

print(f"Downloading {S3_SCRIPT_URI} to {os.path.abspath(LOCAL_PATH)}...")

# Use the SageMaker Session to download the file
sagemaker.Session().download_data(
    path=LOCAL_PATH, 
    bucket=BUCKET_NAME, 
    key_prefix=f'notebooks/{LOCAL_SCRIPT_NAME}'
)

# Verify the file is now local
if os.path.exists(LOCAL_SCRIPT_NAME):
    print(f"✅ Download successful! The script is now available locally at: ./{LOCAL_SCRIPT_NAME}")
else:
    print("❌ Download failed. Please check the S3 URI and your permissions.")
    
# Set the SCRIPT_NAME to the local file path
SCRIPT_NAME = f'./{LOCAL_SCRIPT_NAME}'

from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
import sagemaker
from sagemaker import image_uris

# Ensure SCRIPT_NAME is defined from the previous step
SCRIPT_NAME = './model_forecast_capstone.py'

INSTANCE_TYPE = 'ml.t3.2xlarge'

# ========================================================================
# --- 1. Define Environment Configuration (ALL REQUIRED VARIABLES) ---
# ========================================================================
# Your confirmed S3 bucket
BUCKET_NAME = 'capstone-data-pace' 
S3_INPUT_DATA_PATH = f's3://{BUCKET_NAME}/processed/final_dataset.csv' 
S3_OUTPUT_PATH = f's3://{BUCKET_NAME}/forecast_output/' 

# Define session variables
ROLE = sagemaker.get_execution_role() 
REGION = sagemaker.Session().boto_region_name

# Retrieve the official Scikit-learn image URI
image_uri = image_uris.retrieve(
    framework="sklearn",
    region=REGION,
    instance_type=INSTANCE_TYPE,
    version="1.2-1",  
    py_version="py3", # Supported generic Python version
    image_scope="training"
)

print(f"Retrieved Image URI: {image_uri}")

# --- 3. Create Processor and Run Job (FIXED) ---
print(f"\nCreating ScriptProcessor with instance type: {INSTANCE_TYPE}")

# ⭐ FIX: Explicitly setting the 'command' argument to ['python3'] 
# resolves the 'NoneType' error by defining the container's entrypoint.
processor = ScriptProcessor(
    image_uri=image_uri, 
    role=ROLE,
    instance_count=1,
    instance_type=INSTANCE_TYPE,
    command=['python3'] # <--- THE FIX
)

print("\nStarting SageMaker Processing Job for 4-Year Forecasting...")
print(f"Using local script path: {SCRIPT_NAME}")

# Launch the processing job
job = processor.run(
    code=SCRIPT_NAME, 
    inputs=[
        ProcessingInput(
            source=S3_INPUT_DATA_PATH,
            # The S3 file is mapped to the *directory* /opt/ml/processing/input/data
            destination='/opt/ml/processing/input/data' 
        )
    ],
    outputs=[
        ProcessingOutput(
            # The script writes to the *directory* /opt/ml/processing/output
            source='/opt/ml/processing/output', 
            destination=S3_OUTPUT_PATH 
        )
    ],
    wait=False, 
    logs=True,

)

job_name = processor.latest_job.job_name
print(f"\nProcessing job launched successfully! Job Name: {job_name}")
print("---")
print("\nNEXT STEP: Run 'processor.latest_job.wait(logs=True)' in a new cell to monitor the job's completion and view logs.")

processor.latest_job.wait(logs=True)