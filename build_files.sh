#!/bin/bash
echo "A instalar os requisitos..."
python -m pip install -r requirements.txt

echo "A compilar os ficheiros estáticos..."
python manage.py collectstatic --noinput --clear