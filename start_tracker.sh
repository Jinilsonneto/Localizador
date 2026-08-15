#!/data/data/com.termux/files/usr/bin/bash
# Coloque este arquivo em ~/.termux/boot/start_tracker.sh
# O Termux:Boot executa tudo que estiver nessa pasta automaticamente
# sempre que o celular liga/reinicia.

# AJUSTE ESTE CAMINHO para a pasta onde estão tracker.py, config.py, etc.
PROJETO_DIR="$HOME/localizador"

termux-wake-lock

cd "$PROJETO_DIR" || exit 1

# Loop supervisor: se o tracker.py cair por qualquer motivo, reinicia sozinho
# depois de 5 segundos, em vez de ficar parado até você abrir o Termux de novo.
while true; do
    python3 tracker.py start
    echo "$(date '+%Y-%m-%d %H:%M:%S') - tracker.py encerrou, reiniciando em 5s..." >> "$HOME/.termux/boot/tracker_supervisor.log"
    sleep 5
done
