# Mortality Table Calculations
# This script provides functions for calculating mortality tables

calculate_mortality <- function(age_from, age_to, interest_rate, table_type, gender) {
  # This is a simplified example
  # In a real application, you would use actual mortality tables
  
  ages <- age_from:age_to
  
  # Different mortality rates based on table type and gender
  if (table_type == "Standard Mortality") {
    if (gender == "male") {
      # Simplified Gompertz-Makeham for illustration
      qx <- 0.0005 + 0.00008 * exp(0.09 * ages)
    } else if (gender == "female") {
      qx <- 0.0004 + 0.00004 * exp(0.09 * ages)
    } else {
      # Unisex
      qx <- 0.00045 + 0.00006 * exp(0.09 * ages)
    }
  } else if (table_type == "Annuitant Mortality") {
    # Annuitant tables typically have lower mortality rates
    if (gender == "male") {
      qx <- 0.0004 + 0.00006 * exp(0.085 * ages)
    } else if (gender == "female") {
      qx <- 0.0003 + 0.00003 * exp(0.085 * ages)
    } else {
      qx <- 0.00035 + 0.000045 * exp(0.085 * ages)
    }
  } else {
    # Custom mortality (simplified)
    qx <- 0.0003 + 0.00005 * exp(0.08 * ages)
  }
  
  # Calculate survival probabilities
  px <- 1 - qx
  lx <- c(100000, rep(0, length(ages)-1))
  for (i in 2:length(ages)) {
    lx[i] <- lx[i-1] * px[i-1]
  }
  
  # Calculate life expectancy
  ex <- rep(0, length(ages))
  for (i in 1:length(ages)) {
    future_lx <- c(lx[i:length(lx)])
    future_lx <- future_lx / future_lx[1]
    ex[i] <- sum(future_lx) - 0.5
  }
  
  # Discount factors
  v <- (1/(1+interest_rate))^(0:(length(ages)-1))
  
  # Calculate annuity factors
  ax <- rep(0, length(ages))
  for (i in 1:length(ages)) {
    future_lx <- lx[i:length(lx)] / lx[i]
    ax[i] <- sum(future_lx * v[1:length(future_lx)])
  }
  
  # Prepare results
  result <- data.frame(
    Age = ages,
    qx = qx,
    px = px,
    lx = lx,
    ex = ex,
    ax = ax
  )
  
  return(result)
}