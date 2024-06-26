# EnerVision

This project aims to predict solar panel energy production based on various environmental factors. It consists of two main parts: a client application built with Next.js and a server-side application developed using FastAPI. Both applications are containerized using Docker for easy deployment and scalability.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Solar Panel Energy Prediction system leverages machine learning models to forecast solar panel energy output. This tool is essential for solar farm operators and renewable energy enthusiasts looking to optimize their energy generation strategies.

### Client (Next.js)

The client application provides a user-friendly interface for interacting with the prediction model. Users can input current weather conditions and receive predictions on solar panel energy production.

### Server (FastAPI)

The server handles data processing, model inference, and serves API endpoints for the client application. It also manages database interactions for storing and retrieving historical data.

## Getting Started

To get started with the project, ensure you have Docker installed on your machine. Then, clone this repository and navigate into the project directory.

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Open a terminal and navigate to the root directory of the project.
2. Run `docker-compose up --build` to build and start the containers. This command will automatically pull the necessary images if they are not already present on your machine.

## Running the Application

Once the containers are up and running, you can access the client application through your browser at `http://localhost:3000`.

### Client

Navigate to `http://localhost:3000` to interact with the client application.

### Server

The server exposes several API endpoints for fetching predictions and managing data. Refer to the `/docs` endpoint (`http://localhost:8080/docs`) for detailed API documentation generated by FastAPI.

## Contributing

We welcome contributions from the community Please feel free to submit a pull request or open an issue if you encounter any problems or have suggestions for improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
