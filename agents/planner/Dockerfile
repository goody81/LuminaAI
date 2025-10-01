# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY agents/planner/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire agents directory into the container
COPY agents/ /usr/src/app/agents

# Make port 50051 available to the world outside this container
EXPOSE 50051

# Define environment variable
ENV PYTHONPATH /usr/src/app

# Run main.py when the container launches
CMD ["python", "-m", "agents.planner.main"]
