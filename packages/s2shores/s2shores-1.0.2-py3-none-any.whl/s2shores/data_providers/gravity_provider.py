# -*- coding: utf-8 -*-
""" Definition of the GravityProvider abstract class and ConstantGravityProvider class

:authors: see AUTHORS file
:organization: CNES, LEGOS, SHOM
:copyright: 2021 CNES. All rights reserved.
:license: see LICENSE file
:created: 25/06/2021

  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
  in compliance with the License. You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software distributed under the License
  is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
  or implied. See the License for the specific language governing permissions and
  limitations under the License.
"""
import math
from abc import ABC, abstractmethod

from shapely.geometry import Point

from .localized_data_provider import LocalizedDataProvider


class GravityProvider(ABC, LocalizedDataProvider):
    """ A GravityProvider is a service able to provide the gravity at different places
    and altitudes on earth. The points where gravity is requested are specified by coordinates
    in some SRS.
    """

    @abstractmethod
    def get_gravity(self, point: Point, altitude: float) -> float:
        """ Provides the gravity at some point expressed by its X, Y and H coordinates in some SRS.

        :param point: a point expressed in the SRS coordinates set for this provider
        :param altitude: the altitude of the point in the SRS set for this provider
        :returns: the acceleration due to gravity at this point (m/s2).
        """


class ConstantGravityProvider(GravityProvider):
    """ A GravityProvider which provides the mean accelation of the gravity on Earth.
    """

    def get_gravity(self, point: Point, altitude: float) -> float:
        _ = point
        _ = altitude
        # TODO: replace return value by 9.80665
        return 9.81


class LatitudeVaryingGravityProvider(GravityProvider):
    """ A GravityProvider which provides the acceleration of the gravity depending on the
    latitude of the point on Earth.
    """

    g_poles = 9.832
    g_equator = 9.780
    g_45 = (g_poles + g_equator) / 2.
    delta_g = (g_poles - g_equator) / 2.

    def get_gravity(self, point: Point, altitude: float) -> float:
        _, latitude, _ = self.transform_point((point.x, point.y), altitude)
        gravity = self.g_45 - self.delta_g * math.cos(latitude * math.pi / 90)
        return gravity
