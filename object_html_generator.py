# version 1.1 April 5, 2020
# This script generates html files from subdirectories of type object.  So for example if you specify "person" as the object parameter this script will scan the person
# subdirectory and create html to view the jpegs within that subdirectory and store the images,thumbnails, and person.html files in the parameter specified directory
# (--dst) where you are hosting your web server.
# Multiple objects can be specified by listing them separated by commas eg.  --object 'person,car,dog'  
# If the directory where you are storing the html does not yet have a subdirectory for the object, eg 'person', one will be created for you
# The contents of the --src directory will remain unchanged.
# Only works with .jpeg files
# Install into crontab with 'crontab -e' as follows:
#*/15 * * * * sudo python /yourlocation/object_html_generator.py --src /yourobjectimages  --dst /var/www/yourserver/ --size 0480 270 --object 'person,car,dog'
# where /15 means run every 15 minutes; /yourlocation/ is where you chose to save your python scripts;  /yourobjectimages/ root directory containing subfolders of 
# object type; size is the size of the thumbnail to be generated; and of course /yourserver/ is location your web server is configured to serve web pages from.

# Other Instructions:
#
# Requires PIL and yattag so  pip install PIL yattag 

import os
import time
from PIL import Image, ImageDraw, ImageFont
import argparse
from shutil import copyfile
from yattag import Doc, indent
doc, tag, text = Doc().tagtext()

class ImageHtmlGenerator:


    OVERWRITE_THUMBNAIL = False     

    def __init__(self, src_dir, dst_dir, resize, obj_input):
        self.image_files = []

        self.image_root_dir         = src_dir
        self.web_server_dir         = dst_dir
        self.web_server_image_dir   = os.path.join(self.web_server_dir, obj_input)
	self.resize_parm 	    = resize
        self.object_type            = obj_input
       

    def generate(self):
        self.search_for_images()
        self.copy_images()
        self.generate_html()
        

    def search_for_images(self):

        print ('Searching ' + self.image_root_dir + ' for jpg files...')

        for dirpath, dnames, fnames in os.walk(self.image_root_dir):
            for f in fnames:
                if f.endswith('.jpg'):
                    file_path = os.path.join(dirpath, f)
                    # print('Found jpg file at ' + file_path)
                    self.image_files.append(file_path)

        self.image_files.sort(reverse=True)

        if len(self.image_files) == 0:
            print ('No image jpg files found!')
        else:
            print(len(self.image_files), 'image jpg files found')


    # Copy the jpgs to the web server directory so it can serve them
    def copy_images(self):

        print ('Copying image jpg files to ' + self.web_server_image_dir)

        if not os.path.exists(self.web_server_image_dir):
            os.mkdir(self.web_server_image_dir)

        skipped = 0
        copied = 0

        for file_path in self.image_files:
            head, filename = os.path.split(file_path)   
            dst_filepath = os.path.join(self.web_server_image_dir, filename)

            if os.path.exists(dst_filepath):
                # print(filename + ' already exists in destination folder.')
                skipped += 1
            else:
                print('Copying images to ' + dst_filepath)
                copied += 1
                copyfile(file_path, dst_filepath)
                                

        if skipped > 0:
            print('Skipped copy of', skipped, 'existing image files')
        if copied > 0:
            print('Copied', copied, 'image files.')

    def generate_html(self):
        doc, tag, text = Doc().tagtext()
        if len(self.image_files) == 0:
           htmlheadertext = 'No images with type ' + self.object_type + ' found!'
        elif len(self.image_files) == 1:
           htmlheadertext = 'There is ' + str(len(self.image_files)) + ' image with type ' + self.object_type +  ' found, click on the thumbnail to view the full size image'
        else:
           htmlheadertext = 'There are ' + str(len(self.image_files)) + ' images with type ' + self.object_type +  ' found, click on the thumbnail to view the full size image'

        with tag('html'):
		  with tag('head'):
		    doc.asis('<style> .grid-container {display: grid; grid-template-columns: auto auto auto auto; grid-template-rows: 210px; grid-gap: 10px; background-color: #5aaeed; padding: 10px; }')
                    doc.asis('.grid-container > div { background-color: rgba(255, 255, 255, 0.6); text-align: center; padding: 20px 0; font-size: 30px;} </style>')
						   
						  

        with tag('body'):
                 with tag('div'):
                        with tag('h3',style="color:blue;"):
                            text(htmlheadertext)

                 doc.asis('<div class="grid-container" style="grid-auto-flow: row;">')
                 for index, pic_path in enumerate(self.image_files):
                        head, pic_filename = os.path.split(pic_path)
                        doc.asis('<div class="item1">')
                        with tag('a', href=self.object_type + '/' + pic_filename, target="_blank"):

                                link_text = pic_filename

                                output_image_path = pic_path.strip('.jpg') + '.png'
                                head, image_filename = os.path.split(output_image_path)

                                print('Thumbnail', index + 1, 'of', len(self.image_files))
                                self.generate_thumbnail(image_path=pic_path, output_image_path=output_image_path)
                                
                                doc.stag('img', src=self.object_type + '/' + image_filename, width='300')
			doc.asis('</div>')
                 doc.asis('</div>')

        # Write the HTML to disk
        
        html_text = indent(doc.getvalue(), indent_text = True)
        HTML_FILENAME = self.object_type + '.html'
        
        html_filepath = os.path.join(self.web_server_dir, HTML_FILENAME)

        print ('Generating html file at ' + html_filepath)
        file = open(html_filepath, 'w+')
        file.write(html_text)
        file.close()

    def generate_thumbnail(self, image_path, output_image_path):
        head, image_filename = os.path.split(output_image_path)
        image_output_path = os.path.join(self.web_server_image_dir, image_filename)

        if os.path.exists(image_output_path) and not self.OVERWRITE_THUMBNAIL:
            print(image_filename + ' thumnail already exists.')
        else:
            print('Generating thumbnail at ' + output_image_path)
	    resizeImagewithText(image_path, self.web_server_image_dir, self.resize_parm)  

			


def resizeImagewithText(infile, output_dir, size):
    outfile = os.path.splitext(os.path.basename(infile))[0]
    extension = os.path.splitext(infile)[1]

    if infile != outfile:
       try:
            im = Image.open(infile)
            im.thumbnail(size, Image.ANTIALIAS)
            file_temp_save_path = os.path.join(output_dir, outfile)+'.png'
            im.save(file_temp_save_path)
            im = Image.open(file_temp_save_path)
            fnt = ImageFont.truetype('/usr/share/fonts/truetype/msttcorefonts/Verdana.ttf', size=32)
	    (x, y) = (30, 225)
            last_mod_time = time.ctime(os.path.getmtime(infile))
	    txt =  last_mod_time  
	    color = 'rgb(255, 250, 250)' # snow white
            d = ImageDraw.Draw(im) 
            d.text((x, y), txt, fill=color, font=fnt)
            im.save(file_temp_save_path)
			
       except IOError:
            print("cannot reduce image for ", infile)

def main():

    parser = argparse.ArgumentParser(description='This script takes a source subfolder(s) of jpg files and generates a webpage.')
    parser.add_argument('-s','--src', help='Root directory where you have jpg files stored.',required=True)
    parser.add_argument('-d','--dst', help='Directory where you are hosting your web server, where the generated web page will be copied.', required=True)
    parser.add_argument('-r','--size', nargs=2, type=int,  help='Output size')
    parser.add_argument('-o','--object', help='Object list that html will be generated for.', required=True)
    args = parser.parse_args()

#    src = args.src + '/' + args.object
    dst = args.dst
    output_size = args.size if args.size else (480,270)
    obj_input = args.object
    obj_list = list(obj_input.split(","))
    print('Generating html for the following objects: ', obj_list)
    for ind_obj in obj_list:
        src = args.src + '/' + ind_obj
        print('Doing ', src, ' subfolder now')
        htmlGenerator = ImageHtmlGenerator(src, dst, output_size, ind_obj)
        htmlGenerator.generate()
        print('Finished processing object ', ind_obj)

if __name__ == "__main__":
    main()
