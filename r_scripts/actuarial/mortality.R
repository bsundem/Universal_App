# Mortality table calculations
# This script provides functions for calculating mortality tables and life expectancy

# Function to get available mortality tables
get_available_tables <- function() {
  # In a real application, this would query available tables from a database
  # For this example, we'll just return some standard tables
  tables <- list(
    id = c("soa_2012", "cso_2001"),
    name = c("SOA 2012 IAM", "CSO 2001"),
    description = c(
      "Society of Actuaries 2012 Individual Annuity Mortality",
      "2001 Commissioners Standard Ordinary Mortality Table"
    )
  )
  
  return(tables)
}

# Function to get a mortality table based on type
get_mortality_table <- function(table_type, gender) {
  # In a real application, this would load real mortality data
  # For this example, we'll generate some sample data
  
  # Base mortality rates by age
  ages <- 0:120
  
  # Generate qx (mortality rates) with a simplified Gompertz-Makeham model
  # qx = A + B*exp(C*age)
  if (table_type == "soa_2012") {
    # Parameters for SOA 2012
    if (gender == "male") {
      A <- 0.0001
      B <- 0.00005
      C <- 0.095
    } else if (gender == "female") {
      A <- 0.0001
      B <- 0.00004
      C <- 0.09
    } else { # unisex
      A <- 0.0001
      B <- 0.000045
      C <- 0.0925
    }
  } else {
    # Parameters for CSO 2001
    if (gender == "male") {
      A <- 0.0001
      B <- 0.00007
      C <- 0.10
    } else if (gender == "female") {
      A <- 0.0001
      B <- 0.00005
      C <- 0.095
    } else { # unisex
      A <- 0.0001
      B <- 0.00006
      C <- 0.0975
    }
  }
  
  # Generate qx values (probability of death at each age)
  qx <- pmin(A + B * exp(C * ages), 1.0)
  
  # Return the table
  result <- data.frame(
    Age = ages,
    qx = qx
  )
  
  return(result)
}

# Calculate mortality data for a given age range and interest rate
calculate_mortality <- function(age_from, age_to, interest_rate, table_type, gender) {
  # Validate inputs
  age_from <- as.integer(age_from)
  age_to <- as.integer(age_to)
  interest_rate <- as.numeric(interest_rate)
  
  if (age_from < 0 || age_to > 120 || age_from > age_to) {
    stop("Invalid age range. Must be between 0 and 120, and age_from must be <= age_to.")
  }
  
  if (interest_rate < 0 || interest_rate > 1) {
    stop("Invalid interest rate. Must be between 0 and 1.")
  }
  
  # Get the mortality table
  full_table <- get_mortality_table(table_type, gender)
  
  # Filter to the requested age range
  table <- full_table[full_table$Age >= age_from & full_table$Age <= age_to, ]
  
  # Calculate additional actuarial values
  # px = probability of survival (1 - qx)
  table$px <- 1 - table$qx
  
  # lx = number of lives at age x (starting with 100,000 at age_from)
  lx <- numeric(nrow(table))
  lx[1] <- 100000
  for (i in 2:length(lx)) {
    lx[i] <- lx[i-1] * table$px[i-1]
  }
  table$lx <- lx
  
  # ex = life expectancy
  ex <- numeric(nrow(table))
  for (i in 1:length(ex)) {
    ages_i <- i:nrow(table)
    ex[i] <- sum(lx[ages_i] / lx[i]) - 0.5
  }
  table$ex <- ex
  
  # ax = present value of a whole life annuity of 1 per year
  v <- 1 / (1 + interest_rate)  # discount factor
  ax <- numeric(nrow(table))
  
  # Completely rewrite this calculation to be more robust
  for (i in 1:nrow(table)) {
    # Calculate survival probabilities from age i
    max_periods <- nrow(table) - i + 1
    
    # Initialize tpx vector (probability of surviving t periods from age x)
    tpx <- rep(0, max_periods)
    tpx[1] <- 1  # 0px = 1 (probability of surviving 0 periods is 1)
    
    # Calculate survival probabilities for subsequent periods
    if (max_periods > 1) {
      for (t in 2:max_periods) {
        # Use the probability of survival for the previous age
        idx <- i + t - 2
        if (idx <= nrow(table)) {
          tpx[t] <- tpx[t-1] * table$px[idx]
        } else {
          # For safety, use the last available survival probability
          tpx[t] <- tpx[t-1] * tail(table$px, 1)
        }
      }
    }
    
    # Calculate present value of annuity using discrete approximation
    discount_factors <- v^(0:(max_periods-1))
    ax[i] <- sum(tpx * discount_factors)
  }
  table$ax <- ax
  
  # Return the results
  return(table)
}