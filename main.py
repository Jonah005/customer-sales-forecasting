import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np


def validate_data(data):
    """Validate data integrity and enforce correct data types."""
    required_columns = {
        'Customer': str,
        'Date': 'datetime64[ns]',
        'Weekly_Sales': float,
        'Adjusted_Sales': float,
    }
    for column, dtype in required_columns.items():
        if column in data.columns:
            if dtype == 'datetime64[ns]':
                data[column] = pd.to_datetime(data[column], errors='coerce')
            else:
                data[column] = data[column].astype(dtype, errors='ignore')
    data.fillna(0, inplace=True)  # Replace NaNs with 0
    return data


def calculate_accuracy(y_true, y_pred):
    """Calculate RMSE, MAE, and R2."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {"RMSE": rmse, "MAE": mae, "R2": r2}


def calculate_accuracy_and_precision(metrics, average_sales):
    """Calculate accuracy and precision based on RMSE, MAE, and R2."""
    results = []
    for index, row in metrics.iterrows():
        rmse = row['RMSE']
        mae = row['MAE']
        customer = row['Customer']

        # Calculate Accuracy
        accuracy = max(0, (1 - (rmse / average_sales)) * 100)

        # Calculate Precision
        precision = max(0, (1 - (mae / average_sales)) * 100)

        results.append({
            "Customer": customer,
            "Accuracy (%)": round(accuracy, 2),
            "Precision (%)": round(precision, 2)
        })
    return pd.DataFrame(results)


def save_graphs_to_pdf(customers, sales_data, pdf_file, title_suffix, x_label):
    """Save graphs to PDF for monthly sales and predictions."""
    with PdfPages(pdf_file) as pdf:
        for customer in customers:
            customer_data = sales_data[sales_data['Customer'] == customer]
            if customer_data.empty:
                continue

            plt.figure(figsize=(10, 6))
            plt.plot(
                customer_data['Date'],
                customer_data['Adjusted_Sales'],
                label='Actual Sales',
                marker='o',
                linewidth=2,
            )
            plt.plot(
                customer_data['Date'],
                customer_data['Predicted_Sales'],
                label='Predicted Sales',
                marker='x',
                linestyle='--',
                linewidth=2,
            )
            plt.title(f"Sales Forecast for {customer} ({title_suffix})", fontsize=14, fontweight="bold")
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel("Sales", fontsize=12)
            plt.grid(True, linestyle="--", alpha=0.7)
            plt.legend(fontsize=12)
            plt.xticks(rotation=45)
            pdf.savefig()
            plt.close()
    print(f"Graphs saved to {pdf_file}")


def evaluate_forecast_accuracy(sales_data):
    """Evaluate forecast accuracy and return a DataFrame of results."""
    accuracy_results = []

    for customer in sales_data['Customer'].unique():
        customer_data = sales_data[sales_data['Customer'] == customer]

        # Check if the required columns exist
        if 'Adjusted_Sales' in customer_data.columns and 'Predicted_Sales' in customer_data.columns:
            # Drop rows with NaN values
            customer_data = customer_data.dropna(subset=['Adjusted_Sales', 'Predicted_Sales'])
            y_true = customer_data['Adjusted_Sales']
            y_pred = customer_data['Predicted_Sales']

            # Skip if no valid data remains after dropping NaNs
            if y_true.empty or y_pred.empty:
                print(f"Skipping customer {customer} due to insufficient data.")
                continue

            metrics = calculate_accuracy(y_true, y_pred)
            metrics['Customer'] = customer
            accuracy_results.append(metrics)
        else:
            print(f"Missing required columns for customer {customer}")

    # Convert results to a DataFrame
    accuracy_df = pd.DataFrame(accuracy_results, columns=['Customer', 'RMSE', 'MAE', 'R2'])

    # Debugging output
    print("Metrics DataFrame:")
    print(accuracy_df.head())

    # Assume average sales = 70,000 (for simplicity). Update this if real data is available.
    average_sales = 70000

    # Calculate accuracy and precision
    accuracy_and_precision_df = calculate_accuracy_and_precision(accuracy_df, average_sales)

    # Debugging output
    print("\nAccuracy and Precision DataFrame:")
    print(accuracy_and_precision_df.head())

    # Calculate overall metrics
    total_customers = len(accuracy_and_precision_df)
    overall_accuracy = accuracy_and_precision_df['Accuracy (%)'].mean()
    overall_precision = accuracy_and_precision_df['Precision (%)'].mean()

    print(f"\nOverall Accuracy: {overall_accuracy:.2f}%")
    print(f"Overall Precision: {overall_precision:.2f}%")

    return accuracy_and_precision_df


def process_sales_data(file_path):
    """Process sales data, forecast, and save monthly results."""
    # Load and validate data
    data = pd.read_excel(file_path)
    data = validate_data(data)

    # Add Month column for monthly aggregation
    data['Month'] = data['Date'].dt.to_period('M').dt.to_timestamp()

    # Aggregate to monthly sales
    monthly_sales = data.groupby(['Customer', 'Month']).agg({
        'Adjusted_Sales': 'sum'
    }).reset_index()
    monthly_sales.rename(columns={'Month': 'Date'}, inplace=True)
    monthly_sales['Predicted_Sales'] = 0  # Initialize with zeros

    # Initialize Prophet and forecast
    all_monthly_forecasts = []
    for customer in monthly_sales['Customer'].unique():
        customer_data = monthly_sales[monthly_sales['Customer'] == customer][['Date', 'Adjusted_Sales']]
        customer_data.rename(columns={'Date': 'ds', 'Adjusted_Sales': 'y'}, inplace=True)

        model = Prophet()
        model.fit(customer_data)

        future = model.make_future_dataframe(periods=12, freq='M')
        forecast = model.predict(future)

        # Merge forecasted data
        forecast = forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Predicted_Sales'})
        forecast['Customer'] = customer
        all_monthly_forecasts.append(forecast)

    # Combine all forecasts
    forecast_df = pd.concat(all_monthly_forecasts, ignore_index=True)

    # Merge forecast back into monthly_sales
    monthly_sales = pd.merge(monthly_sales, forecast_df, on=['Customer', 'Date'], how='outer', suffixes=('', '_forecast'))

    # Ensure no duplicate Predicted_Sales columns exist
    if 'Predicted_Sales_forecast' in monthly_sales.columns:
        monthly_sales['Predicted_Sales'] = monthly_sales['Predicted_Sales_forecast']
        monthly_sales.drop(columns=['Predicted_Sales_forecast'], inplace=True)

    # Save graphs
    save_graphs_to_pdf(
        customers=monthly_sales['Customer'].unique(),
        sales_data=monthly_sales,
        pdf_file="outputs/Customer_Monthly_Forecasts.pdf",
        title_suffix="Monthly Sales",
        x_label="Months",
    )

    return monthly_sales


# File path
file_path = 'data/Sales_Forecast_Analysis.xlsx'

# Process sales and evaluate accuracy and precision
monthly_sales = process_sales_data(file_path)
accuracy_and_precision_df = evaluate_forecast_accuracy(monthly_sales)

# Save the results to a CSV file
accuracy_and_precision_df.to_csv("outputs/Forecast_Accuracy_Precision.csv", index=False)

print("\nFinal Results Saved to 'Forecast_Accuracy_Precision.csv'")
