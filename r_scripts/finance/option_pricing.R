# Option pricing functions for finance applications
# This script provides functions for pricing options using Black-Scholes model

# Function to price an option using Black-Scholes model
price_option <- function(option_type, spot_price, strike_price, time_to_expiry,
                         risk_free_rate, volatility, dividend_yield = 0) {
  # Validate inputs
  if (\!(option_type %in% c("call", "put"))) {
    stop("Option type must be 'call' or 'put'.")
  }
  
  if (spot_price <= 0 || strike_price <= 0) {
    stop("Prices must be positive.")
  }
  
  if (time_to_expiry <= 0) {
    stop("Time to expiry must be positive.")
  }
  
  if (volatility <= 0) {
    stop("Volatility must be positive.")
  }
  
  # Calculate d1 and d2
  d1 <- (log(spot_price / strike_price) + 
         (risk_free_rate - dividend_yield + 0.5 * volatility^2) * time_to_expiry) / 
        (volatility * sqrt(time_to_expiry))
  
  d2 <- d1 - volatility * sqrt(time_to_expiry)
  
  # Calculate option price
  if (option_type == "call") {
    price <- spot_price * exp(-dividend_yield * time_to_expiry) * pnorm(d1) - 
             strike_price * exp(-risk_free_rate * time_to_expiry) * pnorm(d2)
    
    delta <- exp(-dividend_yield * time_to_expiry) * pnorm(d1)
  } else {  # put
    price <- strike_price * exp(-risk_free_rate * time_to_expiry) * pnorm(-d2) - 
             spot_price * exp(-dividend_yield * time_to_expiry) * pnorm(-d1)
    
    delta <- exp(-dividend_yield * time_to_expiry) * (pnorm(d1) - 1)
  }
  
  # Calculate the Greeks
  gamma <- exp(-dividend_yield * time_to_expiry) * dnorm(d1) / 
          (spot_price * volatility * sqrt(time_to_expiry))
  
  vega <- 0.01 * spot_price * exp(-dividend_yield * time_to_expiry) * 
          sqrt(time_to_expiry) * dnorm(d1)
  
  theta <- -((spot_price * volatility * exp(-dividend_yield * time_to_expiry) * 
              dnorm(d1)) / (2 * sqrt(time_to_expiry))) - 
           risk_free_rate * strike_price * exp(-risk_free_rate * time_to_expiry) * 
           pnorm(d2 * ifelse(option_type == "call", 1, -1))
  
  # Return the results
  result <- list(
    price = price,
    delta = delta,
    gamma = gamma,
    theta = theta / 365,  # Convert to daily theta
    vega = vega
  )
  
  return(result)
}
