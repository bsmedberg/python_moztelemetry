from __future__ import division

import requests
import histogram_tools
import pandas as pd
import numpy as np

_definitions = requests.get("https://hg.mozilla.org/mozilla-central/raw-file/tip/toolkit/components/telemetry/Histograms.json").json()

class Histogram:
    def __init__(self, name, instance):
        self.definition = histogram_tools.Histogram(name, _definitions[name])

        if isinstance(instance, list) or isinstance(instance, np.ndarray):
            values = None
            if len(instance) == self.definition.n_buckets():
                values = instance
            else:
                values = instance[:-5]
            self.buckets = pd.Series(values, index=self.definition.ranges())
        else:
            entries = {int(k): v for k, v in instance["values"].items()}
            self.buckets = pd.Series(entries, index=self.definition.ranges()).fillna(0)

    def __str__(self):
        return str(self.buckets)

    def get_values(self):
        return self.buckets

    def get_definition(self):
        return self.definition

    def percentile(self, percentile):
        assert(percentile >= 0 and percentile <= 100)

        fraction = percentile/100
        to_count = fraction*self.buckets.sum()
        percentile_bucket = 0

        for percentile_bucket in range(len(self.buckets)):
            freq = self.buckets.values[percentile_bucket]
            if to_count - freq <= 0:
                break
            to_count -= freq

        if percentile_bucket == len(self.buckets) - 1:
            return float('nan')

        percentile_frequency = self.buckets.values[percentile_bucket]
        percentile_lower_boundary = self.buckets.index[percentile_bucket]
        width = self.buckets.index[percentile_bucket + 1] - self.buckets.index[percentile_bucket]
        return percentile_lower_boundary + width*to_count/percentile_frequency
