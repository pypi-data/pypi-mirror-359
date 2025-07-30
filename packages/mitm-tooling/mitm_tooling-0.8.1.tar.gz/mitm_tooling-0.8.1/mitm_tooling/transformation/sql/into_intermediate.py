import pandas as pd
import sqlalchemy as sa

from mitm_tooling.definition import MITM, get_mitm_def
from mitm_tooling.representation.intermediate import Header, HeaderEntry
from mitm_tooling.representation.sql import SchemaName
from mitm_tooling.representation.sql.sql_representation import HeaderMetaTableName, mk_header_tables
from mitm_tooling.transformation.sql import db_engine_into_db_meta
from mitm_tooling.utilities.python_utils import pick_from_mapping
from mitm_tooling.utilities.sql_utils import use_db_bind, AnyDBBind


def mitm_db_into_header(bind: AnyDBBind, override_schema: SchemaName | None = None) -> Header | None:
    sa_meta = sa.MetaData()
    meta_tables = mk_header_tables(sa_meta, override_schema=override_schema)
    with use_db_bind(bind) as conn:
        kvs = dict(conn.execute(sa.select(meta_tables.key_value)).all())
        if mitm_str := kvs.get('mitm'):
            mitm: MITM = MITM(mitm_str)
            mitm_def = get_mitm_def(mitm)
            t_left, t_right = meta_tables.types, meta_tables.type_attributes
            j = sa.join(t_left, t_right, isouter=True)

            type_attributes = conn.execute(
                sa.select(*pick_from_mapping(t_left.c, ('kind', 'type', 'concept')), *pick_from_mapping(t_right.c, ('attribute_order', 'attribute_name', 'attribute_dtype'))).select_from(j)).all()
            df = pd.DataFrame.from_records(type_attributes,
                                           columns=['kind', 'type', 'concept', 'attribute_order', 'attribute_name',
                                                    'attribute_dtype'])
            hes = []
            for (kind, type_name, concept), idx in df.groupby(['kind', 'type', 'concept']).groups.items():
                attributes_df = df.loc[idx].dropna().sort_values('attribute_order', ascending=True)[
                    ['attribute_name', 'attribute_dtype']]
                if len(attributes_df) > 0:
                    attribute_names, attribute_dtypes = zip(*attributes_df.itertuples(index=False))
                else:
                    attribute_names, attribute_dtypes = (), ()
                # c = mitm_def.inverse_concept_key_map[kind]
                hes.append(HeaderEntry(concept=concept, kind=kind, type_name=type_name, attributes=tuple(attribute_names),
                                       attribute_dtypes=tuple(attribute_dtypes)))

            return Header(mitm=mitm, header_entries=frozenset(hes))
        return None
