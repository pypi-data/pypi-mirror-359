import io
import datetime
from pathlib import Path
from typing import Optional, Literal, Any, Union, List, Tuple, Dict

import numpy as np
import numpy.typing as npt
import pandas as pd

from pyoptimum import AsyncClient, PyOptimumException
from pyoptimum.model import Model

LESS_THAN_OR_EQUAL = "\u2264"
GREATER_THAN_OR_EQUAL = "\u2265"
EQUAL = "\u003d"

class Portfolio:
    """
    Helper class to facilitate portfolio calculations using the Optimize and Models API.

    Portfolio objects are constructed from two ``AsyncClient`` s, e.g.

    .. code-block:: python

        from pyoptimum import AsyncClient
        from pyoptimum.portfolio import Portfolio
        optimize_client = pyoptimum.AsyncClient(username=username, password=password, api='optimize')
        models_client = pyoptimum.AsyncClient(username=username, password=password, api='models')
        portfolio = Portfolio(self.portfolio_client, self.model_client)

    The ``portfolio`` object can now be used to coordinate calls to both clients in order to build and manipulate portfolios.

    Optional arguments are:

    :param model_method: one of ['linear', 'linear-fractional', 'diagonal']
    :param follow_resource: if True, will handle polling asynchronous resources
    :param wait_time: how long to wait before pooling again (in seconds)
    :param max_retries: how many times to retry before timing out
    """

    ModelMethodLiteral = Literal['linear', 'linear-fractional', 'diagonal']

    MethodLiteral = Literal['approximate', 'optimal']
    ConstraintFunctionLiteral = Literal['purchases', 'sales', 'holdings', 'short sales']
    ConstraintSignLiteral = Literal[LESS_THAN_OR_EQUAL, GREATER_THAN_OR_EQUAL, EQUAL]
    ConstraintUnitLiteral = Literal['shares', 'value', 'percent value']
    GroupConstraintFunctionLiteral = Literal['purchases', 'sales', 'holdings', 'short sales', 'return']
    GroupConstraintUnitLiteral = Literal['value', 'percent value']

    FunctionTable = {
        'sales': 'sales',
        'purchases': 'buys',
        'short sales': 'leverage',
        'holdings': 'sum',
        'return': 'return'
    }
    InverseFunctionTable = {v: k for k, v in FunctionTable.items()}

    BasicMarket = {
        '^GSPC': "S&P 500",
        '^RUT': "Russel 2000",
        '^IXIC': "NASDAQ"
    }
    BasicRanges = ['1mo', '3mo', '6mo', '1y', '2y', '5y']

    def __init__(self,
                 portfolio_client: AsyncClient,
                 model_client: AsyncClient,
                 model_method: ModelMethodLiteral = 'linear',
                 follow_resource: bool = True,
                 max_retries: int = 18,
                 wait_time: Optional[float]=None):
        self.portfolio_client = portfolio_client
        self.model_client = model_client
        self.model_method = model_method
        self.models: dict = {}
        self.model_weights: Dict[str, float] = {}
        self.portfolio = None
        self.inactive_portfolio = None
        self.frontier = None
        self.frontier_query_params = {}
        self.frontier_method: Portfolio.MethodLiteral = 'approximate'
        self.follow_resource = follow_resource
        self.max_retries = max_retries
        self.wait_time = wait_time
        self.groups = {}
        self.group_constraints = []

    @staticmethod
    def _locate_value(value: Any, column: str, df: pd.DataFrame) -> Tuple[Optional[pd.Series], Optional[pd.Series]]:
        index = df[column].searchsorted(value)
        n = df.shape[0]
        if index == n:
            # got the last element
            return df.iloc[-1], None
        elif index == 0:
            # got the first element
            return None, df.iloc[0]
        else:
            # interpolate
            return df.iloc[index - 1], df.iloc[index]

    def _update_prices(self, prices: dict) -> float:

        # add prices to dataframe
        prices = pd.DataFrame.from_dict(prices, orient='index',
                                        columns=['timestamp', 'close', 'first_quote'])

        # update portfolio value and weights
        self.portfolio['close ($)'] = prices['close']
        self.portfolio['value ($)'] = self.portfolio['shares'] * self.portfolio['close ($)']
        value = self.get_value()
        self.portfolio['value (%)'] = self.portfolio['value ($)'] / value if value > 0.0 else 0.0

        return value

    def _get_portfolio_query(self,
                             cashflow: float, max_sales: float,
                             short_sales: bool, buy: bool, sell: bool,
                             rho: float=0.0) -> dict:

        # get model data
        model = self.get_model()
        data: Dict[str, Any] = model.to_dict(as_list=True,
                                             normalize_variance=True)

        # has regularization
        if rho > 0:
            data['rho'] = rho

        # get portfolio data
        h0 = self.get_value()
        h = h0 + cashflow
        if h0 == 0 and cashflow == 0:
            raise ValueError("Cashflow cannot be zero on a portfolio with no shares")

        if h == 0:
            raise ValueError("Cashflow cannot be equal to current holdings")

        # scaling
        scaling = np.fabs(h)

        x0 = self.portfolio['value (%)']
        data['x0'] = ((h0 / scaling) * x0).tolist()

        # check bound in max_sales
        if np.isfinite(max_sales) and max_sales < 0:
            raise ValueError('max_sales must be non-negative')

        # add cashflow and constraints
        constraints_ = []
        data['cashflow'] = cashflow / scaling
        if np.isfinite(max_sales):
            constraints_.append({
                'label': 'sales',
                'function': 'sales',
                'bounds': max_sales / scaling
            })

        data['options'] = {
            'short': short_sales,
            'buy': buy,
            'sell': sell
        }

        # has lower bound
        if np.isfinite(self.portfolio['lower']).any():
            xlo = self.portfolio['lower'] * self.portfolio['close ($)'] / scaling
            data['xlo'] = xlo.tolist()

        # has upper bound
        if np.isfinite(self.portfolio['upper']).any():
            xup = self.portfolio['upper'] * self.portfolio['close ($)'] / scaling
            data['xup'] = xup.tolist()

        # group constraints
        sets = set()
        for cnstr in self.group_constraints:
            sets.add(cnstr['set'])
            bounds = cnstr['bounds']
            divider = 1 if cnstr['function'] == 'returns' else scaling
            if isinstance(bounds, (list, tuple)) :
                bounds = [b/divider for b in bounds]
            else:
                bounds /= divider
            constraints_.append({**cnstr, 'bounds': bounds})

        if len(sets) > 0:
            # add sets
            tickers = self.get_tickers()
            data['sets'] = [{'label': s, 'indices': [tickers.index(e) for e in self.groups[s]]} for s in sets]

        if len(constraints_) > 0:
            # add constraints
            data['constraints'] = constraints_

        return data

    def set_follow_resource(self, follow_resource: bool,
                            max_retries: int=18,
                            wait_time: Optional[float]=None) -> None:
        """
        Set parameters for pooling asynchronous resources

        :param follow_resource: if True, will handle polling asynchronous resources
        :param wait_time: how long to wait before pooling again (in seconds)
        :param max_retries: how many times to retry before timing out
        """
        self.follow_resource = follow_resource
        self.max_retries = max_retries
        self.wait_time = wait_time

    def get_follow_resource(self) -> dict:
        """
        Get parameters for pooling asynchronous resources

        :return: dictionary with parameters
        """
        results = {
            'follow_resource': self.follow_resource,
            'max_retries': self.max_retries
        }
        if self.wait_time is not None:
            results['wait_time'] = self.wait_time
        return results

    def invalidate_model(self):
        """
        Invalidate the current portfolio models
        """
        self.models = {}
        self.model_weights = {}

    def invalidate_frontier(self):
        """
        Invalidate the current frontier
        """
        self.frontier = None
        self.frontier_query_params = {}
        self.frontier_method = 'none'

    def has_prices(self) -> bool:
        """
        :return: True if prices have been retrieved
        """
        return self.portfolio is not None and 'close ($)' in self.portfolio

    def has_frontier(self) -> bool:
        """
        :return: True if a frontier is available
        """
        return self.frontier is not None

    def has_models(self) -> bool:
        """
        :return: True if models have been retrieved
        """
        return bool(self.models)

    def set_models(self, models: Dict[str, Union[dict, Model]],
                   model_weights: Optional[Dict[str, float]] = None,
                   tickers: Optional[List[str]] = None) -> None:
        """
        Set portfolio models

        :param models: a dictionary with the models per range
        :param model_weights: the model weights (default: ``None``, which is the same as equal weights)
        :param tickers: list of model tickers
        """
        # add models
        self.models = {rg: Model(data) for rg, data in models.items()}

        # set model weights
        model_weights = model_weights or {rg: 1.0 for rg in models.keys()}
        self.set_model_weights(model_weights)

        # reindex portfolio
        if tickers is not None:
            self.portfolio = self.portfolio.reindex(tickers)

        # reinitialize frontier
        self.invalidate_frontier()

    def get_model(self) -> Model:
        """
        :return: the portfolio model for the current model and weights
        """
        assert self.has_models(), "Models have not yet been retrieved"

        if self.model_method == 'diagonal':
            model = Model({attr: sum([weight * getattr(self.models[rg], attr)
                                      for rg, weight in self.model_weights.items()])
                           for attr in ['r', 'Q']})
        elif self.model_method == 'linear':
            # linear model
            model = Model({attr: sum([weight * getattr(self.models[rg], attr)
                                      for rg, weight in self.model_weights.items()])
                           for attr in ['r', 'D', 'F', 'Q']})
        else:
            # linear-fractional model
            model = Model({attr: sum([weight * getattr(self.models[rg], attr)
                                      for rg, weight in self.model_weights.items()])
                           for attr in ['r', 'Di', 'F', 'Q']})

        return model

    def get_tickers(self) -> List[str]:
        """
        :return: the portfolio tickers
        """
        return self.portfolio.index.tolist()

    def get_value(self) -> float:
        """
        :return: the total portfolio value
        """
        try:
            return sum(self.portfolio['value ($)'])
        except (KeyError, TypeError):
            return 0.0

    def import_csv(self, filepath: Union[str,bytes,io.BytesIO,Path]) -> None:
        """
        Import portfolio from csv file

        :param filepath: the file path
        """
        # read csv
        portfolio = pd.read_csv(filepath)

        # sanitize column names
        portfolio.columns = [c.strip() for c in portfolio.columns]

        # import dataframe
        self.import_dataframe(portfolio)

    def import_dataframe(self, portfolio: pd.DataFrame) -> None:
        """
        Import portfolio from dataframe

        :param portfolio: the dataframe
        """

        if portfolio.index.name != 'ticker':
            # set ticker as index
            assert 'ticker' in portfolio.columns, "Portfolio must contain a column " \
                                                  "named 'ticker'"
            portfolio.set_index('ticker', inplace=True)

        # initialize shares
        if 'shares' not in portfolio.columns:
            portfolio['shares'] = 0.0

        # has groups?
        self.groups = {}
        self.group_constraints = []
        if 'groups' in portfolio.columns:
            def add_to_group(row):
                if isinstance(row['groups'], str):
                    for g in row['groups'].split('|'):
                        g = g.strip()
                        if g:
                            if g in self.groups:
                                self.groups[g].append(row.name)
                            else:
                                self.groups[g] = [row.name]
            # add to groups
            portfolio.apply(add_to_group, axis=1)

            # check for uniqueness
            for k, v in self.groups.items():
                if len(set(v)) != len(v):
                    raise PyOptimumException(f'Group {k} members are not unique')

        # make sure shares are float
        portfolio = portfolio.astype({"shares": float})

        # initialize lower and upper
        portfolio['lower'] = -np.inf
        portfolio['upper'] = np.inf

        # invalidate models and frontier
        self.invalidate_frontier()
        self.invalidate_model()

        # remove all other columns and set portfolio
        self.portfolio = portfolio[['shares', 'lower', 'upper']]
        self.inactive_portfolio = None

    async def retrieve_prices(self) -> float:
        """
        Retrieve the latest prices of all portfolio assets

        :return: the total portfolio value
        """

        # retrieve prices
        data = {'symbols': self.portfolio.index.tolist()}
        prices = await self.model_client.call('prices', data,
                                              **self.get_follow_resource())

        # add prices to dataframe
        value = self._update_prices(prices)

        return value

    def split(self, tickers: List[str]) -> None:
        """
        Split inactive portfolio

        :param tickers: the list of active tickers in the portfolio
        """
        if len(tickers) == 0:
            raise ValueError('tickers cannot be empty')

        current_ticker_set = set(self.get_tickers())
        ticker_set = set(tickers)
        if current_ticker_set == ticker_set:
            # do nothing
            return

        # are there unknown tickers?
        unknown = ticker_set.difference(current_ticker_set)
        if unknown:
            raise ValueError(f"'{unknown}' are not active in the current portfolio")

        # determine inactive and active tickers
        inactive = list(current_ticker_set.difference(ticker_set))

        # use list to preserve ordering
        active = [t for t in self.get_tickers() if t not in inactive]

        # remove inactive
        self.inactive_portfolio = self.portfolio.loc[inactive]
        self.portfolio = self.portfolio.loc[active]

        # invalidate models and frontier
        self.invalidate_frontier()
        self.invalidate_model()

    def _set_models(self,
                    response: dict,
                    include_prices: bool,
                    model_weights: Optional[Dict[str, float]] = None):

        # remove messages, tickers and market
        messages = response.pop('messages')
        tickers = response.pop('tickers')
        market = response.pop('market')

        # split inactive portfolio
        self.split(tickers)

        if include_prices:
            # update prices
            self._update_prices(response.pop('prices'))

        # get models
        models = response.pop('models')

        # set models
        self.set_models(models, model_weights, tickers=tickers)

        return messages, tickers, market

    async def retrieve_basic_models(self,
                                    end: datetime.date = datetime.date.today(),
                                    model_weights: Optional[Dict[str, float]] = None,
                                    include_prices: bool = False,
                                    horizon: int = 1)\
            -> Tuple[List[str], List[str], List[str]]:
        """
        Retrieve basic portfolio models based on market tickers

        If ``market_tickers`` is empty then returns a diagonal model in which all
        correlations are ignored.

        :param end: the last day to retrieve models
        :param model_weights: the model weights (default: ``None``, which is the same as equal weights)
        :param include_prices: whether to include prices on results (default: ``False``)
        :param horizon: the investment horizon in days (default: ``1``)
        :return: a list of messages
        """

        # retrieve models
        data = {
            'tickers': self.portfolio.index.tolist(),
            'end': str(end),
            'options': {
                'include_prices': include_prices,
                'horizon': horizon
            }
        }
        response = await self.model_client.call('basic', data,
                                                **self.get_follow_resource())
        return self._set_models(response, include_prices, model_weights)

    async def retrieve_custom_models(self,
                                     market_tickers: List[str],
                                     ranges: Union[str, List[str]],
                                     end: datetime.date = datetime.date.today(),
                                     model_weights: Optional[Dict[str, float]] = None,
                                     common_factors: bool = False,
                                     include_prices: bool = False,
                                     trim_weekends: bool = True,
                                     horizon: int = 1,
                                     weights: Literal['linear', 'quadratic'] = 'linear') \
            -> Tuple[List[str], List[str], List[str]]:
        """
        Retrieve custom portfolio models based on market tickers

        If ``market_tickers`` is empty then returns a diagonal model in which all
        correlations are ignored.

        :param market_tickers: the market tickers
        :param ranges: the ranges to retrieve the portfolio models
        :param end: the last day to retrieve models
        :param model_weights: the model weights (default: ``None``, which is the same as equal weights)
        :param common_factors: whether to keep factors common (default: ``False``)
        :param include_prices: whether to include prices on results (default: ``False``)
        :param trim_weekends: whether to trim weekends (default: ``True``)
        :param horizon: the investment horizon in days (default: ``1``)
        :param weights: the model weights (default: ``linear``)
        :return: a list of messages
        """

        # retrieve models
        data = {
            'tickers': self.portfolio.index.tolist(),
            'end': str(end),
            'range': ranges,
            'options': {
                'common': common_factors,
                'include_prices': include_prices,
                'trim_weekends': trim_weekends,
                'horizon': horizon,
                'weights': weights
            }
        }
        if market_tickers:
            data['market'] = market_tickers
        else:
            self.model_method = 'diagonal'
        response = await self.model_client.call('custom', data,
                                                **self.get_follow_resource())
        return self._set_models(response, include_prices, model_weights)

    async def retrieve_frontier(self,
                                cashflow: float, max_sales: float,
                                short_sales: bool, buy: bool, sell: bool,
                                rho: float=0.0) -> None:
        """
        Retrieve the portfolio frontier

        :param cashflow: the cashflow
        :param max_sales: the max sales
        :param short_sales: whether to allow short sales
        :param buy: whether to allow buys
        :param sell: whether to allow sells
        :param rho: regularization factor (default: ``0.0``)
        """

        # assert models and prices are defined
        assert self.has_prices() and self.has_models(),\
            "Either prices or models are missing"

        # retrieve frontier
        query = self._get_portfolio_query(cashflow, max_sales,
                                          short_sales, buy, sell, rho)
        try:
            sol = await self.portfolio_client.call('frontier', query,
                                                   **self.get_follow_resource())
        except PyOptimumException as e:
            self.invalidate_frontier()
            raise e

        if len(sol['frontier']) == 0:
            self.invalidate_frontier()
            raise ValueError('Could not calculate optimal frontier; constraints likely make the problem infeasible.')

        # calculate variance
        model = self.get_model()
        values = []
        for s in sol['frontier']:
            if s['sol']['status'] == 'optimal':
                mu = s['mu']
                x = np.array(s['sol']['x'])
                _, std = model.return_and_variance(x)
                values.append((mu, std, x))

        # assemble return dataframe
        frontier = pd.DataFrame(values, columns=['mu', 'std', 'x'])
        self.frontier = frontier

        # save query params
        self.frontier_query_params = query
        self.frontier_method = 'optimal'

    async def retrieve_recommendation(self, mu: Optional[float]=None,
                                      method: MethodLiteral = 'approximate') -> dict:
        """
        Retrieve or calculate recommendations

        :param mu: the expected return
        :param method: if `approximate` calculates approximate recommendations using the current frontier; if `exact` retrieve exact recommendation from the Optimize API
        :return:
        """

        assert self.has_frontier(), "Frontier has not been retrieved"

        if mu is None:
            # locate std
            _, std = self.get_return_and_variance()
            left, right = Portfolio._locate_value(std, 'std', self.frontier)
            if left is None:
                # got the first element
                mu = right['mu']
            elif right is None:
                # got the last element
                mu = left['mu']
            else:
                # interpolate
                std1, std2 = left['std'], right['std']
                eta = (std - std1)/(std2-std1)
                mu = (1 - eta) * left['mu'] + eta * right['mu']

        if method == 'approximate':
            # calculate approximate weights

            # locate mu
            left, right = Portfolio._locate_value(mu, 'mu', self.frontier)
            if left is None:
                # got the first element
                x = right['x']
                std = right['std']
            elif right is None:
                # got the last element
                x = left['x']
                std = left['std']
            else:
                # interpolate
                mu1, mu2 = left['mu'], right['mu']
                eta = (mu - mu1)/(mu2-mu1)
                x = (1 - eta) * left['x'] + eta * right['x']
                std = (1 - eta) * left['std'] + eta * right['std']

            return {'x': x, 'status': 'optimal', 'std': std, 'mu': mu}

        elif method == 'exact':
            # exact recommendation
            data = self.frontier_query_params.copy()
            data['mu'] = mu

            recs = await self.portfolio_client.call('portfolio', data,
                                                    **self.get_follow_resource())
            if recs['status'] == 'optimal':
                x = np.array(recs['x'])
                _, std = self.get_model().return_and_variance(x)
                return {'x': x, 'status': recs['status'], 'std': std, 'mu': mu}
            else:
                # return approximate if optimization failed
                return await self.retrieve_recommendation(mu, method='approximate')

        else:

            raise Exception("Invalid method '%s'", method)

    def add_to_frontier(self, mu: float, std: float, x: npt.NDArray) -> None:
        """
        Add point to current frontier

        :param mu: the return
        :param std: the standard deviation
        :param x: the portfolio values
        """
        assert self.has_frontier(), "Frontier has not been retrieved"

        frontier = pd.concat((self.frontier,
                              pd.DataFrame([(mu, std, x)],
                                           columns=['mu', 'std', 'x'])),
                             ignore_index=True)
        frontier.sort_values(by=['mu'], inplace=True, ignore_index=True)
        self.frontier = frontier

    def set_model_weights(self, model_weights: Dict[str, float]) -> None:
        """
        Set weights for the current portfolio models

        :param model_weights: the model weights
        """

        # range checking
        assert self.has_models(), "Models have not yet been retrieved"

        assert self.models.keys() == model_weights.keys(), ("Weights must have the same "
                                                            "keys as models")

        assert all(value >= 0 for value in model_weights.values()), ("Weights must be "
                                                                     "non-negative")

        # normalize weights
        sum_model_weights = sum(model_weights.values())
        if sum_model_weights > 0:
            self.model_weights = {rg: value/sum_model_weights for rg, value in
                                  model_weights.items()}
        else:
            self.model_weights = {rg: 1/len(model_weights) for rg in
                                  model_weights.keys()}

        # update frontier
        if self.has_frontier():
            model = self.get_model()
            mu_std = (self.frontier['x']
                      .apply(lambda x: pd.Series(model.return_and_variance(x),
                                                 index=['mu', 'std'])))
            self.frontier[['mu', 'std']] = mu_std
            self.frontier_method = 'approximate'

    def set_model_method(self, method: ModelMethodLiteral):
        self.model_method = method

    def get_portfolio_dataframe(self) -> pd.DataFrame:
        """
        :return: the portfolio as a dataframe
        """

        # copy portfolio
        portfolio_df = self.portfolio.copy()

        if self.has_models():
            # add return
            model = self.get_model()
            portfolio_df['return (%)'] = model.r.copy()
            portfolio_df['std (%)'] = model.std.copy()

        if self.has_prices():
            # add lower and upper bounds in value
            portfolio_df['lower ($)'] = portfolio_df['close ($)'] * portfolio_df['lower']
            portfolio_df['upper ($)'] = portfolio_df['close ($)'] * portfolio_df['upper']

        return portfolio_df

    def get_recommendation_dataframe(self, x: npt.NDArray, cashflow: float) -> pd.DataFrame:
        """
        :param x: the portfolio weights
        :param cashflow: the cashflow
        :return: the portfolio recommendation as a dataframe
        """

        assert np.fabs(np.sum(x) - 1) < 1e-4, "portfolio weights do not sum to one"

        if self.has_models() and self.has_prices():
            x0 = self.portfolio['value (%)']
            h0 = self.get_value()
            h = h0 + cashflow
            value = x * h
            change_value = value - x0 * h0
            df = pd.DataFrame(data={
                'ticker': self.get_tickers(),
                'shares': value / self.portfolio['close ($)'],
                'value ($)': value,
                'value (%)': x,
                'change (shares)': change_value / self.portfolio['close ($)'],
                'change ($)': change_value,
            })
        else:
            df = pd.DataFrame(columns=['ticker', 'shares', 'value ($)', 'value (%)', 'change (shares)', 'change ($)'])

        return df

    def get_frontier_range(self):
        """
        :return: the range of frontier values
        """
        if self.frontier is None:
            raise ValueError('Frontier has not been retrieved yet')
        mu_range = self.frontier['mu'].iloc[0], self.frontier['mu'].iloc[-1]
        std_range = self.frontier['std'].iloc[0], self.frontier['std'].iloc[-1]
        return mu_range, std_range

    def get_range(self) -> Tuple[List[float], List[float]]:
        """
        :return: the range of the current model
        """

        model = self.get_model()
        mu_range = [model.r.min(), model.r.max()]
        std_range = [model.std.min(), model.std.max()]

        if self.frontier is not None:
            # account for frontier
            fmu_range, fstd_range = self.get_frontier_range()
            mu_range = min(mu_range[0], fmu_range[0]), max(mu_range[1], fmu_range[1])
            std_range = min(std_range[0], fstd_range[0]), max(std_range[1], fstd_range[1])

        return mu_range, std_range

    def get_return_and_variance(self) -> Tuple[float, float]:
        """
        :return: the return and standard deviation of the current portfolio
        """
        return self.get_model().return_and_variance(self.portfolio['value (%)'])

    def get_unconstrained_frontier(self, x_bar: float=1.):
        """
        :return: the unconstrained frontier parameters
        """
        return self.get_model().unconstrained_frontier(x_bar)

    def remove_constraints(self, tickers: List[str]) -> None:
        """
        Remove all individual constraints on the listed tickers

        :param tickers: the list of tickers
        """

        # quick return
        if not tickers:
            return

        self.portfolio.loc[tickers, 'lower'] = -np.inf
        self.portfolio.loc[tickers, 'upper'] = np.inf

    def apply_constraint(self, tickers: List[str],
                         function: ConstraintFunctionLiteral,
                         sign: ConstraintSignLiteral,
                         value: Union[List[float], npt.NDArray, float, int],
                         unit: ConstraintUnitLiteral,
                         short_sales: bool=True, buy: bool=True, sell: bool=True) -> None:
        """
        Apply constraints to list of tickers

        :param tickers: the list of tickers
        :param function: the function to apply on the left-hand side of the inequality
        :param sign: the sign of the inequality
        :param value: the value of the right-hand side of the inequality
        :param unit: the unit in which the constraint is expressed
        :param short_sales: whether to allow short sales
        :param buy: whether to allow buying
        :param sell: whether to allow selling
        """
        # quick return
        if not tickers:
            return

        # make sure value is array
        if isinstance(value, (int, float)):
            value = np.array([value] * len(tickers), dtype='float64')
        elif isinstance(value, list):
            value = np.array(value)
        elif isinstance(value, np.ndarray):
            value = value.copy()
        else:
            raise ValueError("value must be int, float, list or NDArray")

        # make sure value is in shares
        shares = self.portfolio.loc[tickers, 'shares'].values
        if unit == 'value':
            close = self.portfolio.loc[tickers, 'close ($)'].values
            value /= close
        elif unit == 'percent value':
            value *= shares / 100

        # initialize
        lb, ub = None, None

        # sales
        if function == 'sales':
            if sign == LESS_THAN_OR_EQUAL:
                lb = shares - value
            elif sign == GREATER_THAN_OR_EQUAL:
                ub = shares - value
            elif sign == EQUAL:
                ub = shares - value
                lb = ub
        elif function == 'purchases':
            if sign == LESS_THAN_OR_EQUAL:
                ub = shares + value
            elif sign == GREATER_THAN_OR_EQUAL:
                lb = shares + value
            elif sign == EQUAL:
                ub = shares + value
                lb = ub
        elif function == 'short sales':
            if sign == LESS_THAN_OR_EQUAL:
                lb = -value
            elif sign == GREATER_THAN_OR_EQUAL:
                ub = -value
            elif sign == EQUAL:
                ub = -value
                lb = ub
        elif function == 'holdings':
            if sign == LESS_THAN_OR_EQUAL:
                ub = value
            elif sign == GREATER_THAN_OR_EQUAL:
                lb = value
            elif sign == EQUAL:
                ub = value
                lb = ub

        # short sales
        if not short_sales:
            if lb is not None:
                lb = np.where(lb > 0, lb, 0)
            if ub is not None:
                ub = np.where(ub > 0, ub, 0)

        # no buys
        if not buy:
            if lb is not None:
                lb = np.where(lb > shares, shares, lb)
            if ub is not None:
                ub = np.where(ub > shares, shares, ub)

        # no sells
        if not sell:
            if lb is not None:
                lb = np.where(lb < shares, shares, lb)
            if ub is not None:
                ub = np.where(ub < shares, shares, ub)

        # apply bounds
        if sign == EQUAL:
            self.portfolio.loc[tickers, 'lower'] = lb
            self.portfolio.loc[tickers, 'upper'] = ub
        else:
            if lb is not None:
                self.portfolio.loc[tickers, 'lower'] = np.maximum(self.portfolio.loc[tickers, 'lower'], lb)

            if ub is not None:
                self.portfolio.loc[tickers, 'upper'] = np.minimum(self.portfolio.loc[tickers, 'upper'], ub)

    def _get_group_constraint(self,
                              group: str,
                              function: GroupConstraintFunctionLiteral) -> Tuple[int, Optional[dict]]:
        for i, c in enumerate(self.group_constraints):
            if c['function'] == function and c['set'] == group:
                return i, c
        return -1, None

    def create_group(self, label: str, tickers: List[str]) -> None:
        """
        Create group

        :param label: the group label
        :param tickers: the group tickers
        """
        if label in self.groups:
            raise ValueError(f"Group {label} is already in the current portfolio.")
        unknown_tickers = set(tickers) - set(self.get_tickers())
        if unknown_tickers:
            raise ValueError(f"Tickers {list(unknown_tickers)} are not in the current portfolio.")
        self.groups[label] = tickers

    def remove_group(self, label: str) -> None:
        """
        Remove group and all its constraints

        :param label: the group label
        """
        if label not in self.groups:
            raise ValueError(f"Group {label} is not in the current portfolio.")
        # remove constraints first
        self.group_constraints = [c for c in self.group_constraints if c['set'] != label]
        # then remove group
        del self.groups[label]

    def remove_group_constraint(self,
                                group: str,
                                function: GroupConstraintFunctionLiteral) -> Optional[dict]:
        """
        Remove group constraints

        :param group: the group
        :param function: the function
        """
        index, constraint = self._get_group_constraint(group, Portfolio.FunctionTable[function])
        if index >= 0:
            del self.group_constraints[index]
        return constraint

    def apply_group_constraint(self,
                               group: str,
                               function: GroupConstraintFunctionLiteral,
                               sign: ConstraintSignLiteral,
                               value: Union[float, int],
                               unit: GroupConstraintUnitLiteral,
                               short_sales: bool = True, buy: bool = True,
                               sell: bool = True) -> None:
        """
        Add group constraint

        :param group: the group label
        :param function: the function to apply on the left-hand side of the inequality
        :param sign: the sign of the inequality
        :param value: the value of the right-hand side of the inequality
        :param unit: the unit in which the constraint is expressed
        :param short_sales: whether to allow short sales
        :param buy: whether to allow buying
        :param sell: whether to allow selling
        """
        # make sure value is scalar
        if not isinstance(value, (int, float)):
            raise ValueError("value must be int or float")

        # make sure group exists
        if group not in self.groups:
            raise ValueError("group does not exist")

        # short sales
        if not short_sales and function == 'short sales':
            raise ValueError('short sales are not currently allowed')

        # no buys
        if not buy and function == 'purchases':
            raise ValueError('purchases are not currently allowed')

        # no sells
        if not sell and function == 'sales':
            raise ValueError('sales are not currently allowed')

        # check sign
        if function == 'sales' or function == 'purchases' or function == 'short sales':
            if sign == GREATER_THAN_OR_EQUAL:
                raise ValueError('greater than or equal inequality not supported')
            elif sign == EQUAL:
                raise ValueError('equality not supported')

        # make sure value is in dollars
        tickers = self.groups[group]
        shares = self.portfolio.loc[tickers, 'shares'].values
        close = self.portfolio.loc[tickers, 'close ($)'].values
        dollars = shares * close
        if unit == 'percent value':
            value *= dollars.sum() / 100
        elif unit != 'value':
            raise ValueError(f"unit '{unit}' is not supported")

        # translate function
        function = Portfolio.FunctionTable[function]

        # is there already a constraint of the same type?
        index, constraint = self._get_group_constraint(group, function)
        if constraint is None:
            # create constraint if needed
            constraint = {
                'set': group,
                'function': function,
                'bounds': np.inf if function == 'sales' or function == 'buys' or function == 'leverage' else [-np.inf, np.inf]
            }

        # set bounds
        if function == 'sales' or function == 'buys' or function == 'leverage':
            constraint['bounds'] = min(value, constraint['bounds'])
        else:
            if sign == LESS_THAN_OR_EQUAL:
                constraint['bounds'][1] = min(value, constraint['bounds'][1])
            elif sign == GREATER_THAN_OR_EQUAL:
                constraint['bounds'][0] = max(value, constraint['bounds'][0])
            elif sign == EQUAL:
                constraint['bounds'] = [value, value]

            # check bounds
            if constraint['bounds'][0] > constraint['bounds'][1]:
                raise ValueError('constraint lower bound is larger than upper bound')

        # create constraint?
        if index == -1:
            self.group_constraints.append(constraint)
        else:
            self.group_constraints[index] = constraint

    def get_group_dataframe(self, x: Optional[npt.NDArray]=None, cashflow: float=0):
        """
        :param x: the portfolio weights (default=None)
        :param cashflow: the cashflow (default=0)
        :return: the portfolio groups as a dataframe
        """

        if not self.groups:
            return pd.DataFrame(columns=['group', 'tickers', 'return (%)', 'std (%)', 'value ($)', 'value (%)'])

        # create dataframe
        data = [{'group': k, 'tickers': v}  for k, v in self.groups.items()]
        df = pd.DataFrame(data=data)
        df.set_index('group', inplace=True)

        if self.has_prices():
            h0 = self.get_value()
            h = h0 + cashflow
            x0 = self.portfolio['value (%)']

            if x is None:
                x = x0
                recommendation = False
                assert cashflow == 0, 'cashflow must be zero without a recommendation'
            else:
                recommendation = True

            value = x * h
            change = value - self.portfolio['value ($)']

            model = self.get_model() if self.has_models() else None
            data_val = np.zeros((len(self.groups), 2))
            data_ret = np.zeros((len(self.groups), 2))
            data_chg = np.zeros((len(self.groups), 3))
            for i, (group, tickers) in enumerate(self.groups.items()):
                # group indices
                index = x0.index.isin(tickers)
                # calculate group value and weight
                val, weight = value[index].sum(), x[index].sum()
                data_val[i, :] = [val, weight]
                # calculate group weights
                xg = x.copy()
                xg[~index] = 0.0
                xg /= xg.sum()
                if model is not None:
                    # calculate group return and variance
                    mu, std = model.return_and_variance(xg)
                    data_ret[i, :] = [mu, std]
                if recommendation:
                    # calculate change
                    change_ = change[index]
                    data_chg[i, :] = [
                        change_.sum(), change_[change_ >= 0].sum(), -change_[change_ <= 0].sum()
                    ]
            # assemble data frame
            if model is not None:
                df[['return (%)', 'std (%)']] = data_ret
            df[['value ($)', 'value (%)']] = data_val
            if recommendation:
                df[['change ($)', 'purchases ($)', 'sales ($)']] = data_chg

        return df
