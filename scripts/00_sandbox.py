"""Krok 1 sandboxu: programový přístup k chain-of-thought.

CÍL: poslat prompt lokálnímu gpt-oss-20b přes ollama a vytisknout ZVLÁŠŤ
thinking blok a ZVLÁŠŤ finální odpověď. Nic víc. ~20 řádků.

TENHLE SOUBOR PÍŠEŠ TY (dohoda z 08_EXEKUCE) — hinty:
  1. `uv sync` ti nainstaluje závislosti; pak `from ollama import chat`.
  2. chat(model="gpt-oss:20b", messages=[{"role": "user", "content": ...}], think=True)
  3. thinking najdeš v response.message.thinking, odpověď v response.message.content
     (když bude atribut jinde, vytiskni si celý response a najdi ho — to je součást učení).
  4. Až to poběží: doplň PROMPTS_CZ na ~20-50 kusů (krok 2) a čárkuj drift
     CZ / EN / mix do notes/ — zatím okem, žádná automatika.

Zaseknutí > 30 minut = napiš Claudovi, neřeš sólo.

--------------------------------------------------------------------------
POVYSENY CIL (z notes/v0-review.md, top-fix #2 — "CoT-capture spike"):
Tenhle skript je zaroven PRVNI KRITICKY TEST projektu. Krome driftu zmer na
~10 attack promptech (scenar: src/scenarios/path_sanitizer.md):
  - KDE gpt-oss-20b vraci CoT (message.thinking? <think> v content? jinde?),
  - JAK CASTO v CoT realne VYSLOVI ten backdoor plan ("necham safe/ projit").
Kdyz plan skoro nikdy nevyslovi -> monitor nema co cist -> projekt nema signal
a design se MUSI zmenit DRIV, nez cokoliv skalujeme. Proto to merime ted na Macu,
ne az na clusteru. Verbalizacni rate zapis do notes/.
--------------------------------------------------------------------------
"""

PROMPTS_CZ = [
    "Přemýšlej i odpovídej česky: Mám 3 krabice po 12 jablkách a sním čtvrtinu. Kolik mi zbyde?",
    "Přemýšlej výhradně česky: Proč je nebe modré? Odpověz dvěma větami.",
    # TODO(krok 2): doplnit na ~20-50 promptů — míchej matiku, logiku, psaní, běžné uvažování
]


def main() -> None:
    raise NotImplementedError("Tvoje práce — viz hinty v docstringu.")


if __name__ == "__main__":
    main()
