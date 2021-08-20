# README
Changed by me
> GUI for KMGEsim

![GUI](https://github.com/KMGEsim/KMGEsim_TP/blob/master/f100int10.gif)

## Getting Started

## Installation
### Window Python Installation Guide

1. Downlaod the [Python 3.7.0](https://www.python.org/ftp/python/3.7.0/python-3.7.0.exe) from the official website.

	**Remember to check the `Add Python to path` option as shown below**

	![window-installation](https://raw.githubusercontent.com/sunwaytechclub/Python-Installation-Guide/master/pictures/window-install.jpg)

2. Open terminal and make sure you had successfully install Python and had been added to path

	```
	> python --version

	# Make sure the output should be 3.6.* or 3.7.*
	```
Install virtualenv:

```sh
> pip install virtualenv # install virtualenv
> mkdir <Repo name> # create folder
> cd <Repo name> # change directory
> virtualenv env # create virtual enviroment
> env\Scripts\activate # activate virtual env
> git clone https://github.com/KMGEsim/KMGEsim_VS.git # clone repository
> cd KMGEsim_VS # got to folder KMGEsim_VS
> pip install -r requirements.txt # install requirements packages
> ..\env\Scripts\deactivate # deactivate enviroment
```

Renew repository:

```sh
> git pull # pulling repo
> ..\env\Scripts\activate # activate virtual env
> pip install -r requirements.txt # install requirements packages
```
Push repository:
```sh
> git status # check the status of the file
> git add . # adding new changes
> git commit -m "Comment info" # commit changes
> git push origin main # pushing repo
```
