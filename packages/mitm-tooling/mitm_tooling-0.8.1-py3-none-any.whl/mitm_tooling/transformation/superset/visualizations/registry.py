from typing import Type, Union, Iterable

from mitm_tooling.definition import MITM
from mitm_tooling.representation.intermediate import Header
from .maed.registry import MAEDVisualizationType, maed_visualization_creators
from ..asset_bundles import MitMDatasetIdentifierBundle
from ..visualizations.abstract import MitMVisualizationsCreator, SupersetVisualizationBundle

VisualizationType = Union[MAEDVisualizationType]

mitm_visualization_creators: dict[MITM, dict[VisualizationType, Type[MitMVisualizationsCreator]]] = {
    MITM.MAED: maed_visualization_creators
}


def get_mitm_visualization_creator(mitm: MITM, visualization_type: VisualizationType) -> Type[
                                                                                             MitMVisualizationsCreator] | None:
    if creators := mitm_visualization_creators.get(mitm):
        if (creator := creators.get(visualization_type)) is not None:
            return creator
    return None


def mk_visualization(visualization_type: VisualizationType,
                     header: Header,
                     identifiers: MitMDatasetIdentifierBundle,
                     just_placeholders: bool = False) -> SupersetVisualizationBundle | None:
    if (creator_cls := get_mitm_visualization_creator(header.mitm, visualization_type)) is not None:
        creator = creator_cls(header)
        if just_placeholders:
            return creator.mk_placeholder_bundle(identifiers)
        else:
            return creator.mk_bundle(identifiers)
    return None


def mk_visualizations(visualization_types: Iterable[VisualizationType],
                      header: Header,
                      identifiers: MitMDatasetIdentifierBundle,
                      just_placeholders: bool = False) -> dict[VisualizationType, SupersetVisualizationBundle]:
    return {vt: viz for vt in set(visualization_types) if (
        (viz := mk_visualization(vt, header, identifiers, just_placeholders=just_placeholders)) is not None)}
