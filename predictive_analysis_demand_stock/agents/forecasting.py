"""
Sales forecasting module.

Provides simple demand forecasting methods based on historical sales data.
"""

import pandas as pd
import numpy as np


class Forecasting:
    """
    Handles demand forecasting based on historical sales.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        date_col: str = "date",
        product_col: str = "product_id",
        sales_col: str = "quantity",
    ) -> None:
        """
        Initialize the forecasting engine.

        Args:
            df: Cleaned sales DataFrame
            date_col: Name of the date column
            product_col: Name of the product identifier column
            sales_col: Name of the sales quantity column
        """
        self.df = df.copy()
        self.date_col = date_col
        self.product_col = product_col
        self.sales_col = sales_col

        self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])

    def calculate_average_demand(self) -> pd.DataFrame:
        """
        Calculate average demand per product.

        Returns:
            DataFrame with average demand per product
        """
        return (
            self.df.groupby(self.product_col)[self.sales_col]
            .mean()
            .reset_index()
            .rename(columns={self.sales_col: "avg_demand"})
        )

    def calculate_seasonality(self, freq: str = "month") -> pd.DataFrame:
        """
        Calculate basic seasonality by time period.

        Args:
            freq: 'month' or 'week'

        Returns:
            DataFrame with average demand by product and period
        """
        if freq == "month":
            self.df["period"] = self.df[self.date_col].dt.month
        elif freq == "week":
            self.df["period"] = self.df[self.date_col].dt.isocalendar().week
        else:
            raise ValueError("freq must be 'month' or 'week'")

        return (
            self.df.groupby([self.product_col, "period"])[self.sales_col]
            .mean()
            .reset_index()
            .rename(columns={self.sales_col: "seasonal_avg_demand"})
        )

    def moving_average_forecast(
        self,
        window: int = 3,
        periods: int = 1,
    ) -> pd.DataFrame:
        """
        Forecast future demand using moving average.

        Args:
            window: Rolling window size
            periods: Number of future periods to forecast

        Returns:
            DataFrame with forecasted demand per product
        """
        forecasts = []

        for product, group in self.df.groupby(self.product_col):
            group = group.sort_values(self.date_col)

            rolling_mean = group[self.sales_col].rolling(window=window).mean().values[-1]

            if np.isnan(rolling_mean):
                rolling_mean = group[self.sales_col].mean()

            for step in range(1, periods + 1):
                forecasts.append(
                    {
                        self.product_col: product,
                        "forecast_period": step,
                        "forecast_demand": round(rolling_mean, 2),
                    }
                )

        return pd.DataFrame(forecasts)

    def trend_forecast(
        self,
        periods: int = 14,
    ) -> pd.DataFrame:
        """
        Forecast future demand using linear regression trend.
        
        Args:
            periods: Number of future periods to forecast
            
        Returns:
            DataFrame with forecasted demand per product
        """
        forecasts = []
        
        for product, group in self.df.groupby(self.product_col):
            group = group.sort_values(self.date_col)
            
            # Prepare data for linear regression
            X = np.arange(len(group)).reshape(-1, 1)
            y = group[self.sales_col].values
            
            # Calculate linear regression manually
            n = len(X)
            X_mean = np.mean(X)
            y_mean = np.mean(y)
            
            # Calculate slope and intercept
            numerator = np.sum((X.flatten() - X_mean) * (y - y_mean))
            denominator = np.sum((X.flatten() - X_mean) ** 2)
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            intercept = y_mean - slope * X_mean
            
            # Generate forecast
            last_index = len(group)
            for step in range(1, periods + 1):
                future_index = last_index + step - 1
                forecast_value = slope * future_index + intercept
                
                # Add some realistic variation
                noise = np.random.normal(0, abs(forecast_value) * 0.1)
                forecast_value = max(0, forecast_value + noise)
                
                forecasts.append({
                    self.product_col: product,
                    "forecast_period": step,
                    "forecast_demand": round(forecast_value, 2),
                })
        
        return pd.DataFrame(forecasts)

    def seasonal_forecast(
        self,
        periods: int = 14,
        seasonal_freq: str = "week",
    ) -> pd.DataFrame:
        """
        Forecast future demand using seasonal patterns.
        
        Args:
            periods: Number of future periods to forecast
            seasonal_freq: 'week' or 'month' for seasonal pattern
            
        Returns:
            DataFrame with forecasted demand per product
        """
        forecasts = []
        
        for product, group in self.df.groupby(self.product_col):
            group = group.sort_values(self.date_col)
            
            # Calculate seasonal patterns
            if seasonal_freq == "week":
                group["seasonal_period"] = group[self.date_col].dt.dayofweek
            else:  # month
                group["seasonal_period"] = group[self.date_col].dt.day
            
            seasonal_avg = group.groupby("seasonal_period")[self.sales_col].mean()
            overall_avg = group[self.sales_col].mean()
            
            # Generate forecast with seasonal pattern
            last_date = group[self.date_col].iloc[-1]
            for step in range(1, periods + 1):
                future_date = last_date + pd.Timedelta(days=step)
                
                if seasonal_freq == "week":
                    seasonal_period = future_date.dayofweek
                else:
                    seasonal_period = future_date.day
                
                # Get seasonal factor
                if seasonal_period in seasonal_avg.index:
                    seasonal_factor = seasonal_avg[seasonal_period] / overall_avg
                else:
                    seasonal_factor = 1.0
                
                # Base forecast with seasonal adjustment
                base_forecast = overall_avg * seasonal_factor
                
                # Add realistic variation
                noise = np.random.normal(0, abs(base_forecast) * 0.15)
                forecast_value = max(0, base_forecast + noise)
                
                forecasts.append({
                    self.product_col: product,
                    "forecast_period": step,
                    "forecast_demand": round(forecast_value, 2),
                })
        
        return pd.DataFrame(forecasts)

    def combined_forecast(
        self,
        periods: int = 14,
        trend_weight: float = 0.4,
        seasonal_weight: float = 0.4,
        noise_weight: float = 0.2,
    ) -> pd.DataFrame:
        """
        Forecast future demand combining trend, seasonal, and noise components.
        
        Args:
            periods: Number of future periods to forecast
            trend_weight: Weight for trend component
            seasonal_weight: Weight for seasonal component
            noise_weight: Weight for random noise
            
        Returns:
            DataFrame with forecasted demand per product
        """
        forecasts = []
        
        for product, group in self.df.groupby(self.product_col):
            group = group.sort_values(self.date_col)
            
            # Calculate trend component
            X = np.arange(len(group)).reshape(-1, 1)
            y = group[self.sales_col].values
            
            # Manual linear regression
            n = len(X)
            X_mean = np.mean(X)
            y_mean = np.mean(y)
            
            numerator = np.sum((X.flatten() - X_mean) * (y - y_mean))
            denominator = np.sum((X.flatten() - X_mean) ** 2)
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            intercept = y_mean - slope * X_mean
            
            # Calculate seasonal component
            group["seasonal_period"] = group[self.date_col].dt.dayofweek
            seasonal_avg = group.groupby("seasonal_period")[self.sales_col].mean()
            overall_avg = group[self.sales_col].mean()
            
            # Generate forecast
            last_index = len(group)
            last_date = group[self.date_col].iloc[-1]
            
            for step in range(1, periods + 1):
                # Trend component
                future_index = last_index + step - 1
                trend_component = slope * future_index + intercept
                
                # Seasonal component
                future_date = last_date + pd.Timedelta(days=step)
                seasonal_period = future_date.dayofweek
                
                if seasonal_period in seasonal_avg.index:
                    seasonal_factor = seasonal_avg[seasonal_period] / overall_avg
                else:
                    seasonal_factor = 1.0
                
                seasonal_component = overall_avg * seasonal_factor
                
                # Noise component
                noise_component = np.random.normal(0, abs(overall_avg) * 0.2)
                
                # Combine components
                combined_forecast = (
                    trend_weight * trend_component +
                    seasonal_weight * seasonal_component +
                    noise_weight * noise_component
                )
                
                # Ensure non-negative
                forecast_value = max(0, combined_forecast)
                
                forecasts.append({
                    self.product_col: product,
                    "forecast_period": step,
                    "forecast_demand": round(forecast_value, 2),
                })
        
        return pd.DataFrame(forecasts)