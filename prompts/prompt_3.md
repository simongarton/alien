We have some Python scripts to generate alients, write to disk as image, and translate between two formats.

I now want an application that will allow me to create and edit these interactively.

Use PySide6 to create a new multi window application.

The `Main` application will support a simple menu bar with a File menu.

Under the File menu will be the following commands:

- New : a dialog will pop up and ask me to select the width and height of the image, plus the palette. A new `Alien` window will then pop up to allow me to edit and save an alient.
- Open : another dialog will allow me to select a file on disk - either JSON or the Text image - and then load that alien into the `Alien` window for editing and saving.
- Exit : the application will shut down after confirming I want to do so.

The `Alien` window will have a clickable grid of square cells, matching the pixels for the alien, plus a color selector based on the palette. I will be able to click on the color selector to choose a color and then click on a grid to toggle it that color. The color selector will probably have some cells - different to the pixel cells - where I can click to select it, or double click to choose a new color : this should be a standard interface.

The `Alien` window will have it's own File menu with:

- Save : saves the current alien using the filename that was selected, or prompting me for a new filename if it doesn't yet have one.
- Save As : prompt me for the filename, using the existing one as a starting point if it exists.
- Close : closes this window.

Multiple `Alien` windows can be supported.
