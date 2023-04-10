#!/usr/bin/bash

cd docs
make clean
make html

git checkout --orphan doc-branch
find . -type f -not -name 'docs' -delete
cd docs
cp _build/html/*.html .

cd ..
git add docs

git config user.name "jdenholm"
git config user.email "j.denholm.2017@gmail.com"

git commit -m "Updated docs"
git push -u origin doc-branch