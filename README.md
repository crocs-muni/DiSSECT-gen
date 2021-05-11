# DiSSECT-gen

This is a SageMath implementation of the elliptic curve generation according to the standards x9.62, Brainpool, SECG

### Requirements
The implementation is written in Python 3 and imports SageMath. It is recommended to create virtual environment:
``sage --python3 -m venv --system-site-packages environment``
The following packages are required: ``shellescape``, ``sarge``
```pip3 install shellescape, sarge```
It is recommended to also have installed: ``coloredlogs``

### Usage
```python3 dissectgen.py STD -t COUNT```

##### standards

x962, brainpool, secg

##### options

```-i/--interpreter PYTHON ``` choose interpreter. This is either ``sage``, ```sage --python3``` or python of your virtual environment pointing to ```sage --python3``` (see requirements above)

```-b/--bits BITS``` bitsize of the elliptic curve. Must be specified in ```standards/parameters/parameters_*.json```. Currently: Brainpool (160, 192, 224, 256, 320, 384), SECG and x962 (112, 128, 160, 192, 224, 256, 384, 521). 

```-p/--config_path PATH``` The seed for a given bitsize is specified in ```standards/parameters/parameters_*.json```. The path can be changed to PATH.

```-t/--total_count COUNT``` Number of seeds to try for generating elliptic curves.

```-u/--cofactor [1/0 (default)]``` If 1 then cofactor is forced to 1. Otherwise, ignored and proceed according to the standard.

```-o/--offset OFFSET``` This specifies the offset from the starting seed from which the generation will begin with. 

```--tasks NUMBER``` Specifies the number of tasks to run in parallel.

```-c/--count COUNT``` Specifies number of seeds per task.

```--results PATH``` Path to the location where the resulting curves should be stored.



####  Merge

The generation of curves is parallelized so the resulting curves are distributed into multiple files.

```python3 merge -s [x962/brainpool/secg/all] -r PATH_TO_RESULTS -p PATH_TO_PARAMS``` will merge the files together

#### Examples
``python3 dissectgen.py x962 -b 192 -t 100 -u 1``
``python3 merge.py -s x962``