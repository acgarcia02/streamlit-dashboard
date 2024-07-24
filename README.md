# ELISA Test Dashboard

The ELISA Test Dashboard is a Streamlit app designed to provide visualization for ELISA test data. It provides various chart options to visualize the relationships between different variables in the dataset.

## Dependencies

This program requires `python 3.x`, `streamlit`, `pandas`, and `plotly.express`. Make sure you have the dependencies installed before running the application.

You can install the required dependencies using the following command:
`pip install streamlit pandas plotly`

## How to run the app
1. Navigate to the project directory. 
2. Run the Streamlit app using the following command: `streamlit run dashboard.py`
3. The app will open in your default web browser.
4. Upload a CSV file containing your ELISA test data.
5. Once the data is loaded, you will see various chart options in the sidebar, the metrics, and the pre-defined charts with default values.

## Features
- **File Upload:** Upload your ELISA test data in CSV format to visualize and analyze.
- **Pre-defined Charts:** Explore the provided pre-defined charts. Choose parameters, group data, and color points to customize the visualization. Select a date range to focus on specific time periods within the data.
- **Custom Charts:** Create your own custom chart by selecting the chart type, x-axis, y-axis, data grouping, and color coding. This allows having more visualization and performing deeper analysis based on your preferences.
- **Metrics:** View metrics such as the total number of samples, number of unique assays, minimum and maximum GMT values.
