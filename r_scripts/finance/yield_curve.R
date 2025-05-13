# Yield curve analysis for finance applications
# This script provides functions for generating and analyzing yield curves

# Function to calculate yield curve
calculate_yield_curve <- function(start_date, end_date, curve_type = "nominal") {
  # In a real application, this would fetch actual yield curve data
  # For this example, we'll generate some sample data
  
  # Parse the dates
  start_date <- as.Date(start_date)
  end_date <- as.Date(end_date)
  
  # Create sequence of dates
  dates <- seq.Date(start_date, end_date, by = "month")
  
  # Maturities in months
  maturities <- c(1, 2, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360)
  
  # Base yields for different maturities (typical curve shape)
  base_yields <- c(0.015, 0.016, 0.017, 0.019, 0.021, 0.025, 0.028, 0.031, 0.033, 0.035, 0.037, 0.038)
  
  # Create empty data frame for results
  n_dates <- length(dates)
  n_maturities <- length(maturities)
  total_rows <- n_dates * n_maturities
  
  results <- data.frame(
    Date = rep(dates, each = n_maturities),
    Maturity = rep(maturities, times = n_dates),
    Yield = numeric(total_rows)
  )
  
  # Generate yields
  # Simulate the evolution of the yield curve over time
  for (i in 1:n_dates) {
    # Days since start
    days_since_start <- as.numeric(difftime(dates[i], start_date, units = "days"))
    
    # Simulate level and slope changes over time
    level_shift <- 0.001 * sin(days_since_start / 180 * pi)
    slope_factor <- 1 + 0.1 * sin(days_since_start / 360 * pi)
    
    # Adjust yields
    for (j in 1:n_maturities) {
      idx <- (i - 1) * n_maturities + j
      
      if (curve_type == "real") {
        # Real yields are typically lower than nominal
        base <- base_yields[j] - 0.01
      } else {
        base <- base_yields[j]
      }
      
      # Apply shifts and add some randomness
      random_factor <- rnorm(1, mean = 0, sd = 0.0005)
      results$Yield[idx] <- base + level_shift + (slope_factor - 1) * base_yields[j] / 10 + random_factor
    }
  }
  
  # Set variable for R script return
  yield_curve_data <- results
  
  return(results)
}
