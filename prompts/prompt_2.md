So far we have a file format set up for the **Alien generator**, which is `JSON`, and describes a list of lists of hex codes which is all we need to draw the image.

I want to add a second format, which will be `Text` and end in an extension `.txt`.

This format will look like this example:

```
3
B#000000
b#0000FF
W#FFFFFF
4
8
BBBBBBBB
BBBbbBBB
BBbbbbBB
BbWbbWbB
```

The first row tells me how many colours will be used.
Then I have a row for each of those colours, where there is a single character that represents the colour, and then the hex code for that colour.
Then I have an integer for the number of rows in the image (the height)
Then I have an integer for the number of columns in the image (the width)
Then I have a row in the file for each row in the image; the row will be a series of letters, total count will be the number of columns, and each character in the row will be the colour to use.

Create two files:

`alien_json_to_text.py` which takes in the `JSON` object and returns a list of strings ready to be written to the `Text` file format.

`alien_text_to_json.py` which takes in the `Text` object and returns a list of strings ready to be written to the `JSON` file format.

