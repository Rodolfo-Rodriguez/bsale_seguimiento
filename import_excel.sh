source venv/bin/activate

cd data
rm data-dev.sqlite
python create_db.py
python import_excel.py
cd ..
