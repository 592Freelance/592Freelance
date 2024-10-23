import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from io import StringIO
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Function to fetch and process historical sales data
def get_historical_sales_data():
    # Simulating data fetch from an open agriculture database
    # In reality, you would replace this with an API call or database query
    url = "https://example.com/api/historical_sales_data"
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Function to fetch and process market demand data
def get_market_demand_data():
    # Simulating data fetch
    url = "https://example.com/api/market_demand_data"
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Function to fetch and process supply data
def get_supply_data():
    # Simulating data fetch
    url = "https://example.com/api/supply_data"
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Function to determine season based on date
def get_season(date):
    month = date.month
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Autumn'
    else:
        return 'Winter'

# Function to fetch and process weather data
def get_weather_data():
    # Simulating data fetch
    url = "https://example.com/api/weather_data"
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Function to fetch and process economic data
def get_economic_data():
    # Simulating data fetch
    url = "https://example.com/api/economic_data"
    response = requests.get(url)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Main function to create the agriculture platform
def create_agriculture_platform():
    # Fetch all required data
    sales_data = get_historical_sales_data()
    demand_data = get_market_demand_data()
    supply_data = get_supply_data()
    weather_data = get_weather_data()
    economic_data = get_economic_data()

    # Merge all data on date
    merged_data = sales_data.merge(demand_data, on='date', suffixes=('_sales', '_demand'))
    merged_data = merged_data.merge(supply_data, on='date')
    merged_data = merged_data.merge(weather_data, on='date')
    merged_data = merged_data.merge(economic_data, on='date')

    # Add season information
    merged_data['season'] = merged_data['date'].apply(get_season)

    # Calculate some basic metrics
    merged_data['supply_demand_ratio'] = merged_data['quantity_supplied'] / merged_data['quantity_demanded']
    merged_data['price_change'] = merged_data.groupby('product_name')['price'].pct_change()

    return merged_data

# Create the platform

agriculture_platform = create_agriculture_platform()

# Print some sample data
print(agriculture_platform.head())
# You can now use this DataFrame for further analysis, visualization, or as input to machine learning models

# Demand forecasting function
# Import necessary libraries


def predict_future_demand(agriculture_platform, forecast_period='week'):
    # Prepare the data for Prophet
    demand_data = agriculture_platform[['date', 'product_name', 'quantity_demanded']]
    demand_data = demand_data.rename(columns={'date': 'ds', 'quantity_demanded': 'y'})

    # Initialize dictionary to store predictions
    predictions = {}

    # Group data by product
    for product in demand_data['product_name'].unique():
        product_data = demand_data[demand_data['product_name'] == product][['ds', 'y']]
        
        # Initialize and fit the Prophet model
        model = Prophet()
        model.fit(product_data)

        # Create future dataframe for predictions
        if forecast_period == 'week':
            future_dates = model.make_future_dataframe(periods=7)
        elif forecast_period == 'month':
            future_dates = model.make_future_dataframe(periods=30)
        elif forecast_period == 'season':
            future_dates = model.make_future_dataframe(periods=90)
        else:
            raise ValueError("Invalid forecast period. Choose 'week', 'month', or 'season'.")

        # Make predictions
        forecast = model.predict(future_dates)
        
        # Store predictions
        predictions[product] = forecast[['ds', 'yhat']].tail(len(future_dates) - len(product_data))

    return predictions

# Predict demand for the upcoming week
weekly_demand_forecast = predict_future_demand(agriculture_platform, forecast_period='week')

# Print predicted demand for each product
for product, forecast in weekly_demand_forecast.items():
    print(f"\nPredicted demand for {product} in the upcoming week:")
    print(forecast)

# You can also predict for a month or season by changing the forecast_period parameter
# monthly_demand_forecast = predict_future_demand(agriculture_platform, forecast_period='month')
# seasonal_demand_forecast = predict_future_demand(agriculture_platform, forecast_period='season')

# Dynamic pricing function
def dynamic_pricing(agriculture_platform, product_name):
    # Filter data for the specific product
    product_data = agriculture_platform[agriculture_platform['product_name'] == product_name]

    # Prepare features
    features = ['supply', 'demand', 'month']  # Assuming these columns exist
    X = product_data[features]
    y = product_data['price']

    # One-hot encode the 'month' feature
    X = pd.get_dummies(X, columns=['month'], prefix='month')

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train the model
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    # Function to predict price
    def predict_price(supply, demand, month):
        # Create a DataFrame with the input
        input_data = pd.DataFrame([[supply, demand, month]], columns=['supply', 'demand', 'month'])
        
        # One-hot encode the month
        input_data = pd.get_dummies(input_data, columns=['month'], prefix='month')
        
        # Ensure all columns from training are present
        for col in X.columns:
            if col not in input_data.columns:
                input_data[col] = 0

        # Reorder columns to match training data
        input_data = input_data[X.columns]

        # Scale the input
        input_scaled = scaler.transform(input_data)

        # Predict and return the price
        return model.predict(input_scaled)[0]

    return predict_price

# Example usage
predict_price = dynamic_pricing(agriculture_platform, 'tomatoes')

# Get the current supply, demand, and month (you need to implement this based on your data structure)
current_supply = 1000  # example value
current_demand = 1200  # example value
current_month = 6  # June

# Predict the optimal price
optimal_price = predict_price(current_supply, current_demand, current_month)

print(f"The optimal price for {product_name} is: ${optimal_price:.2f}")

# You can now use this function to dynamically adjust prices based on current supply, demand, and seasonality

def real_time_pricing_system(agriculture_platform, product_name, predict_price):
    # Fetch the latest supply and demand data
    current_supply = agriculture_platform.get_current_supply(product_name)
    current_demand = agriculture_platform.get_current_demand(product_name)
    
    # Get the current month
    current_month = datetime.now().month
    
    # Fetch the latest demand forecast
    forecasted_demand = agriculture_platform.get_demand_forecast(product_name)
    
    # Calculate the base price using the dynamic pricing model
    base_price = predict_price(current_supply, current_demand, current_month)
    
    # Adjust price based on supply and demand
    if current_supply > current_demand:
        # Lower prices to incentivize buyers
        adjustment_factor = 0.95  # 5% decrease
    elif current_demand > current_supply:
        # Increase prices due to scarcity
        adjustment_factor = 1.05  # 5% increase
    else:
        adjustment_factor = 1.0  # No change
    
    # Apply seasonal adjustments if needed
    seasonal_factor = agriculture_platform.get_seasonal_factor(product_name, current_month)
    
    # Calculate the final price
    final_price = base_price * adjustment_factor * seasonal_factor
    
    # Round the price to two decimal places
    final_price = round(final_price, 2)
    
    # Update the price on the platform
    agriculture_platform.update_product_price(product_name, final_price)
    
    print(f"Updated price for {product_name}: ${final_price:.2f}")
    print(f"Current supply: {current_supply}, Current demand: {current_demand}")
    print(f"Forecasted demand: {forecasted_demand}")
    
    return final_price

# Example usage
product_name = 'tomatoes'
updated_price = real_time_pricing_system(agriculture_platform, product_name, predict_price)

# You can schedule this function to run periodically (e.g., hourly) to keep prices updated
# For example, using a task scheduler like Celery:
@shared_task
def update_prices_task():
    products = agriculture_platform.get_all_products()
    for product in products:
        real_time_pricing_system(agriculture_platform, product.name, predict_price)

# Schedule the task to run every hour
update_prices_task.apply_async(countdown=3600)

