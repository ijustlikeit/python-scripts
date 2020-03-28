# version 1.0 March 27 2020
# This scripts generates an html file based on a directory of jpg  object images . 

#Instructions:
#
# Install python3 and pip3
# pip install PIL yattag python-crontab

import os
import time
from PIL import Image, ImageDraw, ImageFont
import argparse
from shutil import copyfile
from yattag import Doc, indent
doc, tag, text = Doc().tagtext()

class ImageHtmlGenerator:


    OVERWRITE_THUMBNAIL = False     

    def __init__(self, src_dir, dst_dir, resize, obj_input, cronjob_frequency):
        self.image_files = []

        self.image_root_dir         = src_dir
        self.web_server_dir         = dst_dir
        self.web_server_image_dir   = os.path.join(self.web_server_dir, obj_input)
	self.resize_parm 	    = resize
        self.object_type            = obj_input
        self.cronjob_frequency      = cronjob_frequency

    def generate(self):
        self.search_for_images()
        self.copy_images()
        self.generate_html()
        self.setup_crontab()

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
        print(HTML_FILENAME)
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

			
    def setup_crontab(self):

        if (self.cronjob_frequency is not None):
            from crontab import CronTab

            crontab_comment = 'Object HTML Generator script'
            script_path = os.path.realpath(__file__)
            command = 'python3 ' + script_path +  ' --src ' + self.image_root_dir + ' --dst ' + self.web_server_dir + ' --size ' + self.resize_parm
            print(command)
            my_cron = CronTab(user='don')
            existing_cron_job = None
            for job in my_cron:
                if job.comment == crontab_comment:
                    print ('Updating existing cronjob')
                    existing_cron_job = job

            print('Crontab job command is ' + command)
            if existing_cron_job is None:
                print ('Creating new cronjob')
                existing_cron_job = my_cron.new(command=command, comment=crontab_comment)
            else:
                existing_cron_job.set_command(command)
                
            existing_cron_job.minute.every(self.cronjob_frequency)
             
            my_cron.write()

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

    parser = argparse.ArgumentParser(description='This script takes a source folder of jpg files and generates a webpage.')# You can optionally add --dst to specify a directory where you would like to copy the files to (a web server dir).')
    parser.add_argument('-s','--src', help='Root directory where you have jpg files stored.',required=True)
    parser.add_argument('-d','--dst', help='Directory where you are hosting your web server, where the generated web page will be copied.', required=True)
    parser.add_argument('-r','--size', nargs=2, type=int,  help='Output size')
    parser.add_argument('-o','--object', help='Object type that is to be displayed.', required=True)
    parser.add_argument('-c', '--cronjobp', help='Add an entry to the crontab to start this script periodically.')
    args = parser.parse_args()

    src = args.src + '/' + args.object
    dst = args.dst
    output_size = args.size if args.size else (480,270)
    obj_input = args.object
    cronjob = args.cronjobp
    htmlGenerator = ImageHtmlGenerator(src, dst, output_size, obj_input, cronjob)
    htmlGenerator.generate()

if __name__ == "__main__":
    main()
