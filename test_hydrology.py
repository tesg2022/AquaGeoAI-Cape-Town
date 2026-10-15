import pytest
from app.hydrology import water_availability_screening


def test_water_availability_screening():
    result = water_availability_screening(500, 350)
    assert result["p_minus_et_mm"] == 150
    assert result["units"] == "mm for the specified period"
    assert "not a direct groundwater recharge" in result["interpretation"]


def test_negative_precipitation_rejected():
    with pytest.raises(ValueError):
        water_availability_screening(-1, 100)


def test_negative_et_rejected():
    with pytest.raises(ValueError):
        water_availability_screening(100, -1)
