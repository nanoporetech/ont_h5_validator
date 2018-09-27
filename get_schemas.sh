
COMMIT_HASH=$(python -c "from h5_validator import SCHEMA_VERSION; print(SCHEMA_VERSION)")

git clone https://git.oxfordnanolabs.local/data-integration/data-contract.git --quiet
cd data-contract
git checkout $COMMIT_HASH --quiet

rm -rf ../h5_validator/schemas
cp reads ../h5_validator/schemas -r

cd ../
rm -rf data-contract

echo "Successfully copied schemas from https://git.oxfordnanolabs.local/data-integration/data-contract.git ${COMMIT_HASH}"
