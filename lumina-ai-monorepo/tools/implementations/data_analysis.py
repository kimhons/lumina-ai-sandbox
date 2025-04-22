"""
Data Analysis Tool for Lumina AI.

This module implements a tool for performing data analysis operations
on structured data, including statistical analysis and visualization.
"""

import json
import logging
import base64
from typing import List, Dict, Any, Optional, Union
import io
import os

from ..base import BaseTool

# Import optional dependencies
try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

class DataAnalysisTool(BaseTool):
    """Tool for performing data analysis operations on structured data."""
    
    # Tool metadata for discovery
    TOOL_METADATA = {
        'categories': ['data', 'analysis', 'visualization']
    }
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the data analysis tool.
        
        Args:
            output_dir: Optional directory to save output files
        """
        # Define parameters schema
        parameters_schema = {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The analysis operation to perform",
                    "enum": [
                        "summary", "describe", "correlation", "histogram", 
                        "scatter_plot", "box_plot", "line_chart", "heatmap",
                        "hypothesis_test", "regression"
                    ]
                },
                "data": {
                    "type": "array",
                    "description": "The data to analyze (array of objects)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to a CSV or JSON file containing the data (alternative to 'data')"
                },
                "columns": {
                    "type": "array",
                    "description": "Columns to include in the analysis (default: all)",
                    "items": {
                        "type": "string"
                    }
                },
                "x_column": {
                    "type": "string",
                    "description": "Column to use for x-axis in plots"
                },
                "y_column": {
                    "type": "string",
                    "description": "Column to use for y-axis in plots"
                },
                "group_by": {
                    "type": "string",
                    "description": "Column to group data by"
                },
                "output_format": {
                    "type": "string",
                    "description": "Format for output (for visualizations)",
                    "enum": ["png", "svg", "pdf", "json"],
                    "default": "png"
                },
                "save_path": {
                    "type": "string",
                    "description": "Path to save output file (for visualizations)"
                },
                "title": {
                    "type": "string",
                    "description": "Title for plots"
                },
                "figsize": {
                    "type": "array",
                    "description": "Figure size as [width, height] in inches",
                    "items": {
                        "type": "number"
                    },
                    "minItems": 2,
                    "maxItems": 2
                },
                "test_type": {
                    "type": "string",
                    "description": "Type of hypothesis test to perform",
                    "enum": ["ttest", "anova", "chi2", "pearson", "spearman"]
                },
                "alpha": {
                    "type": "number",
                    "description": "Significance level for hypothesis tests",
                    "default": 0.05
                }
            },
            "required": ["operation"],
            "oneOf": [
                {"required": ["data"]},
                {"required": ["file_path"]}
            ]
        }
        
        # Initialize base tool
        super().__init__(
            name="data_analysis",
            description="Perform data analysis operations on structured data",
            parameters_schema=parameters_schema,
            required_permissions=["file_system"]
        )
        
        self.output_dir = output_dir
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    
    def _execute_tool(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the data analysis operation.
        
        Args:
            parameters: Dictionary of parameter values
            
        Returns:
            Dictionary containing the analysis results
        """
        if not HAS_DEPENDENCIES:
            return {
                "success": False,
                "error": "Required dependencies not installed: numpy, pandas, matplotlib, seaborn, scipy"
            }
        
        operation = parameters["operation"]
        
        # Load data
        try:
            df = self._load_data(parameters)
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return {
                "success": False,
                "error": f"Error loading data: {e}"
            }
        
        # Filter columns if specified
        columns = parameters.get("columns")
        if columns:
            df = df[columns]
        
        self.logger.info(f"Performing {operation} on data with shape {df.shape}")
        
        try:
            # Dispatch to appropriate operation handler
            if operation == "summary":
                return self._summary(df, parameters)
            elif operation == "describe":
                return self._describe(df, parameters)
            elif operation == "correlation":
                return self._correlation(df, parameters)
            elif operation == "histogram":
                return self._histogram(df, parameters)
            elif operation == "scatter_plot":
                return self._scatter_plot(df, parameters)
            elif operation == "box_plot":
                return self._box_plot(df, parameters)
            elif operation == "line_chart":
                return self._line_chart(df, parameters)
            elif operation == "heatmap":
                return self._heatmap(df, parameters)
            elif operation == "hypothesis_test":
                return self._hypothesis_test(df, parameters)
            elif operation == "regression":
                return self._regression(df, parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported operation: {operation}"
                }
        
        except Exception as e:
            self.logger.error(f"Error performing {operation}: {e}")
            return {
                "success": False,
                "error": f"Error performing {operation}: {e}"
            }
    
    def _load_data(self, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Load data from parameters or file."""
        if "data" in parameters:
            # Load from provided data array
            return pd.DataFrame(parameters["data"])
        
        elif "file_path" in parameters:
            # Load from file
            file_path = parameters["file_path"]
            if file_path.endswith(".csv"):
                return pd.read_csv(file_path)
            elif file_path.endswith(".json"):
                return pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        
        else:
            raise ValueError("Either 'data' or 'file_path' must be provided")
    
    def _save_figure(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Save figure and return result with image data."""
        output_format = parameters.get("output_format", "png")
        save_path = parameters.get("save_path")
        
        # Determine save path
        if save_path:
            if self.output_dir and not os.path.isabs(save_path):
                save_path = os.path.join(self.output_dir, save_path)
        elif self.output_dir:
            # Generate a filename if not provided
            import uuid
            filename = f"analysis_{uuid.uuid4().hex}.{output_format}"
            save_path = os.path.join(self.output_dir, filename)
        
        # Save figure if path is specified
        if save_path:
            plt.savefig(save_path, format=output_format, bbox_inches='tight')
        
        # Capture figure as base64 encoded image
        buf = io.BytesIO()
        plt.savefig(buf, format=output_format, bbox_inches='tight')
        buf.seek(0)
        image_data = base64.b64encode(buf.read()).decode('ascii')
        plt.close()
        
        result = {
            "success": True,
            "image_data": image_data,
            "image_format": output_format
        }
        
        if save_path:
            result["save_path"] = save_path
        
        return result
    
    def _summary(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the data."""
        result = {
            "success": True,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "sample": df.head(5).to_dict(orient='records')
        }
        
        # Add numeric column statistics
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            result["numeric_stats"] = {
                "mean": df[numeric_cols].mean().to_dict(),
                "std": df[numeric_cols].std().to_dict(),
                "min": df[numeric_cols].min().to_dict(),
                "max": df[numeric_cols].max().to_dict()
            }
        
        # Add categorical column statistics
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            result["categorical_stats"] = {
                col: {
                    "unique_values": df[col].nunique(),
                    "top_values": df[col].value_counts().head(5).to_dict()
                } for col in cat_cols
            }
        
        return result
    
    def _describe(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate descriptive statistics."""
        # Get descriptive statistics
        desc = df.describe(include='all').fillna('').to_dict()
        
        # Convert any non-serializable values to strings
        for col, stats in desc.items():
            for stat, value in stats.items():
                if not isinstance(value, (int, float, str, bool, type(None))):
                    desc[col][stat] = str(value)
        
        return {
            "success": True,
            "statistics": desc
        }
    
    def _correlation(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate correlation matrix."""
        # Filter to numeric columns
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            return {
                "success": False,
                "error": "No numeric columns available for correlation analysis"
            }
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr().to_dict()
        
        # Create visualization if requested
        output_format = parameters.get("output_format")
        if output_format and output_format != "json":
            plt.figure(figsize=parameters.get("figsize", (10, 8)))
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
            
            if "title" in parameters:
                plt.title(parameters["title"])
            else:
                plt.title("Correlation Matrix")
            
            # Save and return figure
            result = self._save_figure(parameters)
            result["correlation_matrix"] = corr_matrix
            return result
        
        return {
            "success": True,
            "correlation_matrix": corr_matrix
        }
    
    def _histogram(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create histogram for specified columns."""
        columns = parameters.get("columns")
        if not columns:
            # Use numeric columns if not specified
            columns = df.select_dtypes(include=['number']).columns.tolist()
            if not columns:
                return {
                    "success": False,
                    "error": "No numeric columns available for histogram"
                }
        
        # Create figure
        n_cols = len(columns)
        figsize = parameters.get("figsize", (5 * min(n_cols, 3), 4 * ((n_cols + 2) // 3)))
        fig, axes = plt.subplots(nrows=((n_cols + 2) // 3), ncols=min(n_cols, 3), figsize=figsize)
        
        # Handle single subplot case
        if n_cols == 1:
            axes = [axes]
        
        # Flatten axes array for easy iteration
        if n_cols > 1:
            axes = axes.flatten()
        
        # Create histograms
        for i, col in enumerate(columns):
            if i < len(axes):
                if col in df.columns:
                    sns.histplot(df[col], kde=True, ax=axes[i])
                    axes[i].set_title(f"Distribution of {col}")
                    axes[i].set_xlabel(col)
                    axes[i].set_ylabel("Frequency")
        
        # Set overall title if provided
        if "title" in parameters:
            fig.suptitle(parameters["title"], fontsize=16)
        
        plt.tight_layout()
        
        # Save and return figure
        return self._save_figure(parameters)
    
    def _scatter_plot(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create scatter plot for two columns."""
        x_column = parameters.get("x_column")
        y_column = parameters.get("y_column")
        
        if not x_column or not y_column:
            return {
                "success": False,
                "error": "Both x_column and y_column must be specified for scatter plot"
            }
        
        if x_column not in df.columns or y_column not in df.columns:
            return {
                "success": False,
                "error": f"Columns not found: {x_column if x_column not in df.columns else y_column}"
            }
        
        # Create figure
        plt.figure(figsize=parameters.get("figsize", (10, 6)))
        
        # Create scatter plot
        group_by = parameters.get("group_by")
        if group_by and group_by in df.columns:
            # Grouped scatter plot
            for name, group in df.groupby(group_by):
                plt.scatter(group[x_column], group[y_column], label=str(name), alpha=0.7)
            plt.legend(title=group_by)
        else:
            # Simple scatter plot
            plt.scatter(df[x_column], df[y_column], alpha=0.7)
        
        # Add regression line if requested
        if parameters.get("add_regression_line", False):
            x = df[x_column].values
            y = df[y_column].values
            mask = ~(np.isnan(x) | np.isnan(y))
            if np.sum(mask) > 1:  # Need at least 2 points for regression
                x = x[mask]
                y = y[mask]
                m, b = np.polyfit(x, y, 1)
                plt.plot(x, m*x + b, color='red', linestyle='--', alpha=0.7)
        
        # Set labels and title
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        
        if "title" in parameters:
            plt.title(parameters["title"])
        else:
            plt.title(f"{y_column} vs {x_column}")
        
        plt.grid(True, alpha=0.3)
        
        # Save and return figure
        return self._save_figure(parameters)
    
    def _box_plot(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create box plot for specified columns."""
        columns = parameters.get("columns")
        if not columns:
            # Use numeric columns if not specified
            columns = df.select_dtypes(include=['number']).columns.tolist()
            if not columns:
                return {
                    "success": False,
                    "error": "No numeric columns available for box plot"
                }
        
        # Filter to specified columns
        plot_df = df[columns]
        
        # Create figure
        plt.figure(figsize=parameters.get("figsize", (10, 6)))
        
        # Create box plot
        sns.boxplot(data=plot_df)
        
        # Set title
        if "title" in parameters:
            plt.title(parameters["title"])
        else:
            plt.title("Box Plot")
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save and return figure
        return self._save_figure(parameters)
    
    def _line_chart(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create line chart for specified columns."""
        x_column = parameters.get("x_column")
        y_column = parameters.get("y_column")
        
        if not x_column:
            return {
                "success": False,
                "error": "x_column must be specified for line chart"
            }
        
        if x_column not in df.columns:
            return {
                "success": False,
                "error": f"Column not found: {x_column}"
            }
        
        # Create figure
        plt.figure(figsize=parameters.get("figsize", (10, 6)))
        
        # Determine y columns
        if y_column:
            if y_column not in df.columns:
                return {
                    "success": False,
                    "error": f"Column not found: {y_column}"
                }
            y_columns = [y_column]
        else:
            # Use all numeric columns except x_column
            y_columns = [col for col in df.select_dtypes(include=['number']).columns 
                        if col != x_column]
            if not y_columns:
                return {
                    "success": False,
                    "error": "No numeric columns available for y-axis"
                }
        
        # Sort by x_column if it's a date or numeric
        if pd.api.types.is_datetime64_any_dtype(df[x_column]) or pd.api.types.is_numeric_dtype(df[x_column]):
            df = df.sort_values(by=x_column)
        
        # Create line chart
        for col in y_columns:
            plt.plot(df[x_column], df[col], marker='o', linestyle='-', label=col)
        
        # Set labels and title
        plt.xlabel(x_column)
        plt.ylabel(y_columns[0] if len(y_columns) == 1 else "Value")
        
        if "title" in parameters:
            plt.title(parameters["title"])
        else:
            plt.title("Line Chart")
        
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Handle x-axis formatting
        if pd.api.types.is_datetime64_any_dtype(df[x_column]):
            plt.gcf().autofmt_xdate()
        else:
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save and return figure
        return self._save_figure(parameters)
    
    def _heatmap(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create heatmap for specified columns."""
        columns = parameters.get("columns")
        if not columns:
            # Use numeric columns if not specified
            columns = df.select_dtypes(include=['number']).columns.tolist()
            if not columns:
                return {
                    "success": False,
                    "error": "No numeric columns available for heatmap"
                }
        
        # Filter to specified columns
        plot_df = df[columns]
        
        # Create figure
        plt.figure(figsize=parameters.get("figsize", (10, 8)))
        
        # Create heatmap
        sns.heatmap(plot_df, annot=True, cmap='viridis')
        
        # Set title
        if "title" in parameters:
            plt.title(parameters["title"])
        else:
            plt.title("Heatmap")
        
        plt.tight_layout()
        
        # Save and return figure
        return self._save_figure(parameters)
    
    def _hypothesis_test(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform hypothesis test on data."""
        test_type = parameters.get("test_type", "ttest")
        alpha = parameters.get("alpha", 0.05)
        
        if test_type == "ttest":
            # t-test requires two columns
            x_column = parameters.get("x_column")
            y_column = parameters.get("y_column")
            
            if not x_column or not y_column:
                return {
                    "success": False,
                    "error": "Both x_column and y_column must be specified for t-test"
                }
            
            if x_column not in df.columns or y_column not in df.columns:
                return {
                    "success": False,
                    "error": f"Columns not found: {x_column if x_column not in df.columns else y_column}"
                }
            
            # Perform t-test
            x = df[x_column].dropna()
            y = df[y_column].dropna()
            
            t_stat, p_value = stats.ttest_ind(x, y, nan_policy='omit')
            
            return {
                "success": True,
                "test_type": "t-test",
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "alpha": alpha,
                "reject_null": p_value < alpha,
                "interpretation": f"{'Reject' if p_value < alpha else 'Fail to reject'} the null hypothesis at alpha={alpha}"
            }
        
        elif test_type == "pearson":
            # Pearson correlation test
            x_column = parameters.get("x_column")
            y_column = parameters.get("y_column")
            
            if not x_column or not y_column:
                return {
                    "success": False,
                    "error": "Both x_column and y_column must be specified for Pearson correlation"
                }
            
            if x_column not in df.columns or y_column not in df.columns:
                return {
                    "success": False,
                    "error": f"Columns not found: {x_column if x_column not in df.columns else y_column}"
                }
            
            # Perform correlation test
            x = df[x_column].dropna()
            y = df[y_column].dropna()
            
            # Get indices where both x and y are not NaN
            valid_indices = x.index.intersection(y.index)
            x = x.loc[valid_indices]
            y = y.loc[valid_indices]
            
            r, p_value = stats.pearsonr(x, y)
            
            return {
                "success": True,
                "test_type": "Pearson correlation",
                "correlation_coefficient": float(r),
                "p_value": float(p_value),
                "alpha": alpha,
                "reject_null": p_value < alpha,
                "interpretation": f"{'Reject' if p_value < alpha else 'Fail to reject'} the null hypothesis at alpha={alpha}"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unsupported test type: {test_type}"
            }
    
    def _regression(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform regression analysis."""
        x_column = parameters.get("x_column")
        y_column = parameters.get("y_column")
        
        if not x_column or not y_column:
            return {
                "success": False,
                "error": "Both x_column and y_column must be specified for regression analysis"
            }
        
        if x_column not in df.columns or y_column not in df.columns:
            return {
                "success": False,
                "error": f"Columns not found: {x_column if x_column not in df.columns else y_column}"
            }
        
        # Prepare data
        X = df[x_column].values.reshape(-1, 1)
        y = df[y_column].values
        
        # Remove NaN values
        mask = ~(np.isnan(X.flatten()) | np.isnan(y))
        X = X[mask]
        y = y[mask]
        
        if len(X) < 2:
            return {
                "success": False,
                "error": "Not enough valid data points for regression analysis"
            }
        
        # Perform linear regression
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        
        # Get predictions
        y_pred = model.predict(X)
        
        # Calculate metrics
        from sklearn.metrics import mean_squared_error, r2_score
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        # Create visualization
        plt.figure(figsize=parameters.get("figsize", (10, 6)))
        plt.scatter(X, y, color='blue', alpha=0.7)
        plt.plot(X, y_pred, color='red', linewidth=2)
        
        # Set labels and title
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        
        if "title" in parameters:
            plt.title(parameters["title"])
        else:
            plt.title(f"Linear Regression: {y_column} vs {x_column}")
        
        # Add regression equation and R² to plot
        equation = f"y = {model.coef_[0]:.4f}x + {model.intercept_:.4f}"
        plt.annotate(f"{equation}\nR² = {r2:.4f}", 
                    xy=(0.05, 0.95), 
                    xycoords='axes fraction',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save figure
        result = self._save_figure(parameters)
        
        # Add regression results
        result.update({
            "coefficient": float(model.coef_[0]),
            "intercept": float(model.intercept_),
            "equation": equation,
            "r_squared": float(r2),
            "mean_squared_error": float(mse),
            "root_mean_squared_error": float(np.sqrt(mse))
        })
        
        return result
