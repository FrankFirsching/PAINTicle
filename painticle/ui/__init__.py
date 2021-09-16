# This file is part of PAINTicle.
#
# PAINTicle is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAINTicle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PAINTicle.  If not, see <http://www.gnu.org/licenses/>.

# The particle painter, that's using the gpu directly

# <pep8 compliant>

from . import brushnodes
from . import brushtree
from . import preferences_panel
from . import settings_panel

all_ui = [
    *brushnodes.all_nodes,
    brushtree.BrushSocket,
    settings_panel.PAINTiclePresetsMenu,
    settings_panel.PAINTicleBrushMenu,
    settings_panel.AddPresetParticleSettings,
    settings_panel.PAINTicleMainPanel,
    settings_panel.PAINTicleBrushPanel,
    settings_panel.PAINTiclePhysicsPanel,
    preferences_panel.PreferencesPanel,
]