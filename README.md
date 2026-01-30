# openclaw-py
A Python autoexecutable autosetuppable wrapper version of OpenClaw (formely Clawdbot/Moltbot)

# Moltbot Python Wrapper - FULLY AUTOCONFIGURABLE

Wrapper completamente automático que instala **TODO** lo necesario y ejecuta Moltbot.

## 🚀 Uso (un solo clic)

### Primera vez - Setup completo:
```
Doble clic en: SETUP_AND_RUN.bat
```
Esto automáticamente:
1. ✅ Instala Python (si no existe, vía winget)
2. ✅ Instala Node.js 22+ (portable si winget falla)
3. ✅ Instala pnpm
4. ✅ Instala todas las dependencias
5. ✅ Compila el proyecto
6. ✅ Ejecuta el wizard de configuración

### Uso normal:
```
Doble clic en: run_moltbot.bat
```
Menú interactivo con todas las opciones.

## 📁 Archivos

| Archivo | Descripción |
|---------|-------------|
| `SETUP_AND_RUN.bat` | **⭐ USAR ESTE** - One-click setup + onboard |
| `run_moltbot.bat` | Menú interactivo completo |
| `moltbot_wrapper.py` | Script Python principal |

## 🔧 ¿Qué instala automáticamente?

1. **Python 3.12** - vía Windows Package Manager (winget)
2. **Node.js 22+** - vía winget o versión portable
3. **pnpm** - vía npm o corepack
4. **Dependencias del proyecto** - vía pnpm install
5. **Build** - compila TypeScript

## 📋 Menú de opciones

```
[1] Onboard          - Wizard de configuración inicial
[2] Gateway          - Servidor principal (WhatsApp/Telegram/etc)
[3] TUI              - Interfaz de terminal
[4] Doctor           - Diagnósticos
[5] Dev Mode         - Modo desarrollo
[6] Custom Command   - Comando personalizado

[R] Reinstall Deps   - Reinstalar dependencias
[B] Rebuild          - Recompilar proyecto
[Q] Quit
```

## ⚙️ Configuración post-setup

Después del onboard, edita `~/.clawdbot/moltbot.json`:

```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-5"
  },
  "channels": {
    "telegram": {
      "botToken": "123456:ABC..."
    }
  }
}
```

## 🔌 Canales soportados

- WhatsApp (Baileys web)
- Telegram (grammY)
- Discord
- Slack
- Signal
- iMessage (macOS)
- Microsoft Teams
- Matrix
- Google Chat
- WebChat

## 🛠️ Solución de problemas

### winget no disponible
El script usa instalación portable de Node.js como fallback.

### Errores de Unicode
Los scripts ya configuran `chcp 65001` automáticamente.

### Dependencias corruptas
Opción `[R]` en el menú para reinstalar.

### Node.js version incorrecta
El wrapper instala automáticamente la versión correcta.

## 📚 Documentación

- [Docs oficiales](https://docs.molt.bot)
- [Getting Started](https://docs.molt.bot/start/getting-started)
- [Telegram](https://docs.molt.bot/channels/telegram)
- [WhatsApp](https://docs.molt.bot/channels/whatsapp)

---
**Wrapper autoconfigurable para Windows** - Solo ejecuta `SETUP_AND_RUN.bat` y listo.
