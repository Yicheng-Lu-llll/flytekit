import typing
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from flytekit import task, Resources, workflow, StructuredDataset

import timeit

@task(
    limits=Resources(mem="4Gi"),
    disable_deck=True,
)
def create_parquet() -> StructuredDataset:
    df = pd.DataFrame(np.random.choice(['foo','bar','baz'], size=(100000, 3)), columns=["a", "b", "c"])
    df = df.apply(lambda col: col.astype('category'))

    return StructuredDataset(dataframe=df)


@task(
    limits=Resources(mem="4Gi"),
    disable_deck=True,
)
def read_input_records(sd: StructuredDataset) -> List[Dict[str, Any]]:
    df = sd.open(pd.DataFrame).all()
    records = typing.cast(pd.DataFrame, df).to_dict()
    return [records]*1000  # 1000 * 3


@workflow
def wf():
    sd = create_parquet()
    read_input_records(sd=sd)


if __name__ == "__main__":
    print(timeit.timeit(wf, number=10))