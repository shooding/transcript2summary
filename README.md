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
    JIGASI_TRANSCRIPT_FOLDER=/tmp/transcripts
    OLLAMA_HOST=<your_ollama_host>
    MINIO_SERVER=<your_minio_server>
    MINIO_ACCESS_KEY=<your_minio_access_key>
    MINIO_SECRET_KEY=<your_minio_secret_key>
    MINIO_BUCKET_NAME=<your_minio_bucket_name>
    SUMMARY_PATH=<your_transcript_path>
    ```

3. **Build the Docker image**:
    ```sh
    docker build -t mytag .
    ```

## Usage

To process a transcript, pass the directory containing the JSON file as an argument when running the Docker container. Ensure the directory contains exactly one JSON file.

```sh
docker run -d --network host --platform=linux/amd64 --env-file .env -v /tmp/transcripts:/tmp/transcripts mytag
```

