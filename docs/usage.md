---
nav_order: 3
---

# Usage

To activate the particle brush, enter texture paint mode as usual. Then run the add-on's operator
`PAINTicle` by clicking on the menu button in the 3d-view's top menu bar.

![]({{site_url}}/images//painticle_menubutton.png)

This will activate the add-on on the object currently been drawn on. If an existing particle brush is selected, this
one is getting used. If none is selected (e.g. using it for the first time on a new scene), a new set of default
brushes is being automatically created. By drawing onto the mesh, Blender is not using the normal brush anymore but
simulates particles' movement over the surface of the selected mesh. Leaving the particle paint mode can be done by
hitting `ESC`. When activated, you can see in the lower left corner of the viewport the status of the add-on. While
waiting for the next stroke being drawn it reads `PAINTicle active`, but while the simulation is running it shows
`Simulating...`. This indicates, that there are still particles in the scene, influencing the painted texture. When
using the preview mode, it's important to wait until the end of the simulation before exiting the tool, otherwise, the
last stroke is not being synchronized to blender's version of the image anymore and gets lost.

 The *Tools* panel offers a group with settings for the particle brush:

 ![]({{site_url}}/images//painticle_settings.png)

| Property                            | Description                                                                                                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stop on mouse release               | Will stop the simulation as soon as the mouse button has been released. Otherwise simulation continues until all particles died.                              |
| Brush                               | This will show the properties of the selected brush. These may differ depending on the selected brush. Please refer to the [nodes reference](./nodes). |
| Physics                             |                                                                                                                                                               |
| Physics/Max. timestep               | A maximum time-step for the simulation. Choose as low, so that particles don't leave dotted traced.                                                           |
| Simulation substeps                 | The number of steps to divide the timestep above into. Higher substeps can improve the simulation stability while degrading the performance.                  |

## Other properties used

The particle brush utilizes the following common brush properties of Blender's built-in painting system
 
 * Radius   (`F` or `right-click`)
 * Strength (`SHIFT+F` or `right-click`)
 * Color    (`right-click`)

## Brush management

PAINTicle utilized custom node graphs to manage custom brushes. Currently the parameters of a PAINTicle brush can fully
be seen on the right side panel. Adding and removing simulation steps at the moment still needs to be done in the node
editor. A graph represents a set of multiple brushes and flags one of them as the active brush. That way, the graphs
serve as a categorization of brushes. Future UI enhancements will allow definition and modification of PAINTicle
brushes directly from the side panel without going to the node editor.

**WARNING**: Since PAINTicle is still in development mode without a stable release, no guarantees are being made about
future compatibility of authored PAINTicle brush node graphs!

## Undo

Currently there's an issue in Blender when undoing pixel manipulations on image textures. Thus the add-on
implements it's own single step undo queue. While painting, you can press `U` to undo the last paint operation.
