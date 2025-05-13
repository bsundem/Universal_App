# Present value calculations for actuarial applications
# This script provides functions for calculating present values of annuities

# Calculate present value of an annuity
calculate_pv <- function(age, payment, interest_rate, term, freq_factor, table_type, gender) {
  # Validate inputs
  age <- as.integer(age)
  payment <- as.numeric(payment)
  interest_rate <- as.numeric(interest_rate)
  term <- as.integer(term)
  freq_factor <- as.integer(freq_factor)
  
  if (age < 0 || age > 120) {
    stop("Invalid age. Must be between 0 and 120.")
  }
  
  if (payment <= 0) {
    stop("Payment must be positive.")
  }
  
  if (interest_rate < 0 || interest_rate > 1) {
    stop("Invalid interest rate. Must be between 0 and 1.")
  }
  
  if (term <= 0) {
    stop("Term must be positive.")
  }
  
  if (freq_factor <= 0) {
    stop("Frequency factor must be positive.")
  }
  
  # Source the mortality script to get the calculation functions
  source("r_scripts/actuarial/mortality.R")
  
  # Get mortality data for the age range
  mortality_data <- calculate_mortality(age, age + term, interest_rate, table_type, gender)
  
  # Calculate present value
  # For a term certain annuity due with n payments of 1:
  # annuity_due = (1 - v^n) / (1 - v) where v = 1/(1+i)
  
  # Adjust interest rate for payment frequency
  i_adj <- (1 + interest_rate)^(1/freq_factor) - 1
  v_adj <- 1 / (1 + i_adj)
  
  # Number of payments
  n <- term * freq_factor
  
  # Annuity factor for term certain
  a_n <- (1 - v_adj^n) / (1 - v_adj)
  
  # Adjust for mortality
  lx_start <- mortality_data$lx[1]  # lives at starting age
  lx_values <- mortality_data$lx[1:(term+1)]  # lives at each future age
  
  # Calculate expected number of payments
  num_payments <- sum(lx_values[1:term] / lx_start)
  
  # Expected duration (in years)
  expected_duration <- num_payments / freq_factor
  
  # Mortality-adjusted annuity factor
  a_x <- a_n * (expected_duration / term)
  
  # Present value
  present_value <- payment * a_x
  
  # Monthly equivalent (assuming payment is annual)
  monthly_payment <- payment / 12
  monthly_equivalent <- monthly_payment * a_x * (freq_factor / 12)
  
  # Return the results
  result <- list(
    present_value = present_value,
    expected_duration = expected_duration,
    monthly_equivalent = monthly_equivalent
  )
  
  return(result)
}
