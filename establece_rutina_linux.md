
incluye en AGENTS.md y prepara el equipo para la rutina diaria.

## Ejecución diaria recomendada en Linux

La rutina de evaluación del eclipse debe ejecutarse de forma fiable por el sistema operativo, no dependiendo de una sesión interactiva de un asistente. En una máquina Linux, la opción recomendada es:

1. `cron` o `systemd timer` ejecutan la rutina diaria real.
2. La rutina escribe logs persistentes.
3. Claude Code, si se usa, puede quedar en una sesión aparte con `/loop` para supervisar que la rutina sigue funcionando, pero no debe ser el mecanismo principal de ejecución.

La campaña diaria debe lanzarse cada día dentro de la ventana relevante para el eclipse: entre las **19:30 y las 21:00**, hora local de la máquina. Como regla práctica, programar el lanzamiento diario a las **19:30**. La captura debe concentrarse en esa ventana porque la totalidad del eclipse del 12-08-2026 en Asturias será alrededor de las 20:26 CEST.

Motivo: `/loop` en Claude Code es útil para repetir comprobaciones dentro de una sesión abierta, pero no debe tratarse como el planificador principal de una campaña diaria. Si se cierra Claude Code, se reinicia la máquina o no se recupera correctamente la sesión, no debe asumirse que `/loop` seguirá ejecutando la rutina. Por eso la ejecución diaria debe recaer en `cron` o `systemd`, y `/loop` debe usarse solo como vigilancia inteligente.

### Script recomendado para la rutina diaria

Crear un script ejecutable en la raíz del repositorio, por ejemplo:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /ruta/al/repositorio

mkdir -p logs

echo "===== $(date -Is) - inicio rutina diaria eclipse =====" >> logs/daily.log

# Si el proyecto usa entorno virtual, activarlo aquí:
# source .venv/bin/activate

# Captura diaria.
# La rutina debe lanzarse a las 19:30 y trabajar sobre la ventana relevante
# 19:30-21:00 hora local. Si captura_eclipse.py ya gestiona internamente
# esa ventana, no cambiar su lógica aquí.
python3 captura_eclipse.py >> logs/daily.log 2>&1

# Evaluación/ranking acumulado.
# Puede ejecutarse justo después de la captura.
python3 evaluar_eclipse.py >> logs/daily.log 2>&1

echo "===== $(date -Is) - fin rutina diaria eclipse =====" >> logs/daily.log


El nombre sugerido para el archivo es:

run_daily.sh


Después de crearlo, darle permisos de ejecución:

chmod +x run_daily.sh


Antes de programarlo, probarlo manualmente:

./run_daily.sh
tail -n 100 logs/daily.log


No programar en cron hasta confirmar que esta ejecución manual termina correctamente.

Programación con cron

Editar el crontab del usuario que vaya a ejecutar la rutina:

crontab -e


Ejemplo recomendado: ejecutar cada día a las 19:30, hora local de la máquina:

30 19 * * * /ruta/al/repositorio/run_daily.sh >> /ruta/al/repositorio/logs/cron.log 2>&1


Si se quiere fijar explícitamente la zona horaria, por ejemplo para una máquina configurada correctamente en horario peninsular español, se puede añadir al principio del crontab:

TZ=Europe/Madrid


Ejemplo completo:

TZ=Europe/Madrid
30 19 * * * /ruta/al/repositorio/run_daily.sh >> /ruta/al/repositorio/logs/cron.log 2>&1


Notas importantes:

Usar siempre rutas absolutas.
No asumir que cron hereda el mismo entorno que una terminal interactiva.
Si se usa .venv, activarlo dentro de run_daily.sh.
La ejecución diaria debe lanzarse a las 19:30 para cubrir la ventana 19:30-21:00.
Revisar periódicamente logs/daily.log y logs/cron.log.
capturas/, reportes/, animaciones/, grabaciones/ y otros datos generados siguen sin añadirse al repositorio salvo petición explícita del usuario.
Si falla una cámara un día, no eliminarla automáticamente de cameras.py.
Variante con protección de duración máxima

Si se quiere evitar que la fase de captura quede colgada y se extienda más allá de la ventana prevista, se puede envolver solo la captura con timeout.

Ejemplo alternativo dentro de run_daily.sh:

#!/usr/bin/env bash
set -euo pipefail

cd /ruta/al/repositorio

mkdir -p logs

echo "===== $(date -Is) - inicio rutina diaria eclipse =====" >> logs/daily.log

# Si el proyecto usa entorno virtual, activarlo aquí:
# source .venv/bin/activate

# Captura diaria con límite máximo aproximado de 90 minutos.
# Lanzada a las 19:30, esto evita que la captura siga mucho más allá de las 21:00.
timeout 90m python3 captura_eclipse.py >> logs/daily.log 2>&1 || {
    code=$?
    if [ "$code" -eq 124 ]; then
        echo "===== $(date -Is) - captura_eclipse.py detenida por timeout de 90m =====" >> logs/daily.log
    else
        echo "===== $(date -Is) - captura_eclipse.py falló con código $code =====" >> logs/daily.log
        exit "$code"
    fi
}

# Evaluación/ranking acumulado.
python3 evaluar_eclipse.py >> logs/daily.log 2>&1

echo "===== $(date -Is) - fin rutina diaria eclipse =====" >> logs/daily.log


Usar esta variante solo si interesa cortar automáticamente capturas bloqueadas. Si captura_eclipse.py ya controla internamente horarios, reintentos y finalización, preferir la versión simple.

Supervisión opcional con Claude Code y /loop

Claude Code puede usarse como supervisor adicional, pero no como planificador principal.

Arrancar Claude desde la raíz del repo, preferiblemente dentro de tmux:

cd /ruta/al/repositorio
tmux new -s eclipse-claude
claude


Para salir de tmux sin cerrar Claude:

Ctrl+B, luego D


Para volver a la sesión:

tmux attach -t eclipse-claude


Dentro de Claude Code, usar un /loop de supervisión conservador:

/loop 12h Revisa que cron haya ejecutado correctamente la rutina diaria del proyecto eclipse. Lee README.md, AGENTS.md, memoria/MEMORY.md y memoria/proyecto-eclipse-2026.md. Comprueba logs/daily.log, logs/cron.log si existe, la fecha de la última ejecución, errores recientes, el timestamp de las últimas capturas en capturas/ y git status. Verifica especialmente que la rutina se haya lanzado cada día alrededor de las 19:30 y que la campaña cubra la ventana 19:30-21:00 hora local. No ejecutes la rutina salvo que sea necesario para diagnosticar. No cambies archivos, no hagas commit y no hagas push salvo instrucción explícita del usuario. Si detectas un fallo, deja un diagnóstico claro, causa probable y pasos recomendados para corregirlo.


Esta variante es la recomendada por defecto: Claude vigila, pero no modifica nada automáticamente.

Si el usuario quiere permitir que Claude corrija problemas menores de documentación, scripts o configuración, usar esta variante más permisiva:

/loop 12h Revisa que cron haya ejecutado correctamente la rutina diaria del proyecto eclipse. Lee README.md, AGENTS.md, memoria/MEMORY.md y memoria/proyecto-eclipse-2026.md. Comprueba logs/daily.log, logs/cron.log si existe, últimas capturas, errores recientes y git status. Verifica especialmente que la rutina se haya lanzado cada día alrededor de las 19:30 y que la campaña cubra la ventana 19:30-21:00 hora local. No borres datos generados ni cambies el formato de capturas/. Si detectas un fallo corregible en código, documentación o scripts auxiliares, aplica el cambio mínimo, prueba lo que sea razonable, revisa git status, haz un commit descriptivo y haz push. Si no hay cambios reales, no hagas commit vacío.


Preferir siempre la variante conservadora salvo que el usuario haya pedido explícitamente que Claude actúe de forma autónoma.

Qué debe comprobar un asistente durante la supervisión

En cada revisión, el asistente debe comprobar como mínimo:

Que logs/daily.log existe y tiene una ejecución reciente.
Que la última ejecución diaria se lanzó alrededor de las 19:30.
Que la campaña cubre la ventana 19:30-21:00 hora local.
Que logs/cron.log, si existe, no contiene errores recientes de shell, Python, rutas o permisos.
Que se han creado capturas en la fecha esperada bajo el formato:
capturas/AAAA-MM-DD/<slug-cámara>/HHMMSS.jpg

Que evaluar_eclipse.py ha terminado sin romper el histórico.
Que no se han añadido accidentalmente datos pesados al repo.
Que git status no muestra cambios inesperados.
Que las cámaras fallidas no se han eliminado de cameras.py solo por fallar un día.
Que el formato de capturas/ y los slugs se mantienen intactos.
Que cualquier cambio propuesto respeta las decisiones documentadas en este archivo.
Regla de responsabilidad

La responsabilidad de ejecutar la campaña diaria es de cron o systemd.

La responsabilidad de Claude Code con /loop es solamente:

vigilar,
diagnosticar,
resumir incidencias,
sugerir correcciones,
y, si el usuario lo permite explícitamente, aplicar cambios mínimos y versionarlos.

No convertir /loop en el único mecanismo de ejecución diaria de la campaña.

Mandato para futuros agentes

Si el usuario pregunta cómo dejar la campaña funcionando en una máquina Linux, recomendar siempre cron o systemd timer para la ejecución real y Claude Code /loop solo para supervisión.

No recomendar /loop como único mecanismo de automatización diaria persistente.

Para esta campaña concreta, la ejecución diaria debe programarse para comenzar a las 19:30 y cubrir la ventana 19:30-21:00 hora local.


La línea clave de `cron` queda así:

```cron
30 19 * * * /ruta/al/repositorio/run_daily.sh >> /ruta/al/repositorio/logs/cron.log 2>&1
```
