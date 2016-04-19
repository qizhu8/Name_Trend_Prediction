# Name_Trend_Prediction

The code and project can be found in 

https://github.com/qizhu8/Name_Trend_Prediction

## Description for file
./code  directory for code and dataset
./finalReport   directory for final report file
README.md

## Introduction
This is the workspace for UM EECS564 Final Data Project.
This project focuses on 
1) Slope Detection
2) Epidemic Model for Name
3) Spreading Model for New Names

## Request
This project uses MySQL and PYTHON. Make sure you have them installed in your machine.

## Usage and Introduction
Because the datafile is too large, I upload the compressed zip file "namesbystate.zip" rather than raw datafile. Also, this file can be downloaded from http://www.ssa.gov/oact/babynames/state/namesbystate.zip

### Prepare job
 * step 1: Extract data to ./namesbystate
 go into ./code/ and unzip file to ./code/namesbystate/
 for linux user, you may use
```
unzip namesbystate.zip -d ./namesbystate
```
 to unzip the file. 

 * step 2: open mysql and create database
 for command users, you need to use terminal and type 
```
mysql -u username -p passward
```
then type 
```
create database if not exists eecs564 ;
```
If success, you will see "Query OK, 1 row affected (0.00 sec)"

* step 3 feed in data
You need to open "pre_process.py" file, and replace **"username" and "password" with your own username and password for MySql**. Then run the file.
The whole process may take 10 minutes, largely depends on your machine. Don't quit the process even if it seem not respond. 

### run and get the result
run the "main.py" file.

**Note that, the whole process may take more than one hours!!!**


## Final Report
Directory "finalReport" contains the report file. You can try to compile the tex file or just open the pdf
