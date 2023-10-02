# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MFM
                                 A QGIS plugin
 1e MFM
                             -------------------
        begin                : 2016-11-18
        copyright            : (C) 2016 by mro
        email                : rotsaert@svasek.nl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MFM class from file MFM.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .MFM_GUI import MFM
    return MFM(iface)
