#! /usr/bin/env python3


# import libraries
from pssh import ParallelSSHClient
from gevent import joinall
import cgi
import shutil
import os
import subprocess


# get html form data
form = cgi.FieldStorage(keep_blank_values=1)


# initialize ParallelSSHClient information     
hosts = ["RPi1"]    # add hostnames of each Pi here (or IP addresses on network if known)
user = "pi"                # can also do per host configuration; same user and password kept for simplicity
password = "raspberry"
parallel_client = ParallelSSHClient(hosts, user, password)


# most basic command to give before any options are appended; this command will always have options appended to it
command = "raspistill -n"


# process form data by getting all values in form and storing them in variables
sharpness = form.getvalue("sharpness")
contrast = form.getvalue("contrast")
brightness = form.getvalue("brightness")
saturation = form.getvalue("saturation")
ev = form.getvalue("ev")
width = form.getvalue("width")
height = form.getvalue("height")
name = form.getvalue("name")


# append user options to basic command
command += " -sh " + sharpness
command += " -co " + contrast
command += " -br " + brightness
command += " -sa " + saturation
command += " -ev " + ev
command += " -w " + width
command += " -h " + height
command += " -o " + "/home/pi/" + name


# create a folder to store current set images
set_dir = "/var/www/html/img/" + name
os.mkdir(set_dir)


# run commands to take images
output = parallel_client.run_command(command)
parallel_client.join(output)


# transfer all images to web server
greenlets = parallel_client.copy_remote_file(name, set_dir + "/" + name)
joinall(greenlets, raise_error=True)


# delete all images on slave Pis
output = parallel_client.run_command("rm /home/pi/" + name)
parallel_client.join(output)


# add .jpg extension to all images in folder
image_files = os.listdir(set_dir)
for image in image_files:
	os.rename(os.path.join(set_dir, image), os.path.join(set_dir, image + ".jpg"))
image_files = os.listdir(set_dir)  # get updated image files


# zip image set folder to be downloaded
shutil.make_archive(set_dir, "zip", set_dir)


# generate image gallery page
print("Content-type: text/html\n\n")
print("""
<html>
<body>
""")
for image in image_files:
	print("<img src=\"/img/" + name + "/" + image + "\" style=\"width:300px;height:200px;\">")
print("""
<br>
<form method="get" action="index.html">
	<button type="submit"> Main Page </button>
</form>
<br>
<form method="get" action="/img/{}.zip">
	<button type="submit"> Download Set </button>
</form>
""".format(name))

