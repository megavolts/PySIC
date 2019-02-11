seaice
==========

seaice is a script collection developped to work with ice core data. The project origined with the need of importing ice core data saved under excel xlsx format during the operation of SiZONET project (https://eloka-arctic.org/sizonet) into python for processing. In the later years, seaice has been further developped to compute various seaice properties, based on semi-empirical equations described in the litterature, aggregate ice cores for statistical analysis, plot easily profile of physical variable.

seaice is currently getting revamped and worked into a module to ease its use and installation

## Installation and Dependencies:


## Setup
Read [INSTALLATION.md](INSTALLATION.md)

## Quickstart
Clone the repository

```bash
$ git clone https://github.com/..
$ cd seaice
$ python example.py
```

## Variable

### salinity
- salinity [ppt or g/kg] : salinity of the solution 
- conductivity  [mS/cm] : conductivity of the solution at any temperature
- conductivity temperature [°C] : temperature of the solution  when conductivity is measured
- specific conductance [mS/cm] : temperature compensated conductivity; reference temperature is T = 25 °C. Also known as temperature compensated conductivity [1] (Defined by YSI)

### temperature


## Abreviation
- ms : milliSiemens
- cm : centimeter
- °C : degree Celsius


### Sources
[1]: https://www.ysi.com/File%20Library/Documents/Manuals%20for%20Discontinued%20Products/030136-YSI-Model-30-Operations-Manual-RevE.pdf
