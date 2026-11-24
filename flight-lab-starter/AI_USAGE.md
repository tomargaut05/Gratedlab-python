# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Tool and version (e.g. ChatGPT GPT-5, Claude, GitHub Copilot): Gemini

## Conversation links

- Link 1:https://gemini.google.com/app/e9ce99b065cf7640?dest=create

## What I used them for

- e.g. explaining argparse, debugging the date validation, generating test data

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| `validator.py` | The Date Trap, Misleading Python Functions Related to ASCII, The Case of Invalid Prices | modified and explained |
| `query.py` | `run_query`, Strict validation of invalid queries, the filter bug encountered, and sorting stability | explained and modified  |
| `flight_parser.py`and `csv_loader.py`  | Cleaning Up Logging Handlers, Handling Runtime Errors Without Tracebacks | Generated and explained |


## Key prompts

1."Hi, Gemini. I need your help with Python. I need to ensure the strict format $YYYY-MM-DD\ HH:MM$, and I see that using `strptime` isn't enough because it accepts values without the leading zero."
2."aussi les méthodes str.isalnum ou str.isupper de Python acceptent les caractères Unicode accentués comme Ā ou é. Pour les identifiants de vol et les codes d'aéroport je dois pas utiliser autre chose ?"

## What I changed or verified myself
1."(len == 16) and (dt.strftime(...) verified myself"
2." use of regex ASCII strict (^[A-Za-z0-9]{2,8}$ and ^[A-Z]{3}$) is essential. verified myself"
3."math.isnan() and math.isinf() tested by myself"
4."sorted(..., reverse=True) for the stability tested myself"
