from datetime import datetime, timedelta

import pandas as pd
import pytest

from stellar_stats.roundtrip import extract_roundtrips


def test_extract_round_trips():
    # Create sample trade data
    trades = pd.DataFrame(
        {
            "trading_day": [
                datetime(2023, 1, 2).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 3).date(),
            ],
            "timestamp": [
                datetime(2023, 1, 2, 10, 0),
                datetime(2023, 1, 3, 11, 0),
                datetime(2023, 1, 3, 12, 0),
                datetime(2023, 1, 3, 13, 0),
            ],
            "symbol": ["AAPL", "AAPL", "AAPL", "AAPL"],
            "side": ["BUY", "SELL", "SELL", "BUY"],
            "price": [100, 102, 98, 105],
            "volume": [100, 50, 50, 200],
            "value": [10000, 5100, 4900, 21000],
            "pnl": [0, 90, -110, 0],
            "commission": [10, 5, 5, 20],
        }
    )

    result = extract_roundtrips(trades.drop(columns=["commission"]))
    assert len(result) == 1
    assert result["pnl"].sum() == pytest.approx(-20)
    assert result["duration"].iloc[0] == timedelta(days=1)
    assert result["pos_type"].iloc[0] == "LONG"


def test_extract_round_trips_long_to_short():
    trades = pd.DataFrame(
        {
            "trading_day": [
                datetime(2023, 1, 2).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 4).date(),
                datetime(2023, 1, 5).date(),
            ],
            "timestamp": [
                datetime(2023, 1, 2, 10, 0),
                datetime(2023, 1, 3, 11, 0),
                datetime(2023, 1, 4, 12, 0),
                datetime(2023, 1, 5, 13, 0),
            ],
            "symbol": ["AAPL", "AAPL", "AAPL", "AAPL"],
            "side": ["BUY", "SELL", "SELL", "BUY"],
            "price": [100, 105, 102, 99],
            "volume": [100, 50, 100, 50],
            "value": [10000, 5250, 10200, 4950],
            "pnl": [0, 240, 90, 140],
            "commission": [10, 5, 10, 5],
        }
    )

    result = extract_roundtrips(trades.drop(columns=["commission"]))

    assert len(result) == 3
    assert result["pnl"].sum() == pytest.approx(470)
    assert result["pos_type"].iloc[0] == "LONG"  # First partial close long
    assert result["pos_type"].iloc[1] == "LONG"  # Second close remaining long
    assert result["pos_type"].iloc[2] == "SHORT"  # Close short position
    assert result["pos_size"].iloc[0] == 50  # Partial close volume
    assert result["pos_size"].iloc[1] == 50  # Remaining long close volume
    assert result["pos_size"].iloc[2] == 50  # Short close volume


def test_extract_round_trips_multiple_symbols():
    trades = pd.DataFrame(
        {
            "trading_day": [
                datetime(2023, 1, 2).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 4).date(),
                datetime(2023, 1, 5).date(),
            ],
            "timestamp": [
                datetime(2023, 1, 2, 10, 0),
                datetime(2023, 1, 3, 11, 0),
                datetime(2023, 1, 4, 12, 0),
                datetime(2023, 1, 5, 13, 0),
            ],
            "symbol": ["AAPL", "GOOGL", "AAPL", "GOOGL"],
            "side": ["BUY", "BUY", "SELL", "SELL"],
            "price": [100, 1000, 105, 1050],
            "volume": [100, 10, 100, 10],
            "value": [10000, 10000, 10500, 10500],
            "pnl": [0, 0, 480, 480],
            "commission": [10, 10, 10, 10],
        }
    )

    result = extract_roundtrips(trades.drop(columns=["commission"]))

    assert len(result) == 2
    assert set(result["symbol"]) == {"AAPL", "GOOGL"}
    assert result.loc[result["symbol"] == "AAPL", "pnl"].iloc[0] == pytest.approx(480)
    assert result.loc[result["symbol"] == "GOOGL", "pnl"].iloc[0] == pytest.approx(480)
    assert all(result["pos_type"] == "LONG")


def test_extract_round_trips_partial_close():
    trades = pd.DataFrame(
        {
            "trading_day": [
                datetime(2023, 1, 2).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 4).date(),
            ],
            "timestamp": [
                datetime(2023, 1, 2, 10, 0),
                datetime(2023, 1, 3, 11, 0),
                datetime(2023, 1, 4, 12, 0),
            ],
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "side": ["BUY", "SELL", "SELL"],
            "price": [100, 105, 110],
            "volume": [100, 50, 25],
            "value": [10000, 5250, 2750],
            "pnl": [0, 240, 245],
            "commission": [10, 5, 2.5],
        }
    )

    result = extract_roundtrips(trades.drop(columns=["commission"]))

    assert len(result) == 2
    assert result["pnl"].sum() == pytest.approx(485)
    assert all(result["pos_type"] == "LONG")


def test_extract_round_trips_start_with_sell():
    trades = pd.DataFrame(
        {
            "trading_day": [
                datetime(2023, 1, 2).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 4).date(),
            ],
            "timestamp": [
                datetime(2023, 1, 2, 10, 0),
                datetime(2023, 1, 3, 11, 0),
                datetime(2023, 1, 4, 12, 0),
            ],
            "symbol": ["AAPL", "AAPL", "AAPL"],
            "side": ["SELL", "BUY", "SELL"],
            "price": [100, 95, 105],
            "volume": [50, 50, 50],
            "value": [5000, 4750, 5250],
            "pnl": [0, 240, 0],
            "commission": [5, 5, 5],
        }
    )

    result = extract_roundtrips(trades.drop(columns=["commission"]))

    assert len(result) == 1
    assert result["pnl"].sum() == pytest.approx(240)
    assert result["duration"].iloc[0] == timedelta(days=1)
    assert result["pos_type"].iloc[0] == "SHORT"


def test_extract_round_trips_dual_positions():
    trades = pd.DataFrame(
        {
            "trading_day": [
                datetime(2023, 1, 1).date(),
                datetime(2023, 1, 1).date(),
                datetime(2023, 1, 2).date(),
                datetime(2023, 1, 2).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 3).date(),
            ],
            "timestamp": [
                datetime(2023, 1, 1, 10, 0),
                datetime(2023, 1, 1, 11, 0),
                datetime(2023, 1, 2, 10, 0),
                datetime(2023, 1, 2, 11, 0),
                datetime(2023, 1, 3, 10, 0),
                datetime(2023, 1, 3, 11, 0),
            ],
            "symbol": ["IF2302"] * 6,
            "side": [
                "BUY_OPEN",
                "SELL_OPEN",
                "SELL_CLOSE",
                "BUY_CLOSE",
                "BUY_OPEN",
                "SELL_OPEN",
            ],
            "price": [100, 102, 105, 98, 103, 104],
            "volume": [100, 50, 100, 50, 50, 30],
            "value": [10000, 5100, 10500, 4900, 5150, 3120],
            "pnl": [0, 0, 500, 200, 0, 0],
            "commission": [10, 5, 10, 5, 5, 3],
        }
    )

    result = extract_roundtrips(trades)

    assert len(result) == 2

    # Test long position round trip
    long_rt = result[result["pos_type"] == "LONG"].iloc[0]
    assert long_rt["pnl"] == pytest.approx(480)
    assert long_rt["duration"] == timedelta(days=1)

    # Test short position round trip
    short_rt = result[result["pos_type"] == "SHORT"].iloc[0]
    assert short_rt["pnl"] == pytest.approx(190)
    assert short_rt["duration"] == timedelta(days=1)


def test_extract_round_trips_mixed_positions():
    trades = pd.DataFrame(
        {
            "trading_day": [
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 3).date(),
                datetime(2023, 1, 4).date(),
                datetime(2023, 1, 4).date(),
            ],
            "timestamp": [
                datetime(2023, 1, 3, 10, 0),
                datetime(2023, 1, 3, 11, 0),
                datetime(2023, 1, 4, 10, 0),
                datetime(2023, 1, 4, 11, 0),
            ],
            "symbol": ["IF2302", "SC2302", "IF2302", "SC2302"],
            "side": ["SELL_OPEN", "BUY_OPEN", "BUY_CLOSE", "SELL_CLOSE"],
            "price": [103, 105, 99, 108],
            "volume": [50, 80, 50, 80],
            "value": [5150, 8400, 4950, 8640],
            "pnl": [0, 0, 200, 240],
            "commission": [5, 8, 5, 8],
        }
    )

    result = extract_roundtrips(trades)

    assert len(result) == 2

    # Test IF2302 short position round trip
    if2302_short = result[
        (result["symbol"] == "IF2302") & (result["pos_type"] == "SHORT")
    ].iloc[0]
    assert if2302_short["pnl"] == pytest.approx(190)
    assert if2302_short["duration"] == timedelta(days=1)

    # Test SC2302 long position round trip
    sc2302_long = result[
        (result["symbol"] == "SC2302") & (result["pos_type"] == "LONG")
    ].iloc[0]
    assert sc2302_long["pnl"] == pytest.approx(224)
    assert sc2302_long["duration"] == timedelta(days=1)
