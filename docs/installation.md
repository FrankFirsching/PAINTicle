---
nav_order: 1
---
# Installation

To install the add-on grab a release from GitHub's [releases](https://github.com/FrankFirsching/PAINTicle/releases)
page. The downloaded zip file can be installed via `Edit > Preferences > Add-ons > Install...`

This add-on makes use of the python module [moderngl](https://github.com/moderngl/moderngl) under the MIT license.
This module should be installed automatically when activating the add-on. The preferences panel shows a successful
installation by showing a blue/checked button "Install dependencies". If the dependencies are not available, this
button will be clickable gray and it can trigger the installation of the dependencies.

![]({{site_url}}/images/painticle_preferences.png)

# Preview mode selection

The add-on supports multiple ways to improve performance and reduce the rendering quality during painting. Since
updating the texture in blender's image management system is quite costly, starting from a configurable texture size
threshold (predefined to 1 megapixel = 1024 pixels edge length), the add-on won't update blender's texture on each
simulation step.

![]({{site_url}}/images/painticle_previewmode.jpg)

| Mode | Description |
| - | - |
| *Particles* | Drawing the simulated particles as dots. |
| *Texture overlay* | Overlaying the calculated texture on top of the viewport.<br>This doesn't keep the shading of the material but shows the texture content directly. |

## Requirements

The add-on requires a GPU capable of OpenGL 4.3, which provides support for compute shaders. This is a higher level
than Blender requires. It might be, that your system can run Blender, but it can't support this add-on. Please advice
Blenders system information `Help > Save System Info` if your system supports at least the required version.
