# Concept

To allow splitting up a Layer 2 network, the most common strategy is to split by location so neighbouring nodes end up in the same network segment.

This tool allows for multiple decision-criteria to find the most suitable segment for a requesting node. 
It assigns the destination network segment not by node but by mesh.
Once a mesh has been detected by the director, it's assigned domain is set for all nodes belonging to this mesh.
A mesh is currently not re-evaluated. This means once a domain is set for the specific mesh, no member will be removed nor the selected sub network changed. 

This means it analyzes which nodes build a mesh and then assigns this mesh to a specific network segment. It factors in user-provided location which the director retrieves from a YANIC server.
The node can also scan the available WiFi networks in the area and share this information with the director. 
This way a more accurate decision can be made about the correct network segement.

The node-side reference implementation for the Gluon framework can be found [here](https://github.com/freifunk-darmstadt/ffda-packages/tree/master/ffda-domain-director).
