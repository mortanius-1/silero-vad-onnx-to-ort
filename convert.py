import os
import requests
import pathlib
import logging
import shutil
from onnxruntime.tools.convert_onnx_models_to_ort import convert_onnx_models_to_ort, OptimizationStyle


github_token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {github_token}"} if github_token else {}

def get_tag(request_url):
    try:
        api_response = requests.get(request_url, headers=headers)
        api_response.raise_for_status()
        logging.info(api_response.text)

        return api_response.json()['tag_name']
    except Exception as e:
        logging.error(f"Failed to make request: {e}")

    return None

silero_url = 'https://api.github.com/repos/snakers4/silero-vad/releases/latest'
silero_tag = get_tag(silero_url)
logging.info(f'Latest upstream Silero tag detected: {silero_tag}')

ort_url = 'https://api.github.com/repos/mortanius-1/silero-vad-onnx-to-ort/releases/latest'
ort_tag = get_tag(ort_url)
ort_base_tag = ort_tag.replace('-ort', '') if ort_tag is not None else None
logging.info(f'Latest upstream ONNX-to-ORT tag detected: {ort_base_tag}')

# Get GITHUB_OUTPUT
github_output = os.environ.get('GITHUB_OUTPUT')

if ort_base_tag is not None and ort_base_tag == silero_tag:
    logging.info("Versions match: No new updates detected. Exiting...")
    if github_output:
        with open(github_output, 'a') as f:
            f.write('run_release=false\n')
    exit(0)

# Build the final download URL dynamically using the tag
download_url = f"https://github.com/snakers4/silero-vad/raw/refs/tags/{silero_tag}/src/silero_vad/data/silero_vad.onnx"
logging.info(f'Downloading model from: {download_url}')

# Stream the file down
file_response = requests.get(download_url)
file_response.raise_for_status()
model_source = pathlib.Path("silero_vad.onnx")

if model_source:
    with open('silero_vad.onnx', 'wb') as f:
        f.write(file_response.content)
else:
    logging.error(f"Model not found: {model_source}")
    exit(1)


logging.info(f"Starting conversion for: {model_source}")

try:
    convert_onnx_models_to_ort(
        model_path_or_dir=model_source,
        enable_type_reduction=True,
        target_platform="arm",
        output_dir=model_source.parent,
        optimization_styles=[OptimizationStyle.Runtime],
        save_optimized_onnx_model=True
    )
    logging.info("Conversion completed")

    model_output = pathlib.Path('silero_vad.with_runtime_opt.ort')

    if model_output.exists():
        shutil.copy(model_output, 'silero_vad.ort')

except Exception as e:
    logging.error(f"Failed to convert model: {e}")

title = f"Silero VAD {silero_tag} ORT Build"

if github_output:
    with open(github_output, 'a') as f:
        f.write('run_release=true\n')
        f.write(f'tag={silero_tag}-ort\n')
        f.write(f'title={title}\n')
else:
    print(f"[Local] GITHUB_OUTPUT not found. Targets: tag={silero_tag}-ort, title={title}")
