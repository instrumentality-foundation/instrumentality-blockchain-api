FROM python:3

# Setting working directory
WORKDIR /blockchain

# Expose the API port
EXPOSE 9000

# Copy requirements
COPY requirements.txt ./

# Installing dependencies
RUN pip install -U -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the project
COPY . .

# Starting WSGI server
CMD ["gunicorn", "-w", "4", "app:app", "--bind", "0.0.0.0:9000"]