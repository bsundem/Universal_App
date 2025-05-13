# Portfolio analysis functions for finance applications
# This script provides functions for portfolio risk/return analysis

# Function to calculate portfolio metrics
calculate_portfolio_metrics <- function(returns_matrix, weights) {
  # Validate inputs
  if (!is.matrix(returns_matrix)) {
    stop("Returns must be a matrix with each column representing an asset.")
  }
  
  n_assets <- ncol(returns_matrix)
  
  if (length(weights) != n_assets) {
    stop("Number of weights must match number of assets.")
  }
  
  if (sum(weights) != 1) {
    # Normalize weights to sum to 1
    weights <- weights / sum(weights)
  }
  
  # Calculate mean returns for each asset
  mean_returns <- colMeans(returns_matrix)
  
  # Calculate the variance-covariance matrix
  cov_matrix <- cov(returns_matrix)
  
  # Calculate portfolio expected return
  expected_return <- sum(mean_returns * weights)
  
  # Calculate portfolio volatility
  portfolio_variance <- t(weights) %*% cov_matrix %*% weights
  volatility <- sqrt(portfolio_variance)
  
  # Calculate Sharpe ratio (assuming risk-free rate of 0 for simplicity)
  risk_free_rate <- 0
  sharpe_ratio <- (expected_return - risk_free_rate) / volatility
  
  # Return the results
  result <- list(
    expected_return = expected_return,
    volatility = volatility,
    sharpe_ratio = sharpe_ratio
  )
  
  return(result)
}