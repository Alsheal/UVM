#!/usr/bin/env bash
# Запуск УВМ: ./run.sh <asm|run|test|demo> [аргументы]
set -euo pipefail

cd "$(dirname "$0")"
export PYTHONPATH=src
PYTHON="${PYTHON:-python3}"

usage() {
  echo "Использование: ./run.sh <команда> [аргументы]"
  echo "  asm  <исходник.asm> <выход.bin> [--test]"
  echo "  run  <файл.bin> <дамп.json> --from <адрес> --to <адрес>"
  echo "  test         запустить тесты"
  echo "  demo         ассемблировать и выполнить examples/vector_ror_1.asm"
}

demo() {
  "$PYTHON" -m uvm.assembler examples/vector_ror_1.asm demo.bin
  "$PYTHON" -m uvm.interpreter demo.bin dump.json --from 0 --to 26
  cat dump.json
}

case "${1:-}" in
  asm)  shift; "$PYTHON" -m uvm.assembler "$@" ;;
  run)  shift; "$PYTHON" -m uvm.interpreter "$@" ;;
  test) "$PYTHON" -m unittest discover -v ;;
  demo) demo ;;
  *)    usage; exit 1 ;;
esac