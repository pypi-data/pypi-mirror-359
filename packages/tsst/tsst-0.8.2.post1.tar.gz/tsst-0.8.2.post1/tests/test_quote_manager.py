import os

import polars as pl
import polars_talib as plta
import pytest
from dotenv import load_dotenv
from polars.testing import assert_frame_equal

from tsst.broker.__init__ import QuoteManager
from tsst.main import Tsst

load_dotenv(override=True)

broker = "Sino"
tsst = Tsst(is_simulation=True, use_broker=broker, is_backtest=True)
qm = QuoteManager()

tsst.login({
    "email": os.getenv("EMAIL"),
    "tsst_token": os.getenv("TSST_TOKEN"),
    "api_key": os.getenv("API_KEY_PROD"),
    "secret_key": os.getenv("API_SECRET_PROD"),
    "ca_path": os.getenv("CA_PATH"),
    "ca_password": os.getenv("CA_PASSWORD")
    })
tsst.init_quote()

# 測試 add_tick 方法的參數錯誤
# def test_add_tick_arguments_TypeError():
#     """測試 add_tick 方法的參數錯誤"""
#     tick = []
#     with pytest.raises(TypeError) as excinfo:
#         qm.add_tick(tick)
#     assert str(excinfo.value) == "Tick must be a dictionary"

# 測試 add_tick 方法的 market_type 參數錯誤
# def test_add_tick_arguments_detail_TypeError_for_market_type():
#     """測試 add_tick 方法的 market_type 參數錯誤"""
#     tick = {
#         "market_type": 100
#         }
#     with pytest.raises(TypeError) as excinfo:
#         qm.add_tick(tick)
#     assert str(excinfo.value) == "market_type must be 'Stock' or 'Future' in tick dictionary"

# 測試 add_tick 方法的 timestamp 參數錯誤
# def test_add_tick_arguments_detail_TypeError_for_timestamp():
#     """測試 add_tick 方法的 timestamp 參數錯誤"""
#     tick = {
#         "market_type": "Stock",
#         "timestamp": "1704864600.0"
#         }
#     with pytest.raises(TypeError) as excinfo:
#         qm.add_tick(tick)
#     assert str(excinfo.value) == "timestamp must be an integer or float in tick dictionary"

# 測試 add_tick 方法的 code 參數錯誤
# def test_add_tick_arguments_detail_TypeError_for_code():
#     """測試 add_tick 方法的 code 參數錯誤"""
#     tick = {
#         "market_type": "Stock",
#         "timestamp": 1704864600.0,
#         "code": 2330
#         }
#     with pytest.raises(TypeError) as excinfo:
#         qm.add_tick(tick)
#     assert str(excinfo.value) == "code must be a string in tick dictionary"

# 測試 add_tick 方法的 close 參數錯誤
# def test_add_tick_arguments_detail_TypeError_for_close():
#     """測試 add_tick 方法的 close 參數錯誤"""
#     tick = {
#         "market_type": "Stock",
#         "timestamp": 1704864600.0,
#         "code": "2330",
#         "close": "584.0"
#         }
#     with pytest.raises(TypeError) as excinfo:
#         qm.add_tick(tick)
#     assert str(excinfo.value) == "close must be an integer or float in tick dictionary"

# 測試 add_tick 方法的 qty 參數錯誤
# def test_add_tick_arguments_detail_TypeError_for_qty():
#     """測試 add_tick 方法的 qty 參數錯誤"""
#     tick = {
#         "market_type": "Stock",
#         "timestamp": 1704864600.0,
#         "code": "2330",
#         "close": 584.0,
#         "qty": "2648"
#         }
#     with pytest.raises(TypeError) as excinfo:
#         qm.add_tick(tick)
#     assert str(excinfo.value) == "qty must be an integer in tick dictionary"

# 測試 add_tick 方法的 tick_type 參數錯誤
# def test_add_tick_arguments_detail_TypeError_for_tick_type():
#     """測試 add_tick 方法的 tick_type 參數錯誤"""
#     tick = {
#         "market_type": "Stock",
#         "timestamp": 1704864600.0,
#         "code": "2330",
#         "close": 584.0,
#         "qty": 2648,
#         "tick_type": "2"
#         }
#     with pytest.raises(TypeError) as excinfo:
#         qm.add_tick(tick)
#     assert str(excinfo.value) == "tick_type must be an integer in tick dictionary"

# 測試 add_tick 方法的回傳值是否為 None
def test_add_tick_return_is_None():
    """測試 add_tick 方法的回傳值是否為 None"""
    tick = {
        "market_type": "Stock",
        "timestamp": 1704864600.0,
        "code": "2330",
        "close": 584.0,
        "qty": 2648,
        "tick_type": 2,
        "is_simulate": False,
        "is_backfilling": False
    }
    result = qm.add_tick(tick)
    assert result is None

# 測試 add_tick 方法是否正確補齊虛擬 ticks
def test_add_tick_completing_virtual_ticks_correct():
    """測試 add_tick 方法是否正確補齊虛擬 ticks"""
    qm = QuoteManager()
    # 2025-05-10 13:22~13:30
    ticks = [
        {
            "market_type": "Stock",
            "timestamp": 1704864131.0,
            "code": "2330",
            "close": 584.0,
            "qty": 2648,
            "tick_type": 2,
            "is_simulate": False,
            "is_backfilling": False
        }, {
            "market_type": "Stock",
            "timestamp": 1704864600.0,
            "code": "2330",
            "close": 584.0,
            "qty": 2648,
            "tick_type": 2,
            "is_simulate": False,
            "is_backfilling": False
        }
    ]
    for tick in ticks:
        qm.add_tick(tick)
    assert len(qm.ticks) == 9, f"Expected 9 rows, got {len(qm.ticks)}"

# 測試 get_kbar 方法的 code 參數錯誤
def test_get_kbar_arguments_TypeError_for_code():
    """測試 get_kbar 方法的 code 參數錯誤"""
    with pytest.raises(TypeError) as excinfo:
        qm.get_kbar(code=2330, unit="m", freq=5)
    assert str(excinfo.value) == "'code' must be a string"

# 測試 get_kbar 方法的 unit 參數錯誤
def test_get_kbar_arguments_TypeError_for_unit():
    """測試 get_kbar 方法的 unit 參數錯誤"""
    with pytest.raises(TypeError) as excinfo:
        qm.get_kbar(code="2330", unit=5, freq=5)
    assert str(excinfo.value) == "'unit' must be one of ['m', 'h', 'd', 'w', 'mo', 'q', 'y']"

# 測試 get_kbar 方法的 freq 參數錯誤
def test_get_kbar_arguments_TypeError_for_freq():
    """測試 get_kbar 方法的 freq 參數錯誤"""
    with pytest.raises(TypeError) as excinfo:
        qm.get_kbar(code="2330", unit="m", freq="5")
    assert str(excinfo.value) == "'freq' must be an integer"

# 測試 get_kbar 方法的 exprs 參數錯誤
def test_get_kbar_arguments_TypeError_for_exprs():
    """測試 get_kbar 方法的 exprs 參數錯誤"""
    with pytest.raises(TypeError) as excinfo:
        qm.get_kbar(code="2330", unit="m", freq=5, exprs={})
    assert str(excinfo.value) == "'exprs' must be a list"

# 測試 get_kbar 方法的回傳值是否為 polars 的 DataFrame
def test_get_kbar_return_is_dataframe():
    """測試 get_kbar 方法的回傳值是否為 polars 的 DataFrame"""
    result = qm.get_kbar(code="2330", unit="m", freq=5)
    assert isinstance(result, pl.DataFrame) == True

# 測試 get_kbar 方法的回傳值是否正確
def test_get_kbar_return_result_is_correct():
    """測試 get_kbar 方法的回傳值是否正確"""
    qm = QuoteManager()
    ticks = pl.read_csv("./query_files/unittest_data/add_tick_20250110_sample.csv").to_dicts()
    for tick in ticks:
        tick["code"] = str(tick["code"])

    for tick in ticks:
        qm.add_tick(tick)

    result_df = qm.get_kbar(code="2330", unit="m", freq=5, exprs=[(plta.ma(pl.col("Close"), 20).fill_nan(None).alias("MA20"))])
    result_df = result_df.select(["dt", "Open", "High", "Low", "Close", "MA20"]).tail(20)

    correct_df = (pl.read_csv("./query_files/unittest_data/XQ_2330_20250110_compare_sample.csv"))
    correct_df = correct_df.with_columns([
        pl.concat_str(["Date", "Time"], separator=" ")
        .str.strptime(pl.Datetime, "%Y/%m/%d %H:%M:%S")
        .alias("dt")
    ])
    correct_df = correct_df.with_columns([
        pl.col("Open").cast(pl.Float64),
        pl.col("High").cast(pl.Float64),
        pl.col("Low").cast(pl.Float64),
        pl.col("Close").cast(pl.Float64),
        pl.col("MA20").cast(pl.Float64)
    ]).select(["dt", "Open", "High", "Low", "Close", "MA20"]).tail(20)

    assert result_df.shape == correct_df.shape, f"Expected shape {correct_df.shape}, got {result_df.shape}"
    assert_frame_equal(result_df, correct_df)