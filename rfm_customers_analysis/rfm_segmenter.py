"""RFM Segmenter"""

import pandas as pd


class RFMSegmenter:
    """
    Assigns RFM segments based on quantiles.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def segment(self) -> pd.DataFrame:
        """Segment data"""
        df = self.df

        df["r_score"] = pd.qcut(df["recency"], 5, labels=[5, 4, 3, 2, 1])
        df["f_score"] = pd.qcut(
            df["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
        )
        df["m_score"] = pd.qcut(df["monetary"], 5, labels=[1, 2, 3, 4, 5])

        df["rfm_score"] = (
            df["r_score"].astype(int)
            + df["f_score"].astype(int)
            + df["m_score"].astype(int)
        )

        df["rfm_segment"] = pd.cut(
            df["rfm_score"],
            bins=[0, 6, 9, 12, 15],
            labels=["At Risk", "Needs Attention", "Loyal", "Champions"],
        )

        return df
