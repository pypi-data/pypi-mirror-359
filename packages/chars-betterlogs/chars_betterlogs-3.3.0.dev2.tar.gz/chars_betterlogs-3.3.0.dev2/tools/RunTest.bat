@echo off
cd ..\
mkdir "tests\chars_betterlogs"
copy "chars_betterlogs\*" "tests\chars_betterlogs\*"
cd tests\
python testerScript.py -help -testingScript_BLP
pause