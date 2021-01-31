## Welcome to the documentation for F3D Tools for Keyboard Design

### What does this Add-In do?
1. It accepts the same syntax as used by the famous [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/) to generate a Sketch within
Fusion 360 with the placement information & metadata for each key.
[[https://github.com/pragun/f3d_mech_kbrd_addin/blob/master/assets/img/gen_keyboard_layout.png|alt=Generate Keyboard Layout]]

2. It Adds-In the much missing functionality as offered by other CAD programs under names such as "Sketch Driven Component Placement", "Sketch Driven Pattern", etc
to broadcast YOUR chosen components at the key-positions specified in the layout.

3. Plus+. It adds-in the ability to filter the points that each component gets broadcasted to. So, your custom designed sub-assembly for 2u keys will only be broadcasted to
appropriately sized keys. I personally feel that this little bit is a really cool way of doing CAD things programatically.

#### How would it do the point-filtering thing?
You'd provide the filter input in the simplest JSON dictionary possible.

### Gosh, why did you write an Add-In when there are atleast 10 tools out there to generate Keyboard layouts?
### (Or), why would I use your Add-In when I could use any of the 10 tools out there?
Just a little-bit of history. I have been toying with a split-type keyboard design in my mind. I used several keyboard layout
generators to generate dxf/svg files. 

I did not want to send out the dxf/svg files to an online service, and pay $$$$$ for steel/acrylic plates. 
I wanted to use my 3D printer to print the plates for $ instead (reducing the cost of each design-iteration matters to be able to iterate
enough number of times to actually get to a design that does what I imagine it should).

This is where the problem begins:
1. I need to make adjustments to the hole-cut out size to get that snug fit on my 3D printer. Which, for some reason I haven't figured out yet,
I choose to run on a 1.2mm nozzle. Some dxf/svg tools allow you to change those dimensions but the workflow for making those changes
in the dxf/svg file and propagating them to my 3D model seemed awful. For example:Fusion 360 doesn't let you just swap out a dxf file for another one.
2. I am not willing to wait for 3-4 weeks to get plate-mounted stabilizers. PCB mount stabilizers are easier to find in the USA and I want to use them.
This means that I'll have to design custom floating plates for suspending those stabilizers for each of the 2u, 3u, what-have-u key I have. Again, a workflow problem,
as I mess around with my design.

### What workflow do you recommend for designing Mechanical Keyboard using your AddIn?
Glad you asked. 
1. Please spend some quality time with the famous [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/.)
2. Create a keyboard layout you really like.
3. Copy that raw-data (from Keyboard Layout Editor) and bring it into Fusion 360 using the "Generate Keyboard Layout" command. link to come soon.
4. Let the AddIn do the heavy lifing of generating a sketch, and it might take it a minute or so. Depending on what it is lifting.
5. Save your Fusion 360 File. Why not? They're not charging you to save files, yet.
6. At this point you'd bring in your separately designed components for 1u, 2u,... keys. link to come soon.
7. Broadcast these components to their appropriate places using the "Broadcast Components over Sketch Points". link to come soon.
8. Select appropriate plate-sub-components and merge them using Fusion's "Combine" command. 

