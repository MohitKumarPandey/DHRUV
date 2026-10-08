FROM python:3.11-slim

WORKDIR /app

# System dependencies for geospatial libraries (geopandas, rasterio, postgis etc)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker/ ./worker/

# Compile proto for gRPC stubs (dhruv_pb2.py + dhruv_pb2_grpc.py)
RUN python -m grpc_tools.protoc \
    -I./worker \
    --python_out=./worker \
    --grpc_python_out=./worker \
    ./worker/dhruv.proto

# Expose gRPC port
EXPOSE 50051

CMD ["python", "-m", "worker.main"]
