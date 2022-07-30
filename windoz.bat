@echo off
echo.
echo Notes about how to run grid plotter on Windoze 10
echo.
echo Already should have matplotlib, basemap installed from demos
echo Need a few more libs:
echo    pip install xlrd unidecode pyhamtools serial
echo.
echo This is the first code that references my libs so we need add PYTHONPATH to envrionment
echo  	 - Open Setting & search for environment --> set environment vars for you account
echo	 - New --> PYTHONPATH    ...  C:\Users\Joea\Python\libs
echo	 - Resetart command prompt for this to take effect
echo.
echo To run:
echo.
echo    grids1.py
echo    grids1.py -sat
echo.
echo This will not work until we get cartopy working on winbloz:
echo    grids.py
echo.
echo Do not try standalone exe until get demos/basemap1.exe or
echo demos/cart1/py working
echo.
