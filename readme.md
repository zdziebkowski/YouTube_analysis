# YouTube Analysis Project

A comprehensive analysis of YouTube channel statistics post-collaboration with XTB.

## Introduction

This project aims to analyze the impact of XTB collaboration on YouTube channel performance. By leveraging Python and data analysis libraries, we provide insights into key metrics and trends.

### Key Features
- Data collection from YouTube API
- Data processing and cleaning
- Interactive visualizations with Shiny for Python

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#configuration)

## Installation

### Prerequisites
- Python 3.8 or higher

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/zdziebkowski/YouTube_analysis.git
    cd YouTube_analysis
    ```
2. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Data Collection**:
    ```bash
    python scripts/data_collection.py
    ```
2. **Data Processing**:
    ```bash
    python scripts/data_processing.py
    ```
3. **Running the App**:
    ```bash
   shiny run --reload app.py  
    ```

Visit the interactive analysis [here](https://zdziebkowski.shinyapps.io/youtubeapi/).

## Configuration

- No special configurations needed.
- Ensure your API keys and other sensitive data are securely stored.

For more details, visit the [GitHub repository](https://github.com/zdziebkowski/YouTube_analysis).
