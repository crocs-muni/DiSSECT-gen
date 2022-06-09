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

`STD = {x962|brainpool|secg|nums|nist|c25519}` See the details of the individual standards below.

```BITS``` Bit-size of the base field of the generated elliptic curves. See the details of the standards for currently supported bit-sizes.

```[-a/--attempts=ATTEMPTS (default = 1)]``` The number of attempts to generate the elliptic curves. All implemented methods are based on repeated selection of curve parameters (attempts) and checking specified conditions.

```[--tasks NUMBER (default = 1)]```  The number of tasks to run in parallel.

``` [--cofactor_bound BOUND (default = None)]``` Upper bound on the cofactor of the curve. Used if the standards permits more strict upper bound on the cofactor, otherwise ignored.

```[--cofactor_div DIV (default = 0)]``` If ```DIV``` is non-zero then every prime divisor of the cofactor must divide ```DIV```. If the standard does not permit this, it is ignored.

```[-o/--offset OFFSET]``` The offset from the starting seed from which the generation will begin with. See the details of individual standards below.

```[--interpreter PYTHON] ``` choose interpreter. This is either ``sage``, ```sage --python3``` or python of your virtual environment (default).



**Merge**

The generation of curves is parallelized so the resulting curves are distributed into multiple files.

```python3 merge -s [x962,brainpool,...,all] ``` will merge the files together.



### Standards

**X9.62/NIST/SECG**

- Run with ```python dissectgen.py x962 BITS```
- Currently supported bit-sizes: 112, 128, 160, 192, 224, 256, 384, 521. Edit ```standards/parameters/patemeters_x962.json``` to extend the support.
- The curve generation method is implemented according to [this specification](https://webstore.ansi.org/Standards/ASCX9/ansix9621998) (the original 1998 version of the X9.62 standard). The base field primes are fixed and taken from the specification. 
- The attempts correspond to the values of the parameter $b$ of the [Weierstrass form](https://en.wikipedia.org/wiki/Elliptic_curve). See the standard for more details. The initial seeds were taken from standard corresponding to the standardized curves.
- A slightly different version of this algorithm was standardized in [a NIST specification](https://csrc.nist.gov/publications/detail/fips/186/4/final). You can run this version with ```python dissectgen.py nist BITS``` with supported bit-sizes: 160, 192, 224, 256, 384, 521. 
- Another version of this algorithm was described in the [SECG specification](https://www.secg.org/sec1-v2.pdf). You can run this version with ```python dissectgen.py secg BITS``` with supported bit-sizes: 112, 128, 160, 192, 224, 256, 384, 521. 

**Brainpool**

- Run with ```python dissectgen.py brainpool BITS```
- Currently supported bit-sizes: 160, 192, 224, 256, 320, 384, 512. Edit ```standards/parameters/patemeters_brainpool.json``` to extend the support.
- The curve generation method is implemented according to [this specification](https://datatracker.ietf.org/doc/html/rfc5639). The base field primes are fixed and taken from the specification. 
- The attempts correspond to the values of the parameters $a,b$ of the [Weierstrass form](https://en.wikipedia.org/wiki/Elliptic_curve). The exact derivation of these parameters from an initial seed is using a hash function and is rather convoluted. See the specification for more details. The initial seeds in this implementation are the ones corresponding to the standardized curves.
- All Brainpool curves have cofactor 1 and any requirements on the cofactor (see options above) will be ignored.

**NUMS**

- Run with ```python dissectgen.py NUMS BITS  ```
- Currently supported bit-sizes: 160, 192, 224, 256, 384, 521. Edit ```standards/parameters/patemeters_nums.json``` to extend the support.
- The curve generation method is implemented according to [this specification](https://datatracker.ietf.org/doc/html/draft-black-numscurves-02). The base field primes are all fixed. The primes for bit-sizes >256 were taken from the specification. The rest of them were generated using the algorithm in the specification.
- The attempts correspond to incremented values (seeds) of the parameter $b$ in the  [Weierstrass form](https://en.wikipedia.org/wiki/Elliptic_curve). The initial seeds is 1 for bit-sizes <256 and the rest of them correspond to the standardized curves.
- All NUMS curves have cofactor 1 and any requirements on the cofactor (see options above) will be ignored.

**Curve25519**

- Run with `python dissectgen.py c25519 BITS `
- Currently supported bit-sizes: 159, 191, 255. Edit ```standards/parameters/patemeters_c25519.json``` to extend the support.
- The curve generation method is implemented according to [this specification](https://datatracker.ietf.org/doc/html/rfc7748). The base field primes are fixed and were selected according to the [original paper](https://www.iacr.org/cryptodb/archive/2006/PKC/3351/3351.pdf), i.e. $2^{32k-e}-c$ where $c$ is as small as possible and $e \in \{1,2,3\}$. 
- The attempts correspond to incremented values (seeds) of $\frac{A-2}{4}$ where $A$ is the parameter of the [Montgomery form](https://en.wikipedia.org/wiki/Montgomery_curve). The starting value (seed) is 1 for bit-sizes 159, 191 and 121666 for 255 (121665 corresponds to the original Curve25519).
- All Curve25519 curves have cofactor 8 and any requirements on the cofactor (see options above) will be ignored.



### Example

``python3 dissectgen.py x962 192 -a 200 --tasks 10`` Iterates through 200 elliptic curves to find curves satisfying the X9.62 conditions and outputs 10 files.
``python3 merge.py -s x962`` Merges all files together.
