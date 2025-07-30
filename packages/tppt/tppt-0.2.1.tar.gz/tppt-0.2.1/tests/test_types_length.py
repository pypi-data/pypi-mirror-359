import pytest

from tppt.types._length import (
    CentiMeters,
    EnglishMetricUnits,
    Inches,
    MilliMeters,
    Points,
    to_centi_meters,
    to_english_metric_units,
    to_inches,
    to_length,
    to_literal_length,
    to_milli_meters,
    to_points,
)


def test_to_centimeter():
    """Test conversion to centimeters"""
    # Test from inches
    assert to_centi_meters(Inches(1)).value == 2.54
    assert to_centi_meters((1.0, "in")).value == 2.54

    # Test from points
    assert to_centi_meters(Points(72)).value == 2.54
    assert to_centi_meters((72, "pt")).value == 2.54

    # Test from centimeters
    assert to_centi_meters(CentiMeters(2.54)).value == 2.54
    assert to_centi_meters((2.54, "cm")).value == 2.54

    # Test from millimeters
    assert to_centi_meters(MilliMeters(25.4)).value == 2.54
    assert to_centi_meters((25.4, "mm")).value == 2.54

    # Test from EMU
    assert to_centi_meters(EnglishMetricUnits(914400)).value == 2.54
    assert to_centi_meters((914400, "emu")).value == 2.54


def test_to_inche():
    """Test conversion to inches"""
    # Test from inches
    assert to_inches(Inches(1)).value == 1.0
    assert to_inches((1.0, "in")).value == 1.0

    # Test from points
    assert to_inches(Points(72)).value == 1.0
    assert to_inches((72, "pt")).value == 1.0

    # Test from centimeters
    assert to_inches(CentiMeters(2.54)).value == 1.0
    assert to_inches((2.54, "cm")).value == 1.0

    # Test from millimeters
    assert to_inches(MilliMeters(25.4)).value == 1.0
    assert to_inches((25.4, "mm")).value == 1.0

    # Test from EMU
    assert to_inches(EnglishMetricUnits(914400)).value == 1.0
    assert to_inches((914400, "emu")).value == 1.0


def test_to_point():
    """Test conversion to points"""
    # Test from inches
    assert to_points(Inches(1)).value == 72
    assert to_points((1.0, "in")).value == 72

    # Test from points
    assert to_points(Points(72)).value == 72
    assert to_points((72, "pt")).value == 72

    # Test from centimeters
    assert to_points(CentiMeters(2.54)).value == 72
    assert to_points((2.54, "cm")).value == 72

    # Test from millimeters
    assert to_points(MilliMeters(25.4)).value == 72
    assert to_points((25.4, "mm")).value == 72

    # Test from EMU
    assert to_points(EnglishMetricUnits(914400)).value == 72
    assert to_points((914400, "emu")).value == 72


def test_to_millimeter():
    """Test conversion to millimeters"""
    # Test from inches
    assert to_milli_meters(Inches(1)).value == 25.4
    assert to_milli_meters((1.0, "in")).value == 25.4

    # Test from points
    assert to_milli_meters(Points(72)).value == 25.4
    assert to_milli_meters((72, "pt")).value == 25.4

    # Test from centimeters
    assert to_milli_meters(CentiMeters(2.54)).value == 25.4
    assert to_milli_meters((2.54, "cm")).value == 25.4

    # Test from millimeters
    assert to_milli_meters(MilliMeters(25.4)).value == 25.4
    assert to_milli_meters((25.4, "mm")).value == 25.4

    # Test from EMU
    assert to_milli_meters(EnglishMetricUnits(914400)).value == 25.4
    assert to_milli_meters((914400, "emu")).value == 25.4


def test_to_emu():
    """Test conversion to EMU"""
    # Test from inches
    assert to_english_metric_units(Inches(1)).value == 914400
    assert to_english_metric_units((1.0, "in")).value == 914400

    # Test from points
    assert to_english_metric_units(Points(72)).value == 914400
    assert to_english_metric_units((72, "pt")).value == 914400

    # Test from centimeters
    assert to_english_metric_units(CentiMeters(2.54)).value == 914400
    assert to_english_metric_units((2.54, "cm")).value == 914400

    # Test from millimeters
    assert to_english_metric_units(MilliMeters(25.4)).value == 914400
    assert to_english_metric_units((25.4, "mm")).value == 914400

    # Test from EMU
    assert to_english_metric_units(EnglishMetricUnits(914400)).value == 914400
    assert to_english_metric_units((914400, "emu")).value == 914400


def test_internal_length_operations():
    """Test operations on internal length representations"""
    # Test addition
    assert (Inches(1) + Inches(1)).value == 2.0
    assert (Points(72) + Points(72)).value == 144
    assert (CentiMeters(2.54) + CentiMeters(2.54)).value == 5.08
    assert (MilliMeters(25.4) + MilliMeters(25.4)).value == 50.8
    assert (EnglishMetricUnits(914400) + EnglishMetricUnits(914400)).value == 1828800

    # Test addition with Length tuples
    assert (Inches(1) + (1.0, "in")).value == 2.0
    assert (Points(72) + (72, "pt")).value == 144
    assert (CentiMeters(2.54) + (2.54, "cm")).value == 5.08
    assert (MilliMeters(25.4) + (25.4, "mm")).value == 50.8
    assert (EnglishMetricUnits(914400) + (914400, "emu")).value == 1828800

    # Test subtraction
    assert (Inches(2) - Inches(1)).value == 1.0
    assert (Points(144) - Points(72)).value == 72
    assert (CentiMeters(5.08) - CentiMeters(2.54)).value == 2.54
    assert (MilliMeters(50.8) - MilliMeters(25.4)).value == 25.4
    assert (EnglishMetricUnits(1828800) - EnglishMetricUnits(914400)).value == 914400

    # Test subtraction with Length tuples
    assert (Inches(2) - (1.0, "in")).value == 1.0
    assert (Points(144) - (72, "pt")).value == 72
    assert (CentiMeters(5.08) - (2.54, "cm")).value == 2.54
    assert (MilliMeters(50.8) - (25.4, "mm")).value == 25.4
    assert (EnglishMetricUnits(1828800) - (914400, "emu")).value == 914400

    # Test multiplication
    assert (Inches(1) * 2).value == 2.0
    assert (Points(72) * 2).value == 144
    assert (CentiMeters(2.54) * 2).value == 5.08
    assert (MilliMeters(25.4) * 2).value == 50.8
    assert (EnglishMetricUnits(914400) * 2).value == 1828800

    # Test division
    assert (Inches(2) / 2).value == 1.0
    assert (Points(144) / 2).value == 72
    assert (CentiMeters(5.08) / 2).value == 2.54
    assert (MilliMeters(50.8) / 2).value == 25.4
    assert (EnglishMetricUnits(1828800) / 2).value == 914400

    # Test in-place operations with Length tuples
    inch = Inches(1)
    inch += (1.0, "in")
    assert inch.value == 2.0

    point = Points(72)
    point += (72, "pt")
    assert point.value == 144

    cm = CentiMeters(2.54)
    cm += (2.54, "cm")
    assert cm.value == 5.08

    mm = MilliMeters(25.4)
    mm += (25.4, "mm")
    assert mm.value == 50.8

    emu = EnglishMetricUnits(914400)
    emu += (914400, "emu")
    assert emu.value == 1828800

    inch = Inches(2)
    inch -= (1.0, "in")
    assert inch.value == 1.0

    point = Points(144)
    point -= (72, "pt")
    assert point.value == 72

    cm = CentiMeters(5.08)
    cm -= (2.54, "cm")
    assert cm.value == 2.54

    mm = MilliMeters(50.8)
    mm -= (25.4, "mm")
    assert mm.value == 25.4

    emu = EnglishMetricUnits(1828800)
    emu -= (914400, "emu")
    assert emu.value == 914400


def test_conversion_between_units():
    """Test conversion between different units"""
    # Test inch to point
    assert to_points(Inches(1)).value == 72
    assert to_points((1.0, "in")).value == 72

    # Test inch to centimeter
    assert to_centi_meters(Inches(1)).value == 2.54
    assert to_centi_meters((1.0, "in")).value == 2.54

    # Test inch to millimeter
    assert to_milli_meters(Inches(1)).value == 25.4
    assert to_milli_meters((1.0, "in")).value == 25.4

    # Test inch to EMU
    assert to_english_metric_units(Inches(1)).value == 914400
    assert to_english_metric_units((1.0, "in")).value == 914400

    # Test point to inch
    assert to_inches(Points(72)).value == 1.0
    assert to_inches((72, "pt")).value == 1.0

    # Test point to centimeter
    assert to_centi_meters(Points(72)).value == 2.54
    assert to_centi_meters((72, "pt")).value == 2.54

    # Test point to millimeter
    assert to_milli_meters(Points(72)).value == 25.4
    assert to_milli_meters((72, "pt")).value == 25.4

    # Test point to EMU
    assert to_english_metric_units(Points(72)).value == 914400
    assert to_english_metric_units((72, "pt")).value == 914400

    # Test centimeter to inch
    assert to_inches(CentiMeters(2.54)).value == 1.0
    assert to_inches((2.54, "cm")).value == 1.0

    # Test centimeter to point
    assert to_points(CentiMeters(2.54)).value == 72
    assert to_points((2.54, "cm")).value == 72

    # Test centimeter to millimeter
    assert to_milli_meters(CentiMeters(2.54)).value == 25.4
    assert to_milli_meters((2.54, "cm")).value == 25.4

    # Test centimeter to EMU
    assert to_english_metric_units(CentiMeters(2.54)).value == 914400
    assert to_english_metric_units((2.54, "cm")).value == 914400

    # Test millimeter to inch
    assert to_inches(MilliMeters(25.4)).value == 1.0
    assert to_inches((25.4, "mm")).value == 1.0

    # Test millimeter to point
    assert to_points(MilliMeters(25.4)).value == 72
    assert to_points((25.4, "mm")).value == 72

    # Test millimeter to centimeter
    assert to_centi_meters(MilliMeters(25.4)).value == 2.54
    assert to_centi_meters((25.4, "mm")).value == 2.54

    # Test millimeter to EMU
    assert to_english_metric_units(MilliMeters(25.4)).value == 914400
    assert to_english_metric_units((25.4, "mm")).value == 914400

    # Test EMU to inch
    assert to_inches(EnglishMetricUnits(914400)).value == 1.0
    assert to_inches((914400, "emu")).value == 1.0

    # Test EMU to point
    assert to_points(EnglishMetricUnits(914400)).value == 72
    assert to_points((914400, "emu")).value == 72

    # Test EMU to centimeter
    assert to_centi_meters(EnglishMetricUnits(914400)).value == 2.54
    assert to_centi_meters((914400, "emu")).value == 2.54

    # Test EMU to millimeter
    assert to_milli_meters(EnglishMetricUnits(914400)).value == 25.4
    assert to_milli_meters((914400, "emu")).value == 25.4


def test_internal_to_public_conversion():
    """Test conversion between internal and public representations"""
    # Test inch conversion
    assert to_length((1.0, "in")) == Inches(1.0)
    assert to_literal_length(Inches(1.0), "in") == (1.0, "in")
    assert to_literal_length(Inches(1.0), "cm") == (2.54, "cm")
    assert to_literal_length(Inches(1.0), "pt") == (72, "pt")
    assert to_literal_length(Inches(1.0), "mm") == (25.4, "mm")
    assert to_literal_length(Inches(1.0), "emu") == (914400, "emu")

    # Test point conversion
    assert to_length((72, "pt")) == Points(72)
    assert to_literal_length(Points(72), "in") == (1.0, "in")
    assert to_literal_length(Points(72), "cm") == (2.54, "cm")
    assert to_literal_length(Points(72), "pt") == (72, "pt")
    assert to_literal_length(Points(72), "mm") == (25.4, "mm")
    assert to_literal_length(Points(72), "emu") == (914400, "emu")

    # Test centimeter conversion
    assert to_length((2.54, "cm")) == CentiMeters(2.54)
    assert to_literal_length(CentiMeters(2.54), "in") == (1.0, "in")
    assert to_literal_length(CentiMeters(2.54), "cm") == (2.54, "cm")
    assert to_literal_length(CentiMeters(2.54), "pt") == (72, "pt")
    assert to_literal_length(CentiMeters(2.54), "mm") == (25.4, "mm")
    assert to_literal_length(CentiMeters(2.54), "emu") == (914400, "emu")

    # Test millimeter conversion
    assert to_length((25.4, "mm")) == MilliMeters(25.4)
    assert to_literal_length(MilliMeters(25.4), "in") == (1.0, "in")
    assert to_literal_length(MilliMeters(25.4), "cm") == (2.54, "cm")
    assert to_literal_length(MilliMeters(25.4), "pt") == (72, "pt")
    assert to_literal_length(MilliMeters(25.4), "mm") == (25.4, "mm")
    assert to_literal_length(MilliMeters(25.4), "emu") == (914400, "emu")

    # Test EMU conversion
    assert to_length((914400, "emu")) == EnglishMetricUnits(914400)
    assert to_literal_length(EnglishMetricUnits(914400), "in") == (1.0, "in")
    assert to_literal_length(EnglishMetricUnits(914400), "cm") == (2.54, "cm")
    assert to_literal_length(EnglishMetricUnits(914400), "pt") == (72, "pt")
    assert to_literal_length(EnglishMetricUnits(914400), "mm") == (25.4, "mm")
    assert to_literal_length(EnglishMetricUnits(914400), "emu") == (914400, "emu")


def test_invalid_unit():
    """Test handling of invalid units"""
    with pytest.raises(AssertionError):
        to_length((1.0, "invalid"))  # type: ignore

    with pytest.raises(AssertionError):
        to_literal_length(Inches(1.0), "invalid")  # type: ignore
