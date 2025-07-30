import pandas as pd

from mitm_tooling.data_types.convert import convert_df
from mitm_tooling.definition import MITM, ConceptName
from mitm_tooling.utilities.io_utils import DataSink, DataSource, use_for_pandas_io, FilePath, ensure_directory_exists
from ..common import guess_k_of_header_df
from ..common import mk_header_file_columns, mk_concept_file_header


def write_header_file(df: pd.DataFrame, sink: DataSink | None) -> str | None:
    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    return df.to_csv(sink, header=True, index=False, sep=';')


def write_data_file(df: pd.DataFrame, sink: DataSink | None, append: bool = False) -> str | None:
    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    return df.to_csv(sink, header=not append, index=False, sep=';', date_format='%Y-%m-%dT%H:%M:%S.%f%z')
