# install

```
pip install -r requirements.txt
```

# run

```
uvicorn main:app --reload
```

# clean

```
fd "__pycache__" -I | xargs rm -rf
fd users.db -I | xargs rm
```
