import numpy as np
import pandas as pd
from scipy.stats import norm

class RiskEngine:
    """
    Reusable market risk engine for sensitivity-based portfolios.

    The engine calculates Value at Risk (VaR), Expected Shortfall (ES),
    and simple stress losses using Historical, Parametric, and
    Monte Carlo methodologies.

    The portfolio is represented using linear sensitivities to risk
    factors. Portfolio P&L is therefore approximated as:

        P&L = risk-factor returns @ sensitivities

    This is a linear sensitivity-based risk engine and does not perform
    full revaluation of nonlinear instruments.

    Parameters
    ----------
    sensitivities : pandas.Series
        Portfolio sensitivity for each risk factor.

    risk_factor_prices : pandas.DataFrame
        Historical prices or levels for the corresponding risk factors.

    Notes
    -----
    - Risk-factor names in sensitivities and risk_factor_prices must match.
    - Market data must be numeric and finite.
    - Historical VaR/ES use observed historical returns.
    - Parametric VaR/ES assume normally distributed returns.
    - Monte Carlo uses a multivariate normal return model.
    - Monte Carlo uses a random seed for reproducibility.
    - Stress loss currently applies a common return shock to all factors.
    """

    def __init__(self, sensitivities, risk_factor_prices):
        self.sensitivities = sensitivities
        self.risk_factor_prices = risk_factor_prices

        self._validate_inputs()

    # ---------------------------------------------------------
    # Input Validation
    # ---------------------------------------------------------

    def _validate_inputs(self):
        """
        Validate portfolio sensitivities and risk-factor market data.

        Checks input types, numeric values, finite values, matching
        risk-factor names, and duplicate risk-factor labels.
        """

        if not isinstance(self.sensitivities, pd.Series):
            raise TypeError(
                "sensitivities must be a pandas Series."
            )

        if not isinstance(self.risk_factor_prices, pd.DataFrame):
            raise TypeError(
                "risk_factor_prices must be a pandas DataFrame."
            )

        if not pd.api.types.is_numeric_dtype(self.sensitivities):
            raise TypeError(
                "Sensitivities must contain numeric values."
            )

        if not all(
            pd.api.types.is_numeric_dtype(dtype)
            for dtype in self.risk_factor_prices.dtypes
        ):
            raise TypeError(
                "Risk factor prices must contain numeric values."
            )

        if not np.isfinite(self.sensitivities.to_numpy()).all():
            raise ValueError(
                "Sensitivities must contain only finite values."
            )

        if not np.isfinite(
            self.risk_factor_prices.to_numpy()
        ).all():
            raise ValueError(
                "Risk factor prices must contain only finite values."
            )

        if set(self.sensitivities.index) != set(
            self.risk_factor_prices.columns
        ):
            raise ValueError(
                "Risk factors in sensitivities and "
                "risk_factor_prices must match."
            )

        if self.sensitivities.index.duplicated().any():
            raise ValueError(
                "Sensitivities must not contain duplicate "
                "risk-factor names."
            )

        if self.risk_factor_prices.columns.duplicated().any():
            raise ValueError(
                "Risk factor prices must not contain duplicate "
                "risk-factor names."
            )

    # ---------------------------------------------------------
    # Parameter Validation
    # ---------------------------------------------------------

    def _validate_confidence(self, confidence):
        """Validate that confidence is strictly between 0 and 1."""

        if not isinstance(confidence, (int, float)):
            raise ValueError(
                "Confidence must be a numeric value between 0 and 1."
            )

        if not 0 < confidence < 1:
            raise ValueError(
                "Confidence must be between 0 and 1."
            )

    def _validate_horizon(self, horizon):
        """Validate that the risk horizon is a positive integer."""

        if (
            isinstance(horizon, bool)
            or not isinstance(horizon, int)
            or horizon <= 0
        ):
            raise ValueError(
                "Horizon must be a positive integer."
            )

    def _validate_simulations(self, simulations):
        """Validate that the Monte Carlo simulation count is positive."""

        if (
            isinstance(simulations, bool)
            or not isinstance(simulations, int)
            or simulations <= 0
        ):
            raise ValueError(
                "Simulations must be a positive integer."
            )

    # ---------------------------------------------------------
    # Return Calculation
    # ---------------------------------------------------------

    def _calculate_returns(self, horizon):
        """
        Calculate percentage returns over the specified horizon.

        Parameters
        ----------
        horizon : int
            Number of periods used to calculate returns.

        Returns
        -------
        pandas.DataFrame
            Historical percentage returns for each risk factor.
        """

        self._validate_horizon(horizon)

        if len(self.risk_factor_prices) <= horizon:
            raise ValueError(
                f"Insufficient historical observations for "
                f"a {horizon}-period horizon."
            )

        returns = self.risk_factor_prices.pct_change(
            periods=horizon,
            fill_method=None
        ).dropna()

        if returns.empty:
            raise ValueError(
                f"Insufficient historical observations for "
                f"a {horizon}-period horizon."
            )

        return returns

    # ---------------------------------------------------------
    # Portfolio P&L
    # ---------------------------------------------------------

    def _calculate_portfolio_pnl(self, returns):
        """
        Calculate portfolio P&L from risk-factor returns.

        The calculation uses a linear sensitivity approximation:

            P&L = returns @ sensitivities
        """

        aligned_sensitivities = self.sensitivities[
            returns.columns
        ]

        pnl = returns @ aligned_sensitivities

        return pnl

    # ---------------------------------------------------------
    # Historical VaR
    # ---------------------------------------------------------

    def historical_var(self, confidence=0.95, horizon=1):
        """
        Calculate Historical Value at Risk.

        Historical VaR is calculated as the absolute value of the
        lower-tail percentile of the historical portfolio P&L
        distribution.

        Parameters
        ----------
        confidence : float, default=0.95
            VaR confidence level.

        horizon : int, default=1
            Return horizon in periods.

        Returns
        -------
        float
            Historical VaR.
        """

        self._validate_confidence(confidence)
        self._validate_horizon(horizon)

        returns = self._calculate_returns(horizon)
        pnl = self._calculate_portfolio_pnl(returns)

        var_threshold = pnl.quantile(1 - confidence)

        var = abs(var_threshold)

        return var

    # ---------------------------------------------------------
    # Historical Expected Shortfall
    # ---------------------------------------------------------

    def historical_es(self, confidence=0.95, horizon=1):
        """
        Calculate Historical Expected Shortfall.

        Expected Shortfall is the average portfolio loss in the
        observations falling beyond the Historical VaR threshold.

        Parameters
        ----------
        confidence : float, default=0.95
            ES confidence level.

        horizon : int, default=1
            Return horizon in periods.

        Returns
        -------
        float
            Historical Expected Shortfall.
        """

        self._validate_confidence(confidence)
        self._validate_horizon(horizon)

        returns = self._calculate_returns(horizon)
        pnl = self._calculate_portfolio_pnl(returns)

        var_threshold = pnl.quantile(1 - confidence)

        tail_losses = pnl[pnl <= var_threshold]

        if tail_losses.empty:
            raise ValueError(
                "No observations available in the Expected "
                "Shortfall tail."
            )

        es = abs(tail_losses.mean())

        return es

    # ---------------------------------------------------------
    # Parametric VaR
    # ---------------------------------------------------------

    def parametric_var(self, confidence=0.95, horizon=1):
        """
        Calculate Parametric VaR under a normal-return assumption.

        Portfolio volatility is estimated from the historical
        covariance matrix of risk-factor returns and scaled by
        the square root of the selected horizon.

        Parameters
        ----------
        confidence : float, default=0.95
            VaR confidence level.

        horizon : int, default=1
            Return horizon in periods.

        Returns
        -------
        float
            Parametric VaR.
        """

        self._validate_confidence(confidence)
        self._validate_horizon(horizon)

        returns = self._calculate_returns(1)

        covariance_matrix = returns.cov()

        aligned_sensitivities = self.sensitivities[
            covariance_matrix.columns
        ]

        portfolio_variance = (
            aligned_sensitivities.T
            @ covariance_matrix
            @ aligned_sensitivities
        )

        portfolio_volatility = np.sqrt(
            portfolio_variance
        )

        z_score = norm.ppf(1 - confidence)

        horizon_volatility = (
            portfolio_volatility * np.sqrt(horizon)
        )

        var = abs(z_score * horizon_volatility)

        return var

    # ---------------------------------------------------------
    # Parametric Expected Shortfall
    # ---------------------------------------------------------

    def parametric_es(self, confidence=0.95, horizon=1):
        """
        Calculate Parametric Expected Shortfall.

        Expected Shortfall is derived from the normal distribution
        using the portfolio volatility and the selected confidence
        level.

        Parameters
        ----------
        confidence : float, default=0.95
            ES confidence level.

        horizon : int, default=1
            Return horizon in periods.

        Returns
        -------
        float
            Parametric Expected Shortfall.
        """

        self._validate_confidence(confidence)
        self._validate_horizon(horizon)

        returns = self._calculate_returns(1)

        covariance_matrix = returns.cov()

        aligned_sensitivities = self.sensitivities[
            covariance_matrix.columns
        ]

        portfolio_variance = (
            aligned_sensitivities.T
            @ covariance_matrix
            @ aligned_sensitivities
        )

        portfolio_volatility = np.sqrt(
            portfolio_variance
        )

        horizon_volatility = (
            portfolio_volatility * np.sqrt(horizon)
        )

        z_score = norm.ppf(1 - confidence)

        es = (
            horizon_volatility
            * norm.pdf(z_score)
            / (1 - confidence)
        )

        return es

    # ---------------------------------------------------------
    # Monte Carlo VaR
    # ---------------------------------------------------------

    def monte_carlo_var(
        self,
        confidence=0.95,
        horizon=1,
        simulations=10000,
        seed=42
    ):
        """
        Calculate Monte Carlo VaR.

        Risk-factor returns are simulated from a multivariate
        normal distribution using the historical mean vector and
        covariance matrix.

        Parameters
        ----------
        confidence : float, default=0.95
            VaR confidence level.

        horizon : int, default=1
            Return horizon in periods.

        simulations : int, default=10000
            Number of Monte Carlo simulations.

        seed : int, default=42
            Random-number-generator seed used for reproducibility.

        Returns
        -------
        float
            Monte Carlo VaR.

        Notes
        -----
        For horizons greater than one period, simulated returns
        are scaled using the square-root-of-time assumption.
        """

        self._validate_confidence(confidence)
        self._validate_horizon(horizon)
        self._validate_simulations(simulations)

        returns = self._calculate_returns(1)

        mean_returns = returns.mean()
        covariance_matrix = returns.cov()

        rng = np.random.default_rng(seed)

        simulated_returns = rng.multivariate_normal(
            mean=mean_returns,
            cov=covariance_matrix,
            size=simulations
        )

        if horizon > 1:
            simulated_returns *= np.sqrt(horizon)

        simulated_returns = pd.DataFrame(
            simulated_returns,
            columns=returns.columns
        )

        simulated_pnl = self._calculate_portfolio_pnl(
            simulated_returns
        )

        var_threshold = simulated_pnl.quantile(
            1 - confidence
        )

        var = abs(var_threshold)

        return var

    # ---------------------------------------------------------
    # Monte Carlo Expected Shortfall
    # ---------------------------------------------------------

    def monte_carlo_es(
        self,
        confidence=0.95,
        horizon=1,
        simulations=10000,
        seed=42
    ):
        """
        Calculate Monte Carlo Expected Shortfall.

        Expected Shortfall is calculated as the average loss
        beyond the simulated VaR threshold.

        Parameters
        ----------
        confidence : float, default=0.95
            ES confidence level.

        horizon : int, default=1
            Return horizon in periods.

        simulations : int, default=10000
            Number of Monte Carlo simulations.

        seed : int, default=42
            Random-number-generator seed used for reproducibility.

        Returns
        -------
        float
            Monte Carlo Expected Shortfall.
        """

        self._validate_confidence(confidence)
        self._validate_horizon(horizon)
        self._validate_simulations(simulations)

        returns = self._calculate_returns(1)

        mean_returns = returns.mean()
        covariance_matrix = returns.cov()

        rng = np.random.default_rng(seed)

        simulated_returns = rng.multivariate_normal(
            mean=mean_returns,
            cov=covariance_matrix,
            size=simulations
        )

        if horizon > 1:
            simulated_returns *= np.sqrt(horizon)

        simulated_returns = pd.DataFrame(
            simulated_returns,
            columns=returns.columns
        )

        simulated_pnl = self._calculate_portfolio_pnl(
            simulated_returns
        )

        var_threshold = simulated_pnl.quantile(
            1 - confidence
        )

        tail_losses = simulated_pnl[
            simulated_pnl <= var_threshold
        ]

        if tail_losses.empty:
            raise ValueError(
                "No observations available in the Expected "
                "Shortfall tail."
            )

        es = abs(tail_losses.mean())

        return es

    # ---------------------------------------------------------
    # Stress Loss
    # ---------------------------------------------------------

    def stress_loss(self, stress_return):
        """
        Calculate portfolio loss under a common stress shock.

        Parameters
        ----------
        stress_return : float
            Hypothetical return shock applied to every risk factor.

        Returns
        -------
        float
            Absolute portfolio loss under the stress scenario.

        Notes
        -----
        The current implementation applies the same shock to every
        risk factor. Factor-specific stress scenarios can be added
        in a future version.
        """

        if not isinstance(stress_return, (int, float)):
            raise ValueError(
                "stress_return must be numeric."
            )

        if not np.isfinite(stress_return):
            raise ValueError(
                "stress_return must be finite."
            )

        stress_returns = pd.Series(
            stress_return,
            index=self.risk_factor_prices.columns
        )

        pnl = stress_returns @ self.sensitivities

        return abs(pnl)

    # ---------------------------------------------------------
    # Main Calculation Interface
    # ---------------------------------------------------------

    def calculate(
        self,
        confidence=0.95,
        horizon=1,
        methodology="historical",
        simulations=10000,
        seed=42
    ):
        """
        Calculate VaR and Expected Shortfall using the selected method.

        Parameters
        ----------
        confidence : float, default=0.95
            Risk confidence level.

        horizon : int, default=1
            Risk horizon in periods.

        methodology : str, default="historical"
            Risk methodology. Supported values are:
            "historical", "parametric", and "monte_carlo".

        simulations : int, default=10000
            Number of simulations used for Monte Carlo methods.

        seed : int, default=42
            Random-number-generator seed used for Monte Carlo methods.

        Returns
        -------
        dict
            Dictionary containing methodology, confidence, horizon,
            VaR, and Expected Shortfall.

        Examples
        --------
        result = engine.calculate(
            confidence=0.99,
            horizon=10,
            methodology="historical"
        )
        """

        self._validate_confidence(confidence)
        self._validate_horizon(horizon)
        self._validate_simulations(simulations)

        if not isinstance(methodology, str):
            raise ValueError(
                "Methodology must be a string: "
                "historical, parametric, or monte_carlo."
            )

        methodology = methodology.lower()

        if methodology == "historical":

            var = self.historical_var(
                confidence=confidence,
                horizon=horizon
            )

            es = self.historical_es(
                confidence=confidence,
                horizon=horizon
            )

        elif methodology == "parametric":

            var = self.parametric_var(
                confidence=confidence,
                horizon=horizon
            )

            es = self.parametric_es(
                confidence=confidence,
                horizon=horizon
            )

        elif methodology == "monte_carlo":

            var = self.monte_carlo_var(
                confidence=confidence,
                horizon=horizon,
                simulations=simulations,
                seed=seed
            )

            es = self.monte_carlo_es(
                confidence=confidence,
                horizon=horizon,
                simulations=simulations,
                seed=seed
            )

        else:

            raise ValueError(
                "Methodology must be one of: "
                "historical, parametric, monte_carlo."
            )

        return {
            "methodology": methodology,
            "confidence": confidence,
            "horizon": horizon,
            "VaR": round(var, 2),
            "Expected Shortfall": round(es, 2)
        }