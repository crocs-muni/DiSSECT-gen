# DiSSECT-gen

A [SageMath](https://www.sagemath.org/) implementation of elliptic curve generation according to popular standards or recommendations.

### Requirements

The implementation is written in Python 3 and imports SageMath. It is recommended to create virtual environment:

``sage --python3 -m venv --system-site-packages environment``

Installation:

``pip install -r requirements.txt``

### Usage

```python3 dissectgen.py STD BITS ```

**Options**

`STD = {x962|brainpool|secg|nums|nist|bls|c25519}` See more details about individual standards below.

```BITS``` Bit-size of the base field of the generated elliptic curves. See details of the standards for currently supported bit-sizes.

```-a/--attempts=ATTEMPTS``` Number of attempts to generate elliptic curves. All implemented methods are based on repeated selection of curve parameters (attempts) and checking specified conditions.

```-u/--cofactor [1/0 (default)]``` If 1 then cofactor is forced to 1. Otherwise, ignored and proceed according to the standard.

```-o/--offset OFFSET``` This specifies the offset from the starting seed from which the generation will begin with.

```--interpreter PYTHON ``` choose interpreter. This is either ``sage``, ```sage --python3``` or python of your virtual environment (default).

```--tasks NUMBER``` Specifies the number of tasks to run in parallel (default 1).



**Merge**

The generation of curves is parallelized so the resulting curves are distributed into multiple files.

```python3 merge -s [x962/brainpool/.../all] -r PATH_TO_RESULTS -p PATH_TO_PARAMS``` will merge the files together.



### Standards

X9.62

Brainpool

SECG

NUMS

NIST

BLS

**Curve25519**

- The curve generation method is implemented according to [this specification](https://datatracker.ietf.org/doc/html/rfc7748). The base field prime is selected according to the [original paper](https://www.iacr.org/cryptodb/archive/2006/PKC/3351/3351.pdf), i.e. $2^{32k-e}-c$ where $c$ is as small as possible and $e \in \{1,2,3\}$.
- Run by `python3 dissectgen.py c25519 -t COUNT`
- 



### Examples

``python3 dissectgen.py x962 -b 192 -t 100 -u 1``
``python3 merge.py -s x962``
