# python-scripts
 
<h2> object_html_generator.py </h2>
<p>
in progress


</p>

Install instructions:
1. 
2. Install python3 and pip3
3. pip install  yattag

Usage:
`python object-html-generator.py --src /coralai/objects --dst /var/www/yoursite/ --size 480 270 --object person`

--src is the source  root folder where you have your image objects are stored.<br>
--dst is the destination folder where you will host the site.<br>
--size is the size of the thumbnail tuple (480 270).<br>
--object is the object type that Coral AI has detected (eg person, car, book etc).<br>

Note: It is currently hard coded to only support jpg formats.
