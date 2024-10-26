# data_241_autumn_2024_2

This repository contains a basic dockerfile that will run a jupyter notebook instance. To build the docker image, please type in:

docker build . -t data241

Note that the image name in the above command is drw

To run the image type in the following:

docker run -p 8888:8888 -v ${PWD}:/tmp data241

as you can see we are running the data241 image.

People
Anuj Agarwal - 4th-year Undergraduate Data Science major
Disha Mohta - 4th-year Undergraduate Economics and Data Science major
Ishani Raj - 3rd-year Undergraduate exchange student
Ken Law - 4th-year Undergraduate MENG major

Folders and Files

Util folder - Our code is in this folder
Data folder - All our data is in this folder

DockerFile - Has instructions to run code and set up proper environment conditions 
requirements.txt - All python/library versions for the project