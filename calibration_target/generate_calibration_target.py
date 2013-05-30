#!/usr/bin/env python

#
# FILE:   generate_calibration_target.py
# copyright Kevin Atkinson, 2008
# kevin.atkinson@gmail.com
# http://methodart.blogspot.com
#
# You have permission to use this code to do whatever you wish, with
# the sole proviso that if you redistribute this source file, or
# modifications of this source file, you retain this notice.
#
# The other part of the license is a request, rather than a requirement:
# if you use it for something interesting, drop me a line (kevin.atkinson@gmail.com)
# to let me know about it.  After all, the only reward in giving your code 
# away is knowing that someone somewhere is finding it useful.
#
# Finally, this is fairly new code, so it's entirely probable that you may discover
# some bugs.  If you do, please let me know about them so I can fix them.
#

# Modified by Thomas Denewiler, 2012.
# Added support for more standard checkerboard and circle arrays, with the option
# of inverting colors.

# Modified by Antonella Wilby, May 2013.
# Added support for center-to-center spacing specification for circle patterns.
# NOTE: this entire script needs a lot of fixes, and working stuff hasn't been thoroughly tested!
# KNOWN ISSUES: Text always displays, even when use_text is set to false
#		When using fiducials, bottom and right borders are small
#		When using fiducials, bottom text overlaps targets
#		Can't yet specify center-to-center spacing for asymmetric circles
#		Text runs off side of page for smaller targets --
#			need to size text based on layout size
#		Invert function seems to be confused throughout script...
#			not sure if invert means set to black on white or white on black.
#			For now, when invert is set it outputs white targets on black background.
#
# Please verify the results you get from this script!

import sys
import cairo
import pango
import pangocairo
from math import pi
from optparse import OptionParser
import pygtk
import gtk
import Image
import StringIO

parser = OptionParser()
parser.add_option("-W", "--width", dest="width", help="Number of squares or \
		  circles in x-dir. Default: 15", default=15)
parser.add_option("-H", "--height", dest="height", help="Number of squares or \
		  circles in y-dir. Default: 11", default=11)
parser.add_option("-s", "--shapesize", dest="shapesize", help="Length of \
		  square side or diameter of circles. Default: 1", default=1)
parser.add_option("-u", "--units", dest="units", help="Units: 1=inches, \
		  2=centimeters. Default: 1", default=1)
parser.add_option("-f", "--file", dest="filename", help="Name of pdf file to \
		  generate. Default: calibration_target.pdf", \
		  default="calibration_target.pdf")
parser.add_option("-b", "--border", dest="border", help="Size of border around\
		  calibration pattern. Default: 0.5", default=0.5)
parser.add_option("-i", "--invert", dest="invert", help="Invert colors: \
		  True=white markers on black background, False=black markers\
		  on white background. Default: False", default=False)
parser.add_option("-p", "--pattern", dest="pattern", help="Pattern to use: \
		  1=fiducials, 2=checkerboard, 3=circles (symmetric), 4=circles\
		  (asymmetric). Default: 1", default=1)
parser.add_option("-c", "--spacing", dest="spacing", help="Center-to-center \
		  spacing. Only used for circle patterns (-p 3). Default: 2", default=2)
parser.add_option("-t", "--use_text", dest="use_text", help="Add text \
		  description to board. Default: True", default=True)

options, args = parser.parse_args(sys.argv)

filename = options.filename

def set_vars():
    global width
    global height
    global shapesize
    global border
    global units
    global invert
    global pattern
    global spacing
    global use_text
    width = 0
    height = 0
    shapesize = 0
    border = 0
    units = 1
    invert = False
    pattern = 1
    spacing = 2
    use_text = True

# Read in options with a bit of validation.
try:
    global width
    width = int(options.width)
except ValueError:
    print "width option (-W) must be an integer."
    sys.exit(0)
    
if width < 0 or width > 64:
    print "width option (-W) must be an integer between 0 and 64."
    sys.exit(0)
    
try:
    global height
    height = int(options.height)
except ValueError:
    print "height option (-H) must be an integer"
    sys.exit(0)
    
if height < 0 or height > 32:
    print "height option (-H) must be an integer between 0 and 32."
    sys.exit(0)
    
try:
    global shapesize
    shapesize = float(options.shapesize)
except ValueError:
    print "shapesize option (-s) must be a floating point number."
    sys.exit(0)

try:
    global border
    border = float(options.border)
except ValueError:
    print "border option (-b) must be a floating point number."
    sys.exit(0)

try:
    global units
    units = int(options.units)
except ValueError:
    print "unit option (-u) must be an integer."
    sys.exit(0)

try:
    global invert
    invert = bool(options.invert)
except ValueError:
    print "invert option (-i) must be a boolean."
    sys.exit(0)

try:
    global pattern
    pattern = int(options.pattern)
except ValueError:
    print "pattern option (-p) must be an integer."
    sys.exit(0)

try:
    global spacing 
    spacing = int(options.spacing)
except ValueError:
    print "spacing option (-c) must be a floating point number."
    sys.exit(0)

try:
    global use_text
    use_text = bool(options.use_text)
except ValueError:
    print "use_text option (-t) must be a boolean."
    sys.exit(0)

def do_poly(cr, pts):
    cr.move_to(*(pts[0]))
    for pt in pts[1:]:
        cr.line_to(*pt)

# Draws a code square in (0,0), (1,1).
# n is dimension of square; code area is (n-1)x(n-1).
def draw_code(cr, code_val, n):
    assert code_val < (2**((n-1)*(n-2)-1))
    
    incr = 1./(n)
    do_poly(cr, [(0,0),(0,1),(1,1),(1,1-incr),(incr,1-incr),(incr,0)])
    cr.fill()
    ones_count = 0
    bit = 0
    code_val <<= 1 # Want the first bit to be clear.
    for i in range(n-2):
        for j in range(n-1):
            if (code_val & (1<<bit)):
                cr.rectangle((j+1)*incr, i*incr, incr, incr)
                cr.fill()
                ones_count += 1
            bit += 1
    
    # Checksum.
    for i in range(n-2):
        if ones_count & (1<<i):
            cr.rectangle((i+1)*incr, (n-2)*incr, incr, incr)
            cr.fill()


def draw_cb_square(cr, code, n, border=.2):
    cr.set_source_rgb(0,0,0)
    cr.rectangle(0,0,1,1)
    cr.fill()
    cr.save()
    cr.translate(border, border)
    cr.scale(1-2*border, 1-2*border)
    cr.set_source_rgb(1,1,1)
    cr.rectangle(0,0,1,1)
    cr.fill()
    cr.restore()
    cr.save()
    cr.translate(1.5*border, 1.5*border)
    cr.scale(1-3*border, 1-3*border)
    cr.set_source_rgb(0,0,0)
    draw_code(cr, code, n)
    cr.restore()
    cr.rectangle(-border, -border, border, border)
    cr.rectangle(1, -border, border, border)
    cr.rectangle(1, 1, border, border)
    cr.rectangle(-border, 1, border, border)


# We encode squares with a code of size 5, which gives us
# 2**((5-1)*(5-2)-1) = 512 codes.  We will furthermore use
# 6 bits for width and 5 bits for height, which gives a maximum
# checkerboard size of 64x32.  w and h should be odd.
def draw_cb_fiducials(cr, w, h):
    border = 0.2
    cr.translate(border, border)
    for i in range(h):
        for j in range(i%2,w,2):
            cr.save()
            cr.translate(j, h-i-1)
            draw_cb_square(cr, (j<<5)|i, 5, border)
            cr.fill()
            cr.restore()

def draw_cb(cr, w, h):
    in_to_pts = 1/72.0
    cm_to_pts = in_to_pts / 2.54
    for i in range(w):
        for j in range(h):
            if not i%2:
                if not j%2:
                    if invert:
                        cr.set_source_rgb(1,1,1)
                    else:
                        cr.set_source_rgb(0,0,0)
                        #cr.set_source_rgb(0.7,0.7,0.7)
                    if units == 1:
                        cr.rectangle(border*in_to_pts+i,border*in_to_pts+j,1,1)
                    elif units == 2:
                        cr.rectangle(border*cm_to_pts+i,border*cm_to_pts+j,1,1)
                    cr.fill()
                    cr.save()
            else:
                if j%2:
                    if invert:
                        cr.set_source_rgb(1,1,1)
                    else:
                        cr.set_source_rgb(0,0,0)
                        #cr.set_source_rgb(0.7,0.7,0.7)
                    if units == 1:
                        cr.rectangle(border*in_to_pts+i,border*in_to_pts+j,1,1)
                    elif units == 2:
                        cr.rectangle(border*cm_to_pts+i,border*cm_to_pts+j,1,1)
                    cr.fill()
                    cr.save()

def draw_circles(cr, w, h):
    in_to_pts = 1/72.0
    cm_to_pts = in_to_pts / 2.54
    centerX = 0		# x coordinate of center of cirlce
    centerY = 0		# x coordinate of center of circle
    for i in range(w):
        for j in range(h):
	    # Check to see if colors should be inverted
	    if invert:
		cr.set_source_rgb(1,1,1) 	# Set circles to white
	    else:
		cr.set_source_rgb(0,0,0) 	# Set circles to black

	    # Compute center coordinates of circle
	    if units == 1:
		centerX = border*in_to_pts+(i*spacing)+0.5
		centerY = border*in_to_pts+(j*spacing)+0.5
	    elif units == 2:
		center_x = border*cm_to_pts+(i*spacing)+0.5
		center_y = order*cm_to_pts+(j*spacing)+0.5
		
	    # Draw the circle
	    cr.arc(centerX, centerY, 0.5, 0, 2*pi)
	    cr.fill()
	    cr.save()


def draw_circles_asymmetric(cr, w, h):
    in_to_pts = 1/72.0
    cm_to_pts = in_to_pts / 2.54
    for i in range(w):
        for j in range(h):
            if not i%2:
                if not j%2:
                    if invert:
                        cr.set_source_rgb(1,1,1)
                    else:
                        cr.set_source_rgb(0,0,0)
                    if units == 1:
                        cr.arc(border*in_to_pts+i+0.5,border*in_to_pts+j+0.5,0.5,0,2*pi)
                    elif units == 2:
                        cr.arc(border*cm_to_pts+i+0.5,border*cm_to_pts+j+0.5,0.5,0,2*pi)
                    cr.fill()
                    cr.save()
            else:
                if j%2:
                    if invert:
                        cr.set_source_rgb(1,1,1)
                    else:
                        cr.set_source_rgb(0,0,0)
                    if units == 1:
                        cr.arc(border*in_to_pts+i+0.5,border*in_to_pts+j+0.5,0.5,0,2*pi)
                    elif units == 2:
                        cr.arc(border*cm_to_pts+i+0.5,border*cm_to_pts+j+0.5,0.5,0,2*pi)
                    cr.fill()
                    cr.save()
		    
def draw_logo(cr):
    # Add the UCSD Logo to the page -- only works with PNGs!
    ucsdLogo = Image.open('ucsd_logo.png')
    ucsdLogoBuffer = StringIO.StringIO()
    ucsdLogo.save(ucsdLogoBuffer, format="PNG")
    ucsdLogoBuffer.seek(0)
    ucsdLogoSurface = cairo.ImageSurface.create_from_png(ucsdLogoBuffer)
    
    # Add the Engineers for Exploration logo to the page
    e4eLogo = Image.open('e4e_logo.png')
    e4eLogoBuffer = StringIO.StringIO()
    e4eLogo.save(e4eLogoBuffer, format="PNG")
    e4eLogoBuffer.seek(0)
    e4eLogoSurface = cairo.ImageSurface.create_from_png(e4eLogoBuffer)
    
    # Add UCSD logo to image surface
    cr.translate(0,0)		# Set proper position for drawing logo
    cr.save()
    cr.scale(0.35,0.35)
    cr.set_source_surface(ucsdLogoSurface, 20, 20)
    cr.paint()
    cr.restore()
    
    # Add the Engineers for Exploration logo to image surface
    cr.translate(125,0)		# Set proper position for drawing logo
    cr.save()
    cr.scale(0.35,0.35)
    cr.set_source_surface(e4eLogoSurface, 20, 20)
    cr.paint()
    cr.restore()

            
if __name__=='__main__':
    pts_to_in = 72.0
    pts_to_cm = pts_to_in / 2.54
    

    # Calculate the width and height of the whole target
    if pattern == 1 or pattern == 2 or pattern == 4:
	layoutWidth = width*(shapesize) + 2*border
	layoutHeight = height*shapesize + 2*border
    if pattern == 3: 
	layoutWidth = width*(shapesize) + (width-1)*(spacing-shapesize) + 2*border
	layoutHeight = height*(shapesize) + (height-1)*(spacing-shapesize) + 2*border
	
    # Convert the layout height and width to proper units
    if units == 1:	# If units are in inches
	layoutWidth *= pts_to_in
	layoutHeight *= pts_to_in
    if units == 2:	# If units are in centimeters
	layoutWidth *= pts_to_cm
	layoutHeight *= pts_to_cm
  
    
    # Set up cairo surface for drawing shapes
    surface = cairo.PDFSurface(filename, layoutWidth, layoutHeight)
    cr = cairo.Context(surface)
    
    # Add the UCSD and E4E logos to the page
    draw_logo(cr)
    

    # This sets to black??  FIX LATER
    if invert:
        cr.set_source_rgb(0,0,0)
        cr.rectangle(0,0,w,h)
        cr.fill()
        cr.save()
	
    
    # Reset the cursor to the upper left-hand corner
    cr.translate(-125,0)
    
    # Move the "cursor" to start drawing inside border
    if units == 1:
        cr.translate(border*pts_to_in, border*pts_to_in)
        cr.scale(shapesize*pts_to_in, shapesize*pts_to_in)
    if units == 2:
        cr.translate(border*pts_to_cm, border*pts_to_cm)
        cr.scale(shapesize*pts_to_cm, shapesize*pts_to_cm)
    
    # Draw patterns
    if pattern == 1:	# Draw fiducials
        draw_cb_fiducials(cr, width, height)
    elif pattern == 2:	# Draw checkerboard
        draw_cb(cr, width, height)
    elif pattern == 3:	# Draw circles
        draw_circles(cr, width, height)
    elif pattern == 4:	# Draw asymmetric circles
        draw_circles_asymmetric(cr, width, height)
    else:
        print 'Unknown pattern. See `python gen_targets.py -h` for help. Exiting.'
	
    # Set up layout for writing file
    pangocairo_context = pangocairo.CairoContext(cr)
    pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

    layout = pangocairo_context.create_layout()
    fontname = "Sans"
    font = pango.FontDescription(fontname + " 0.2")
    layout.set_font_description(font)
    
    
    # Decrease font size if the layoutWidth is too small
    if int(layoutWidth/pts_to_in) <= 11:
	decreaseScale =  (layoutWidth / (10*pts_to_in)) - 0.1
	font.set_size(int(font.get_size() * decreaseScale ))
	layout.set_font_description(font)	# Update the font in the layout


    # Add text description.
    if use_text:
        # Set position of top-left corner of text.
        cr.translate(0,layoutHeight*(1/pts_to_in)-1.8*border)
	
	# Set text to use if units are in inches
	if units == 1:
	    if pattern == 1:
	        layout.set_text(u"{0}x{1} fiducials, {2}in squares, {3}in border".format(width, height, shapesize, border))
	    elif pattern == 2:
	        layout.set_text(u"{0}x{1} checkerboard, {2}in squares, {3}in border".format(width, height, shapesize, border))
	    elif pattern == 3:
	        layout.set_text(u"{0}x{1} circles, {2}in dia., {3}in spacing (center-to-center), {4}in border".format(width, \
				height, shapesize, spacing, border))
	    elif pattern == 4:
	        layout.set_text(u"{0}x{1} asymmetric, {2}in dia., {3}in spacing (center-to-center), {4}in border".format(width, \
				height, shapesize, spacing, border))
	
	# Set text to use if units are in cm
	if units == 2:
	    if pattern == 1:
		layout.set_text(u"{0}x{1} fiducials, {2}cm squares, {3}cm border".format(width, height, shapesize, border))
	    elif pattern == 2:
	        layout.set_text(u"{0}x{1} checkerboard, {2}cm squares, {3}cm border".format(width, height, shapesize, border))
	    elif pattern == 3:
	        layout.set_text(u"{0}x{1} circles, {2}cm dia., {3}cm spacing (center-to-center), {4}cm border".format(width,\
				height, shapesize, spacing, border))
            elif pattern == 4:
                layout.set_text(u"{0}x{1} asymmetric, {2}cm dia., {3}cm spacing (center-to-center), {4}cm border".format(width, \
				height, shapesize, spacing, border))

	# Set color of text (light gray)
	cr.set_source_rgb(0.7,0.7,0.7)
	

    pangocairo_context.update_layout(layout)		# Update layout
    pangocairo_context.show_layout(layout)		# Show layout
	
    # Write to file
    with open(filename, "wb") as image_file:
        surface.write_to_png(image_file)
