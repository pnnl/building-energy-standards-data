#!/bin/bash

echo "Step 1: Clone OSSTD repo"
git clone https://github.com/NREL/openstudio-standards.git
cd openstudio-standards
echo "===="

echo "Step 2: Create new branch data_update_$COMMIT_ID in OSSTD"
git checkout -b data_update
echo "===="

echo "Step 3: Clone data repo"
mkdir data_update
cd data_update
git clone https://github.com/pnnl/building-energy-standards-data.git
cd building-energy-standards-data
echo "CHECKOUT COMMIT ID $COMMIT_ID"
git checkout $COMMIT_ID
echo "===="

echo "Step 4: Update OSSTD data"
cp ../../../build_data.py .
python build_data.py
echo "===="

echo "Step 5: Cleanup local"
cd ../../
rm -rf data_update
echo "===="

echo "Step 6: push new branch to OSSTD github $GHTOKEN (REPLACE TOKEN AFTER TEST!!!)"
git config --global user.email "xuechen.lei@pnnl.gov"
git config --global user.name "Xuechen (Jerry) Lei"
git add --all
git commit -m "data_update $COMMIT_ID"
git remote set-url origin https://leijerry888:$GHTOKEN@github.com/NREL/openstudio-standards.git
git push -u origin data_update
echo "===="
