Accelerator, radiation and x-ray optics simulation framework

# An Introduction to Ocelot

Ocelot is a multiphysics simulation toolkit designed for studying Free Electron Lasers (FEL) and storage ring-based light sources. Implemented in Python, Ocelot caters to researchers seeking the flexibility provided by high-level languages like Matlab and Python. Its core principle revolves around scripting beam physics simulations in Python, utilizing Ocelot's modules and extensive collection of Python libraries.

Users developing high-level control applications can accelerate development by using physics models from Ocelot and Python graphics libraries such as [PyQt](http://pyqt.sourceforge.net/Docs/PyQt5/) and [PyQtGraph](http://www.pyqtgraph.org/) to create a GUI. 

Developing machine learning (ML) applications for accelerators can also benefit from using Ocelot, as many popular ML frameworks are written in Python. Ocelot provides a seamless connection between physics and ML methods, making it easier to integrate physical accelerator simulators with machine learning algorithms.

## Contents
1. [Ocelot main modules](#modules)
2. [Ocelot installation](#installation)
3. [Tutorials](#tutorials)


## Ocelot main modules:
<a id='modules'></a>

* **Charged particle beam dynamics module (CPBD)**
    - optics
    - tracking
    - matching
    - collective effects (description can be found [here](http://vrws.de/ipac2017/papers/wepab031.pdf) and [here](https://journals.aps.org/prab/abstract/10.1103/PhysRevAccelBeams.22.024401))
        - Space Charge (3D Laplace solver)
        - CSR (Coherent Synchrotron Radiation) (1D model with arbitrary number of dipoles).
        - Wakefields (Taylor expansion up to second order for arbitrary geometry).
    - MOGA (Multi Objective Genetics Algorithm) [ref](http://accelconf.web.cern.ch/AccelConf/ipac2016/papers/thpmb034.pdf).
* **Native module for spontaneous radiation calculation** (some details can be found [here](http://accelconf.web.cern.ch/AccelConf/ipac2019/papers/wepts017.pdf) and [here](http://scripts.iucr.org/cgi-bin/paper?S1600577519002509))
* **FEL calculations: interface to GENESIS and pre/post-processing**
* **Modules for online beam control and online optimization of accelerator performances.**   [ref1](http://accelconf.web.cern.ch/accelconf/IPAC2014/papers/mopro086.pdf), [ref2](https://jacowfs.jlab.org/conf/y15/ipac15/prepress/TUPWA037.PDF), [ref3](http://accelconf.web.cern.ch/AccelConf/ipac2016/papers/wepoy036.pdf), [ref4](https://arxiv.org/pdf/1704.02335.pdf).
    - This module is being developed in collaboration with SLAC. The module has been migrated to a separate [repository](https://github.com/ocelot-collab/optimizer) (in [ocelot-collab](https://github.com/ocelot-collab) organization) for ease of collaborative development.

Ocelot extensively  uses Python's [NumPy (Numerical Python)](http://numpy.org) and [SciPy (Scientific Python)](http://scipy.org) libraries, which enable efficient in-core numerical and scientific computation within Python and give you access to various mathematical and optimization techniques and algorithms. To produce high quality figures Python's [matplotlib](http://matplotlib.org/index.html) library is used.

It is an open source project and it is being developed by physicists from  [The European XFEL](http://www.xfel.eu/), [DESY](http://www.desy.de/) (Germany), [NRC Kurchatov Institute](http://www.nrcki.ru/) (Russia).

We still have no documentation but you can find a lot of examples in /demos/ folder and jupyter [tutorials](#tutorials)

## Ocelot installation
<a id='installation'></a>

### Requirements
-  Python 3.9+
- `numpy` version 1.8 or higher: http://www.numpy.org/
- `scipy` version 0.15 or higher: http://www.scipy.org/
- `matplotlib` version 1.5 or higher: http://matplotlib.org/
- `h5py` version 3.10 or higher, https://www.h5py.org

**Optional**, but highly recommended for speeding up calculations

- numexpr (version 2.6.1 or higher)
- pyfftw (version 0.10 or higher)
- numba

**Orbit Correction module is required**
- `pandas`

### Installation
#### GitHub (for advanced python users)
Clone OCELOT from GitHub:
```
$ git clone https://github.com/ocelot-collab/ocelot.git
```
or download last release [zip file](https://github.com/ocelot-collab/ocelot/archive/v24.03.0.zip).
Now you can install OCELOT from the source:
```
$ python setup.py install
```

#### Anaconda Cloud (recommended)
The easiest way to install OCELOT is to use Anaconda cloud. In that case use command:
 ```
 $ conda install -c ocelot-collab ocelot
 ``` 

#### PythonPath
Another way is download ocelot from [GitHub](https://github.com/ocelot-collab/ocelot)
1. you have to download from GitHub [zip file](https://github.com/ocelot-collab/ocelot/archive/master.zip).
2. Unzip ocelot-master.zip to your working folder **/your_working_dir/**.
3. Add **../your_working_dir/ocelot-master** to PYTHONPATH
    - **Windows 7:** go to Control Panel -> System and Security -> System -> Advance System Settings -> Environment Variables.
    and in User variables add **/your_working_dir/ocelot-master/** to PYTHONPATH. If variable PYTHONPATH does not exist, create it

    Variable name: PYTHONPATH

    Variable value: ../your_working_dir/ocelot-master/
    - Linux:
    ```
    $ export PYTHONPATH=/your_working_dir/ocelot-master:$PYTHONPATH
    ```

## Tutorials
<a id='tutorials'></a>

* [Introduction. Tutorial N1. Linear optics](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/1_introduction.ipynb)
    - Linear optics. Double Bend Achromat (DBA). Simple example of usage OCELOT functions to get periodic solution for a storage ring cell.
* [Tutorial N2. Tracking](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/2_tracking.ipynb)
    - Linear optics of the European XFEL Injector.
    - Tracking. First and second order.
    - Artificial beam matching - BeamTransform
* [Tutorial N3. Space Charge](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/3_space_charge.ipynb)
    - Tracking through RF cavities with SC effects and RF focusing.
* [Tutorial N4. Wakefields](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/4_wake.ipynb)
    - Tracking through corrugated structure (energy chirper) with Wakefields
* [Tutorial N5. CSR](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/5_CSR.ipynb)
    - Tracking trough bunch compressor with CSR effect.
* [Tutorial N6. RF Coupler Kick](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/6_coupler_kick.ipynb)
    - Coupler Kick. Example of RF coupler kick influence on trajjectory and optics.
* [Tutorial N7. Lattice design](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/7_lattice_design.ipynb)
    - Lattice design, twiss matching, twiss backtracking
* [Tutorial N8. Physics process addition. Laser heater](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/8_laser_heater.ipynb)
    - Theory of Laser Heater, implementation of new Physics Process, track particles w/o laser heater effect.
* [Tutorial N9. Tracking with parallel-plate corrugated structures](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/9_thz_source.ipynb)
    - A simple accelerator with the electron beam formation system and an undulator to generate THz radiation.
* [Tutorial N10. Simple accelerator based THz source](https://nbviewer.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/10_CorrugatedStructures.ipynb)
    - In this tutorial, a few examples for tracking with parallel-plate corrugated structures are shown. The wakefields model are based on analytical wakefield formulas for flat corrugated structures. 

#### Photon field simulation

* [PFS tutorial N1. Synchrotron radiation module](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/pfs_1_synchrotron_radiation.ipynb).
    - Simple examples how to calculate synchrotron radiation with OCELOT Synchrotron Radiation Module.
* [PFS tutorial N2. Coherent radiation module and RadiationField object](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/pfs_2_radiation_field.ipynb).
* [PFS tutorial N3. Reflection from imperfect highly polished mirror](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/pfs_3_imperfect_mirror.ipynb).
* [PFS tutorial N4. Converting synchrotron radiation Screen object to RadiationField object for viewing and propagation](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/pfs_4_synchrotron_radiation_visualization.ipynb).
* [PFS tutorial N5: SASE estimation and imitation](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/pfs_5_SASE_Estimator_and_Imitator.ipynb).

#### Appendixes
* [Undulator matching](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/undulator_matching.ipynb).
    - brief theory and example in OCELOT
* [Some useful OCELOT functions](http://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/small_useful_features.ipynb)
    - Aperture, RK tracking 
* [Example of an accelerator section optimization](https://nbviewer.jupyter.org/github/ocelot-collab/ocelot/blob/master/demos/ipython_tutorials/accelerator_optim.ipynb)
    - A simple demo of accelerator section optimization with a standard scipy numerical optimization method. 


#### To launch "ipython notebook" or "jupyter notebook"

If you want to play with these tutorials they can be found in `ocelot/demos/ipython_tutorials`. 
Run the following commands in the command line:

```
$ ipython notebook
```
or 

```
jupyter lab
```


## Documentation
The API documentation can be build using [sphinx](https://sphinx.org).
To do so, you have to clone the repository or download the zip file, as explained in the [ocelot installation section](#ocelot-installation).
Then you can install all dependencies by running
``` bash
python -m pip install -r docs/requirements.txt
python setup.py install
```
Now you can build the documentation by running
```
python setup.py build_sphinx
```
If these steps succeeded (yes, there are still very many errors and warnings during building the documentation),
you can browse the HTML documentation by opening `build/sphinx/html/index.html` in your browser.


**Disclaimer:** The OCELOT code comes with absolutely NO warranty. The authors of the OCELOT do not take any responsibility for any damage to equipments or personnel injury that may result from the use of the code.
