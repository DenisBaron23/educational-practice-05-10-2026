# аудит безопасности

## что проверено
Все обращения к базе данных: etl.py, discounts.py, materials.py,
main_window.py, partner_edit_window.py, partner_history_window.py.

## результат
| место | вид запроса | защита |
|---|---|---|
| main_window.load_partners | поиск like | параметры ?, шаблон % собирается в python |
| partner_edit_window.save | insert, update | параметры ? |
| partner_edit_window.load_partner | select | параметр ? |
| partner_history_window | select с join | параметр ? |
| discounts, materials | select | параметры ? |
| etl.py | insert | параметры ? |

## как проверялось
1. `grep -rn "execute(" --include=*.py .` и осмотр каждой строки.
2. `grep -rnE "f\"(SELECT|INSERT|UPDATE)" .` дал 0 совпадений.
3. Ручная проверка: в поиск введено `' OR 1=1 --`, таблица пуста, ошибок нет.

## вывод
Конкатенации строк в sql нет, уязвимостей к sql-инъекциям не выявлено.
