# Transcript Processing with Summary and Upload to MinIO

This project processes meeting transcripts produced by Jigasi json format, generates a summary using the Ollama chat API, and uploads the summary to a MinIO server.

## Prerequisites

- Docker
- Python 3.12
- MinIO server
- Ollama API

## Setup

1. **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create a `.env` file**:
    ```sh
    touch .env
    ```

    Populate the `.env` file with the following variables:
    ```
    OLLAMA_HOST=<your_ollama_host>
    MINIO_SERVER=<your_minio_server>
    MINIO_ACCESS_KEY=<your_minio_access_key>
    MINIO_SECRET_KEY=<your_minio_secret_key>
    MINIO_BUCKET_NAME=<your_minio_bucket_name>
    TRANSCRIPT_PATH=<your_transcript_path>
    ```

3. **Build the Docker image**:
    ```sh
    docker build -t mytag .
    ```

## Usage

To process a transcript, pass the directory containing the JSON file as an argument when running the Docker container. Ensure the directory contains exactly one JSON file.

```sh
docker run --env-file .env -v $(pwd)/transcript_samples:/app/transcript_samples mytag /app/transcript_samples
```

## Setup jigasi

copy `finalize.sh` to `/tmp/script/finalize.sh` and edit `/etc/jitsi/jigasi/sip-communicator.properties`

```sh
# execute one or more scripts when a transcript or recording is saved
org.jitsi.jigasi.transcription.EXECUTE_SCRIPTS=true
org.jitsi.jigasi.transcription.SCRIPTS_TO_EXECUTE_LIST_SEPARATOR=","
org.jitsi.jigasi.transcription.SCRIPTS_TO_EXECUTE_LIST=/tmp/script/finalize.sh
```

This way enables to final script executed. You should change the image tag in `finalize.sh` if needed.

