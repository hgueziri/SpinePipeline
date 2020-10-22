# Pre-processing pipeline for spine surgery

This pipeline is intended to prepare preoperative CT data for ultrasound-based spine surgery neuronavigation. 

## Input data

Input data are expected to be preoperative CT of patient in supine position.

## Output data

The scripts allow to two functionalities:
- Rotate CT images from supine to prone position
- Extract the posterior surface of the vertebra

# Pre-requirement

- python 2.7 or later
- virtualenv

```sudo apt-get install python-dev virtualenv```

# Installation

Run `install.sh` script:
```./install.sh```

# Running

```./SpinePipeline -rp -i inputFile [-o outputFile] [-t 150]```

## Options:
	-i 	 the file containing the CT image
	-o 	 (optional) the file containing the rotated MINC file. If not specified, the command overwrites inputFile.

	-r 	Rotate input image from LPS to RAS
	-p 	Extract posterior surface of vertebra
	-t 	Threshold value in H.U. (default 150)

	-h 	Display help message
	-v 	Verbose mode

