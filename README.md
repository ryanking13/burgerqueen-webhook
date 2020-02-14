# Burgerqueen webhook

## DISCLAIMER (2020/02/14): Not used anymore

Azure function app webhook for [Burgerqueen](https://github.com/ryanking13/burgerqueen).

### How to run

```sh
virtualenv .env -p=python3.6
call .env/scripts/activate
pip install -r requirements.txt
func host start
```

### Deploy

```sh
# import local.settings.json
func azure functionapp fetch-app-settings burgerqueen-api 
func azure functionapp publish burgerqueen-api
```
