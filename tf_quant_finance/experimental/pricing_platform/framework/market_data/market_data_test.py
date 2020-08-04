# Lint as: python3
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the market data."""
import tensorflow.compat.v2 as tf

import tf_quant_finance as tff

from tensorflow.python.framework import test_util  # pylint: disable=g-direct-tensorflow-import

core = tff.experimental.pricing_platform.framework.core
market_data = tff.experimental.pricing_platform.framework.market_data
interpolation_method = tff.experimental.pricing_platform.framework.core.interpolation_method


@test_util.run_all_in_graph_and_eager_modes
class MarketDataTest(tf.test.TestCase):

  def setUp(self):
    dates = [[2021, 2, 8], [2022, 2, 8], [2023, 2, 8], [2025, 2, 8],
             [2027, 2, 8], [2030, 2, 8], [2050, 2, 8]]
    discounts = [0.97197441, 0.94022746, 0.91074031, 0.85495089, 0.8013675,
                 0.72494879, 0.37602059]
    libor_3m_config = market_data.config.RateConfig(
        interpolation_method=interpolation_method.InterpolationMethod.LINEAR)

    self._rate_config = {"USD": {"LIBOR_3M": libor_3m_config}}
    risk_free_dates = [
        [2021, 2, 8], [2022, 2, 8], [2023, 2, 8], [2025, 2, 8], [2050, 2, 8]]
    risk_free_discounts = [
        0.97197441, 0.94022746, 0.91074031, 0.85495089, 0.37602059]
    self._market_data_dict = {"USD": {
        "risk_free_curve":
        {"dates": risk_free_dates, "discounts": risk_free_discounts},
        "OIS":
        {"dates": dates, "discounts": discounts},
        "LIBOR_3M":
        {"dates": dates, "discounts": discounts},}}
    self._valuation_date = [(2020, 6, 24)]
    self._libor_discounts = discounts
    self._risk_free_discounts = risk_free_discounts
    super(MarketDataTest, self).setUp()

  def test_discount_curve(self):
    market = market_data.MarketDataDict(
        self._valuation_date,
        self._market_data_dict,
        config=self._rate_config)
    # Get the risk free discount curve
    risk_free_curve_type = core.curve_types.RiskFreeCurve(currency="USD")
    risk_free_curve = market.yield_curve(risk_free_curve_type)
    # Get LIBOR 3M discount
    libor_3m = core.rate_indices.RateIndex(type="LIBOR_3M")
    rate_index_curve_type = core.curve_types.RateIndexCurve(
        currency="USD", index=libor_3m)
    libor_3m_curve = market.yield_curve(rate_index_curve_type)
    with self.subTest("RiskFree"):
      discount_factor_nodes = risk_free_curve.discount_factor_nodes
      self.assertAllClose(discount_factor_nodes, self._risk_free_discounts)
    with self.subTest("LIBOR_3M"):
      discount_factor_nodes = libor_3m_curve.discount_factor_nodes
      self.assertAllClose(discount_factor_nodes, self._libor_discounts)


if __name__ == "__main__":
  tf.test.main()
