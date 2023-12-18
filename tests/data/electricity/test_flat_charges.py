"""
Pytests for flat_charges.py

Date:
    10-09-2023

"""
#pylint: skip-file

import pytest

from data.electricity.flat_charges import FlatCharges


@pytest.fixture
def flat_charges():
    return FlatCharges()

@pytest.fixture
def expected_charges():
    gov_charge = 0.697
    sys_tariff = 0.054
    trans_tariff = 0.058
    total = gov_charge + sys_tariff + trans_tariff
    return { 'Gov': gov_charge, 'Sys': sys_tariff, 'Trans': trans_tariff, 'Total': total }


"""=========================================   TESTS   ==================================================="""

def test_flat_charges_class(flat_charges: FlatCharges, expected_charges: dict[str, float]):
    assert flat_charges.gov_charge == expected_charges['Gov']
    assert flat_charges.sys_tariff == expected_charges['Sys']
    assert flat_charges.trans_tariff == expected_charges['Trans']
    assert flat_charges.total == expected_charges['Total']


def test_flat_charges_repr(flat_charges: FlatCharges):
    expected_str = f"FlatCharges(gov=0.697, sys=0.054, trans=0.058)"

    assert flat_charges.__repr__() == expected_str