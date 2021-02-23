### What does this Add-In do?
1. It accepts the same syntax as used by the famous [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/) to generate a Sketch within
Fusion 360 with position information & metadata for each key.
![gen_keyboard_layout](https://github.com/pragun/f3d_mech_kbrd_addin/wiki/images/gen_keyboard_layout.png)

2. It *Adds-In* much missing functionality as offered by other CAD programs under names such as "Sketch Driven Component Placement", "Sketch Driven Pattern", etc
to broadcast YOUR chosen components at the key-positions specified in the layout.
![Broadcast Squares to 1u keys](https://github.com/pragun/f3d_mech_kbrd_addin/wiki/images/broad_cast_1.png)
![Broadcast Spheres to 1.25u keys](https://github.com/pragun/f3d_mech_kbrd_addin/wiki/images/broad_cast_2.png)

3. Plus+. It *Adds-in* the ability to filter the points that each component gets broadcasted to. So, your custom designed sub-assembly for 2u keys will only be broadcasted to
appropriately sized keys. I personally feel that this little bit is a really cool way of doing CAD things programatically.


### Recommended Workflow for using this AddIn
Please don't forget to checkout the examples in the [wiki](https://github.com/pragun/f3d_mech_kbrd_addin/wiki).
1. Please spend some quality time with the famous [Keyboard Layout Editor](http://www.keyboard-layout-editor.com/.)
2. Create a keyboard layout you really like.
3. Copy that raw-data (from Keyboard Layout Editor) and bring it into Fusion 360 using the "Generate Keyboard Layout" command. link to come soon.
4. Let the AddIn do the heavy lifing of generating a sketch, and it might take it a minute or so. Depending on what it is lifting.
5. Save your Fusion 360 File. Why not? They're not charging you to save files (yet).
6. At this point you'd bring in your separately designed components for 1u, 2u,... keys. You're welcome to use my elementry collection from the submodules folder in this repo.
7. Broadcast these components to their appropriate places using the "Broadcast Components over Sketch Points". link to come soon.
8. Select appropriate plate-sub-components and merge them using Fusion's "Combine" command. 

### Install Instructions
1. Download/Clone. If you use git then go ahead and clone this repo, otherwise you're welcome to download this repo using this [link](https://github.com/pragun/f3d_mech_kbrd_addin/archive/master.zip)
2. Unzip the downloaded archive. For the next steps, I'll assume that you have extracted the archive at C:\Downloads\f3d_mech_kbrd_addin-master
3. Add AddIn into Fusion 360. Go to Fusion 360 > Tools > ADD-INS (You can click on the big button that has a small grey gear icon on it)
4. Select the Add-Ins tab and click on the green + icon, right after "My Add-Ins"
5. Open the path where you extracted the downloaded zip file (as in step 2. For example: C:\Downloads\f3d_mech_kbrd_addin-master)
6. You should see a new entry appear under "My Add-Ins" called "Mechanical Keyboard Tools"
7. Go ahead, select it and click on Run.
8. You should see a pop-up reading "Mechanical Keyboard Design Tools Add-In Started".
 


### Why yet another Keyboard layout tool?
I have been toying with a split-type keyboard design in my mind. I used several keyboard layout
generators to generate dxf/svg files. I did not want to send out the dxf/svg files to an online service, and pay $$$$$ for steel/acrylic plates. 
I wanted to use my 3D printer to print the plates for $ instead (reducing the cost of each design-iteration matters to be able to iterate
enough number of times to actually get to a design that does what I imagine it should).

This is where the problem begins:
1. I need to make adjustments to the hole-cut out size to get that snug fit on my 3D printer. Which, for some reason I haven't figured out yet,
I choose to run on a 1.2mm nozzle. Some dxf/svg tools allow you to change those dimensions but the workflow for making those changes
in the dxf/svg file and propagating them to my 3D model seemed awful. For example:Fusion 360 doesn't let you just swap out a dxf file for another one.
2. I am not willing to wait for 3-4 weeks to get plate-mounted stabilizers. PCB mount stabilizers are easier to find in the USA and I want to use them.
This means that I'll have to design custom floating plates for suspending those stabilizers for each of the 2u, 3u, what-have-u key I have. Again, a workflow problem,
as I mess around with my design.

