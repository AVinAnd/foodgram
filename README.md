# praktikum_new_diplom
```
python manage.py loadingredients /d/Dev/foodgram/foodgram-project-react/data/ingredients.csv
```
sudo docker exec infra_backend_1 python manage.py migrate
sudo docker exec infra_backend_1 python manage.py collectstatic --no-input
sudo docker exec infra_backend_1 python manage.py loadingredients ./data/ingredients.csv