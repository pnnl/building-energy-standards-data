#!/bin/bash

echo "Step 1: Clone OSSTD repo"
git clone https://github.com/NREL/openstudio-standards.git
cd openstudio-standards
echo "===="

echo "Step 2: Create new branch data_update_$COMMIT_ID in OSSTD"
git checkout -b data_update_${COMMIT_ID:0:7}
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

echo "Step 6: push new branch to OSSTD github (currently updating economizers (**/*economizers*.json.json) data only)"
git config --global user.email "xuechen.lei@pnnl.gov"
git config --global user.name "Xuechen (Jerry) Lei"
git add **/*economizers*.json
#git add **/*vrfs*.json
#git add **/*construction_properties*.json
#git add **/*heat_pumps*.json
#git add **/*motor*.json
#git add **/*heat_rejection*.json
#git add **/*unitary_acs*.json
#git add **/*water_heater*.json
#git add **/*furnace*.json
#git add **/*boiler*.json
#git add **/*chiller*.json
git commit -m "data_update (construction_propeties_only) ${COMMIT_ID:0:7}"
git remote set-url origin https://leijerry888:$GHTOKEN@github.com/NREL/openstudio-standards.git
git push -u origin data_update_${COMMIT_ID:0:7}
echo "===="
