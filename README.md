# python-librus
API do e-dziennika librus synergia.
# Spis treści
1. [Instalacja](#instalacja)
2. [Przykładowe użycie](#przykładowe-użycie)
3. [Spis funkcji](#spis-funkcji)
# Instalacja
...
# Przykładowe użycie
```python
from librus import Librus()

librus = Librus()
print(librus.get_lucky_number())
# 14
```
# Spis funkcji
## get_lucky_number()
Zwraca szczęśiwy numerek w formacie `int`
## get_grades()
Zwraca wszystkie oceny w formacie
```
grades = {
  "Biologia": [
    {
      "Ocena": "5",
      "Waga": "3",
      "Kategoria": "Kartkówka",
      "Nauczyciel": "Janusz Kowalski",
      "Komentarz": "kartkówka z działu o płazach",
      "Do średniej": "Tak"
    }
    ...
  ]
  ...
}
```
## get_teachers()
Zwraca liste nauczycieli w formacie(!format zmieni się w przyszłej aktualizacji!):
```
112233: {
  "FirstName": "Janusz",
  "LastName": "Kowalski",
}
```
