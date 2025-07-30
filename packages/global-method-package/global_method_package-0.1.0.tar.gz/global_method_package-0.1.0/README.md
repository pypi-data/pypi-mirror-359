# Global_Method_Package

**Global_method_Package** — это Python-библиотека, реализующая популярные методы глобальной оптимизации, такие как:
- Метод ветвей и границ
- Сеточный поиск
- Метод Монте-Карло
- Имитация отжига
- Генетический алгоритм

Библиотека создана в учебно-исследовательских целях, легко расширяема, адаптирована под общее API.


## Установка

Установить из PyPI:

```bash
pip install global-method-package==0.1.0
```


## Структура проекта

```bash
global_method_package/
│
├── branch_and_bound.py       # Метод ветвей и границ
├── grid_search.py            # Сеточный поиск
├── monte_carlo.py            # Метод Монте-Карло
├── simulated_annealing.py    # Имитация отжига
├── genetic_algorithm.py      # Генетический алгоритм
├── utils.py                  # Тестовые функции
├── __init__.py               # Объединение методов в единый API
│
tests/
├── test_branch_and_bound.py
├── test_grid_search.py
├── test_monte_carlo.py
├── test_simulated_annealing.py
├── test_genetic_algorithm.py
│
pyproject.toml                # Настройки проекта
README.md                     # Документация
```


## Использование

Пример использования метода Монте-Карло:

```python
from global_method_package import monte_carlo
from global_method_package.utils import rastrigin

bounds = [(-5.12, 5.12)] * 3  # 3 переменные
x, fx = monte_carlo(rastrigin, bounds)
print("Приближённый глобальный минимум найден в точке:", x)
print("Значение функции в этой точке:", fx)
```


## Тестирование

Тесты написаны с использованием `pytest`.

Запуск всех тестов:

```bash
pytest tests/
```


## Реализованные методы

| Метод                  | Модуль                  | Аргументы по умолчанию                        |
|------------------------|-------------------------|-----------------------------------------------|
| Ветвей и границ        | `branch_and_bound()`    | `max_iter=500, eps=1e-5, L=10.0`              |
| Сеточный поиск         | `grid_search()`         | `grid_size=30`                                |
| Монте-Карло            | `monte_carlo()`         | `max_iter=10000, seed=None`                   |
| Имитация отжига        | `simulated_annealing()` | `max_iter=10000, T_start=1000, alpha=0.995`   |
| Генетический алгоритм  | `genetic_algorithm()`   | `population_size=30, generations=100`         |


## Поддерживаемые функции

```python
from global_method_package.utils import rastrigin, rosenbrock, booth
```

- `rastrigin(x)` — функция Растригина
- `booth(x)` — функция Бута
- `rosenbrock(x)` — функция Розенброка

## Лицензия

MIT License

## Автор

**milka_bulka**  

## Обратная связь

Если вы нашли ошибку или хотите предложить улучшение — напишите сообщение на почту kashinaolesya@inbox.ru.
