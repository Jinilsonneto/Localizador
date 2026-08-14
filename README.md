# Localizador para Termux - Rastreador de Localização com Detecção de Permanência

## 📍 Funcionalidades

- **Rastreamento GPS contínuo** com intervalo configurável
- **Detecção automática de permanências**: Quando o celular fica mais de 10 minutos no mesmo lugar, salva automaticamente um arquivo JSON com os dados da localização
- **Economia de bateria**: Intervalos configuráveis entre coletas (padrão: 60s)
- **Exportação simplificada**: Arquivos individuais para cada permanência, fáceis de compartilhar
- **Múltiplos formatos**: CSV, GPX e JSON
- **Comando share**: Envia automaticamente o último arquivo de permanência

## 🚀 Instalação Rápida

```bash
# Instale o Termux:API no Android primeiro!
pkg install termux-api python
termux-grant all
```

## 📖 Uso Simplificado

### Iniciar rastreamento
```bash
python tracker.py start
# Pressione CTRL+C para parar quando quiser
```

### Parar rastreamento
```bash
python tracker.py stop
```

### Ver última localização
```bash
python tracker.py status
```

### 📤 Listar e enviar arquivos (MAIS FÁCIL!)
```bash
# Lista todos os arquivos disponíveis
python tracker.py files

# Envia automaticamente o último arquivo de permanência
python tracker.py share
```

### Exportar dados completos
```bash
# Todos os pontos em CSV (para Excel/Planilhas)
python tracker.py export csv

# Percurso em GPX (para Google Earth, OsmAnd, etc.)
python tracker.py export gpx
```

### Configurar
```bash
python tracker.py config
```

## 📁 Arquivos de Permanência (Automático!)

Quando você permanece **mais de 10 minutos** no mesmo local, o sistema cria automaticamente um arquivo JSON na pasta `exports/` com:

- ✅ Coordenadas GPS precisas
- ✅ Links diretos para **Google Maps** e **Waze**
- ✅ Horário de chegada e saída
- ✅ Duração total da permanência

### Exemplo de arquivo gerado:
```json
{
  "tipo": "permanencia",
  "localizacao": {
    "latitude": -23.55052,
    "longitude": -46.633308,
    "google_maps": "https://www.google.com/maps?q=-23.55052,-46.633308",
    "waze": "https://waze.com/ul?ll=-23.55052,-46.633308&navigate=yes"
  },
  "chegada": "2025-01-15 10:00:00",
  "saida": "2025-01-15 10:15:00",
  "duracao_minutos": 15.0
}
```

## 🚀 Como Enviar os Arquivos (Muito Fácil!)

### Opção 1: Comando share (Recomendado)
```bash
python tracker.py share
```
Este comando já abre a janela de compartilhamento do Android com o último arquivo de permanência!

### Opção 2: Manual com termux-share
```bash
# Lista os arquivos
python tracker.py files

# Envia o que quiser
termux-share exports/permanencia_20250115_100000.json
```

### Opção 3: Copiar manualmente
Os arquivos estão em `/workspace/exports/` - copie como quiser!

## ⚙️ Configurações Padrão

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| interval_seconds | 60 | Tempo entre coletas GPS |
| stay_duration_minutes | 10 | Tempo mínimo para registrar permanência |
| stay_radius_meters | 30 | Raio para considerar permanência |
| jitter_radius_meters | 10 | Raio para ignorar oscilações do GPS |

Para alterar: `python tracker.py config`

## 💡 Dicas de Uso

1. **Economizar bateria**: Aumente o intervalo para 300s (5 min) ou mais
2. **Compartilhar locais importantes**: Os arquivos de permanência são perfeitos!
3. **Ver rotas**: Use o comando `export gpx` e abra no Google Earth
4. **Análise de dados**: Use `export csv` e abra no Excel/LibreOffice

## 🆘 Comandos Rápidos

```bash
python tracker.py          # Mostra ajuda
python tracker.py start    # Inicia
python tracker.py stop     # Para
python tracker.py status   # Última posição
python tracker.py files    # Lista arquivos
python tracker.py share    # Envia último arquivo ⭐
python tracker.py stats    # Estatísticas
```