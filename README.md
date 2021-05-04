# DiSSECT-gen

This is a SageMath implementation of the elliptic curve generation according to the standards x9.62, Brainpool, SECG

### Requirements
The implementation is written in Python 3 and imports SageMath. It is recommended to create virtual environment:
``sage --python3 -m venv --system-site-packages environment``
The following packages are required: ``shellescape``, ``sarge``
```pip3 install shellescape, sarge```
It is recommended to also have installed: ``coloredlogs``

### Usage
```dissectgen -s STD -t COUNT```

##### standards

```-s/--standard [x962/brainpool/secg]```

##### options

```-i/--interpreter PYTHON ``` choose interpreter. This is either ``sage``, ```sage --python3``` or python of your virtual environment pointing to ```sage --python3``` (see requirements above)



```-b/--bits BITS``` bitsize of the elliptic curve. Must be supported by the standard or specified in ```standards/parameters/parameters_*.json```. Currently: Brainpool (160, 192, 224, 256, 320, 384), SECG and x962 (112, 128, 160, 192, 224, 256, 384, 521). 

```-p/--configpath PATH``` The seed for a given bitsize is specified in ```standards/parameters/parameters_*.json```. The path can be changed to PATH.

```-t/--totalcount COUNT``` number seeds to try for generating elliptic curves

```-u/--cofactor [1/0 (default)]``` If 1 then cofactor is forced to 1. Otherwise  any cofactor supported by the standard is permitted.

```-o/--offset OFFSET``` This specifies the offset from the starting seed from which the generation will begin with. 

```--tasks NUMBER``` Specifies the number of tasks to run in parallel.

```-c/--count COUNT``` number of seeds per task

```--resdir PATH``` Path to the location where the resulting curves should be stored.



####  Merge

The generation of curves is parallelized so the resulting curves are distributed into multiple files.

```merge -s [x962/brainpool/secg] -r PATH_TO_RESULTS -p PATH_TO_PARAMS``` will merge the files together