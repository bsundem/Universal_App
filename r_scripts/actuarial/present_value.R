# Present Value Calculations
# This script provides functions for calculating present values of annuities

calculate_pv <- function(age, payment, interest_rate, term, freq_factor, 
                       table_type, gender) {
  # Convert to equivalent annual interest rate
  i <- interest_rate
  
  # Number of payments
  n <- term * freq_factor
  
  if (table_type == "None (Fixed Term)") {
    # Fixed term annuity calculation
    v <- 1/(1+i)
    if (i == 0) {
      pv <- payment * n / freq_factor
    } else {
      pv <- payment * (1 - v^n) / (i * freq_factor)
    }
    
    expected_duration <- term
    
  } else {
    # Life contingent annuity
    # Simplified mortality calculation for demonstration
    
    # Different mortality rates based on table type and gender
    if (table_type == "Standard Mortality") {
      if (gender == "male") {
        # Simplified Gompertz-Makeham for illustration
        qx_base <- 0.0005 + 0.00008 * exp(0.09 * age)
      } else if (gender == "female") {
        qx_base <- 0.0004 + 0.00004 * exp(0.09 * age)
      } else {
        # Unisex
        qx_base <- 0.00045 + 0.00006 * exp(0.09 * age)
      }
    } else if (table_type == "Annuitant Mortality") {
      # Annuitant tables typically have lower mortality rates
      if (gender == "male") {
        qx_base <- 0.0004 + 0.00006 * exp(0.085 * age)
      } else if (gender == "female") {
        qx_base <- 0.0003 + 0.00003 * exp(0.085 * age)
      } else {
        qx_base <- 0.00035 + 0.000045 * exp(0.085 * age)
      }
    }
    
    # Generate mortality rates for projection period
    ages <- age:(age+term)
    qx <- numeric(length(ages))
    
    for (j in 1:length(ages)) {
      current_age <- ages[j]
      if (table_type == "Standard Mortality") {
        if (gender == "male") {
          qx[j] <- 0.0005 + 0.00008 * exp(0.09 * current_age)
        } else if (gender == "female") {
          qx[j] <- 0.0004 + 0.00004 * exp(0.09 * current_age)
        } else {
          qx[j] <- 0.00045 + 0.00006 * exp(0.09 * current_age)
        }
      } else {
        if (gender == "male") {
          qx[j] <- 0.0004 + 0.00006 * exp(0.085 * current_age)
        } else if (gender == "female") {
          qx[j] <- 0.0003 + 0.00003 * exp(0.085 * current_age)
        } else {
          qx[j] <- 0.00035 + 0.000045 * exp(0.085 * current_age)
        }
      }
    }
    
    # Calculate survival probabilities
    px <- 1 - qx
    
    # Discount factors
    v <- (1/(1+i))^(0:(length(ages)-1))
    
    # Compute present value
    lx <- c(100000, rep(0, length(ages)-1))
    for (j in 2:length(ages)) {
      lx[j] <- lx[j-1] * px[j-1]
    }
    
    # For frequency adjustment
    payment_times <- c()
    survival_probs <- c()
    
    for (t in 1:(term*freq_factor)) {
      year_frac <- t / freq_factor
      if (year_frac <= length(ages) - 1) {
        payment_times <- c(payment_times, year_frac)
        
        # Interpolate survival probability
        year_idx <- floor(year_frac) + 1
        frac_part <- year_frac - floor(year_frac)
        
        if (year_idx < length(lx)) {
          interp_lx <- lx[year_idx] * (1-frac_part) + lx[year_idx+1] * frac_part
          survival_probs <- c(survival_probs, interp_lx / lx[1])
        } else {
          survival_probs <- c(survival_probs, lx[length(lx)] / lx[1])
        }
      }
    }
    
    # Discount factors for payment times
    payment_discount <- (1/(1+i))^payment_times
    
    # Present value calculation
    pv <- payment * sum(survival_probs * payment_discount) / freq_factor
    
    # Expected duration calculation (approximate)
    expected_duration <- sum(lx / lx[1]) - 0.5
    if (expected_duration > term) expected_duration <- term
  }
  
  # Calculate monthly equivalent
  monthly_payment <- pv * (i/12) / (1 - 1/((1+i/12)^(term*12)))
  
  return(list(
    present_value = pv,
    expected_duration = expected_duration,
    monthly_equivalent = monthly_payment
  ))
}