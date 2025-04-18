from typing import Any
from unittest.mock import MagicMock

import pytest
from _pytest.fixtures import FixtureRequest
from loguru import logger

from tests.data_collection.data.dividends import DIVIDENDS_1, DIVIDENDS_0
from tests.data_collection.data.moex_0 import MOEX_0
from tests.data_collection.data.moex_1 import MOEX_1

data = [
    MOEX_0, MOEX_1, MOEX_0,
    DIVIDENDS_0, DIVIDENDS_1
]


@pytest.fixture(scope='function')
async def mockers(request: FixtureRequest, mocker: MagicMock) -> Any:
    logger.remove()
    flag_inx, data_ind = request.param

    mock_response = mocker.MagicMock()
    mock_response.return_value.__aenter__.return_value.text.return_value = data[data_ind]
    mock_response.return_value.__aenter__.return_value.raise_for_status = mocker.MagicMock()

    mock_db_read_flag = mocker.AsyncMock(
        return_value=flag_inx
    )

    mock_db_update = mocker.AsyncMock(
        side_effect=print
    )

    mocker.patch("aiohttp.ClientSession.get", mock_response)
    mocker.patch("app.repositories.results_trades.ResultsTradesRepository.db_read_flag", mock_db_read_flag)
    mocker.patch("app.repositories.results_trades.ResultsTradesRepository.db_update", mock_db_update)

    mocker.patch("app.repositories.dividends.DividendsRepository.db_read_flag", mock_db_read_flag)
    mocker.patch("app.repositories.dividends.DividendsRepository.db_update", mock_db_update)

    return data_ind
