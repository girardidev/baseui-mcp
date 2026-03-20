FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py .
COPY update_components.py .
COPY components_index.json .
COPY components/ components/

CMD ["python", "mcp_server.py"]
