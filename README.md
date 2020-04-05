# python-scripts
 
<h2> object_html_generator.py </h2>
<p>
Input is folder with subfolders named as objects (person, car, dog).  In these subfolders are jpeg images (that I my case have been identified by google coral AI and boxes drawn around them) of said object type (eg person).  So the end result is a object html file (eg person.html) that has thumbnails in a grid of 4 per row that can be clicked on to expand to the full image.
This script generates html files from subdirectories of type object.  So for example if you specify "person" as the object parameter this script will scan the person subdirectory and create html to view the jpegs within that subdirectory and store the images,thumbnails, and person.html files in the parameter specified directory (--dst) where you are hosting your web server.
Multiple objects can be specified by listing them separated by commas eg.  --object 'person,car,dog'.  
If the directory where you are storing the html does not yet have a subdirectory for the object, eg 'person', one will be created for you.
The contents of the --src directory will remain unchanged.
Only works with .jpeg files
Install into crontab with 'crontab -e' as follows:
*/15 * * * * sudo python /yourlocation/object_html_generator.py --src /yourobjectimages  --dst /var/www/yourserver/ --size 0480 270 --object 'person,car,dog'
where /15 means run every 15 minutes; /yourlocation/ is where you chose to save your python scripts;  /yourobjectimages/ root directory containing subfolders of object type; size is the size of the thumbnail to be generated; and of course /yourserver/ is location your web server is configured to serve web pages from.



</p>



