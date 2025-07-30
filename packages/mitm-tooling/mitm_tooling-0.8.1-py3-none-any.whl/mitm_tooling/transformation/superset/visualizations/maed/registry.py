from enum import StrEnum
from typing import Type

from ..abstract import MitMVisualizationsCreator
from .dashboards import BaselineMAEDDashboard, \
    ExperimentalMAEDDashboard, CustomChartMAEDDashboard


class MAEDVisualizationType(StrEnum):
    Baseline = 'baseline'
    Experimental = 'experimental'
    CustomChart = 'custom-chart'


maed_visualization_creators: dict[MAEDVisualizationType, Type[MitMVisualizationsCreator]] = {
    MAEDVisualizationType.Baseline: MitMVisualizationsCreator.wrap_dashboard_creator(MAEDVisualizationType.Baseline,
                                                                                     BaselineMAEDDashboard),
    MAEDVisualizationType.Experimental: MitMVisualizationsCreator.wrap_dashboard_creator(MAEDVisualizationType.Experimental,
                                                                                         ExperimentalMAEDDashboard),
    MAEDVisualizationType.CustomChart: MitMVisualizationsCreator.wrap_dashboard_creator(MAEDVisualizationType.CustomChart,
                                                                                        CustomChartMAEDDashboard)}
