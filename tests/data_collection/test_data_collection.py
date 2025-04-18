from typing import AnyStr
from unittest.mock import MagicMock

import pytest
from _pytest.capture import CaptureFixture

from app.services.data_collection import DataCollectionService
from tests.data_collection.data.dividends import DIVIDENDS_0_capture, DIVIDENDS_1_capture
from tests.data_collection.data.moex_0 import MOEX_0_capture
from tests.data_collection.data.moex_1 import MOEX_1_capture

data_lst = [
    MOEX_0_capture, MOEX_1_capture, '',
    DIVIDENDS_0_capture, DIVIDENDS_1_capture
]


@pytest.mark.usefixtures("mockers")
class TestDataCollection:
    @pytest.mark.parametrize(
        "start, page, mockers", [
            (0, 0, (0, 0)),
            (0, 1, (1, 2)),
            (1, 1, (0, 1)),
            (1, 1, (1, 1))
        ], indirect=["mockers"]
    )
    async def test_get_information(
            self,
            start: int,
            page: int,
            capsys: CaptureFixture[AnyStr],
            mockers: MagicMock
    ) -> None:
        _, index = await DataCollectionService().get_information('', start)
        captured = capsys.readouterr()
        assert captured.out == data_lst[mockers]
        assert index.ind == page

    @pytest.mark.parametrize(
        "mockers", [
            # (3, 2),
            (1, 3),
            (2, 4),
        ], indirect=["mockers"]
    )
    async def test_get_dividends(
            self,
            capsys: CaptureFixture[AnyStr],
            mockers: MagicMock
    ) -> None:
        await DataCollectionService().get_dividends('')
        captured = capsys.readouterr()
        assert captured.out == data_lst[mockers]
