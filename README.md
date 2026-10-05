# Customer Sales Forecasting

A customer-level sales forecasting project built with **Prophet** and Python.

The project analyzes historical customer sales, aggregates them into monthly time series, trains an individual forecasting model for each customer, and generates 12-month sales forecasts together with automated evaluation reports and visualizations.

## Project Highlights

- Customer-level time-series forecasting
- Monthly sales aggregation
- Separate Prophet model for each customer
- 12-month future forecasting
- Forecast evaluation using RMSE, MAE, and R²
- Custom forecast accuracy and precision scores
- Automated actual-vs-predicted charts
- PDF forecast report generation
- CSV export of customer-level forecast scores

## Dataset

The project uses the Excel workbook:

```text
Sales_Forecast_Analysis.xlsx
```

The main sales data includes fields such as:

- Customer
- Customer Type
- Region
- Date
- Weekly Sales
- Weather Impact
- Holiday Impact
- Competitor Impact
- Adjusted Sales

The workbook also contains supporting sheets for sales summaries and contextual business factors.

## How It Works

```text
Sales Data
    ↓
Data Validation
    ↓
Monthly Aggregation
    ↓
Customer-Level Time Series
    ↓
Prophet Model per Customer
    ↓
12-Month Forecast
    ↓
Forecast Evaluation
    ↓
PDF + CSV Outputs
```

## Forecasting Pipeline

For each customer, the application:

1. Loads and validates the sales data.
2. Converts dates into monthly periods.
3. Aggregates adjusted sales by customer and month.
4. Trains a Prophet forecasting model.
5. Extends the time series by 12 months.
6. Generates predicted monthly sales.
7. Compares predictions with available historical sales.
8. Calculates forecast evaluation metrics.
9. Produces forecast charts and output reports.

## Evaluation

The project calculates:

- **RMSE** — Root Mean Squared Error
- **MAE** — Mean Absolute Error
- **R²** — coefficient of determination

It also produces custom forecast quality scores derived from RMSE and MAE relative to an assumed average sales baseline.

Across the current saved results, the average custom scores are approximately:

- **Forecast Accuracy Score:** 91.62%
- **Forecast Precision Score:** 93.53%

These are project-specific normalized forecast scores, not classification accuracy or precision metrics.

## Outputs

The project generates:

```text
Customer_Monthly_Forecasts.pdf
Forecast_Accuracy_Precision.csv
```

### Customer_Monthly_Forecasts.pdf

Contains one forecast chart per customer showing:

- historical actual sales
- model predictions
- future forecast values

### Forecast_Accuracy_Precision.csv

Contains the calculated customer-level forecast accuracy and precision scores.

## Project Structure

```text
customer-sales-forecasting/
├── data/
│   └── Sales_Forecast_Analysis.xlsx
├── outputs/
│   ├── Customer_Monthly_Forecasts.pdf
│   └── Forecast_Accuracy_Precision.csv
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Running the Project

Make sure the input workbook is available at the path expected by `main.py`.

Then run:

```powershell
python main.py
```

The script will generate the customer forecast PDF and evaluation CSV.

## Tech Stack

- Python
- Pandas
- Prophet
- NumPy
- Scikit-learn
- Matplotlib
- OpenPyXL

## Notes

This project was developed as a time-series forecasting and customer-trend analysis exercise. It demonstrates customer-level forecasting, model evaluation, automated visualization, and reporting using real tabular business-style data.
