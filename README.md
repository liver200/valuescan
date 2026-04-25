# ValueScan v2 — Deploy en Railway

## Pasos para deployar

1. Crear cuenta en railway.app (gratis, con GitHub)
2. New Project → Deploy from GitHub repo → seleccionar este repo
3. En el proyecto → Variables → agregar:
   - ANTHROPIC_API_KEY = sk-ant-...
   - ALPHAVANTAGE_API_KEY = tu-key
4. Railway deployea automáticamente y te da una URL pública
5. Abrí esa URL y listo — sin instalar nada

## Límites del plan gratuito Railway
- 500 horas/mes (suficiente para uso personal)
- Sleep después de inactividad (despierta solo al entrar)

## Archivos
- server.py        → servidor proxy (llama a Anthropic y Alpha Vantage)
- valuescan_v2.html → dashboard frontend
- Procfile         → instrucción de arranque para Railway
- railway.json     → configuración de deploy
