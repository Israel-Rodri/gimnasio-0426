#!/bin/bash
set -euo pipefail  # Modo seguro: falla en errores, variables no definidas y pipes

# 🔧 CONFIGURACIÓN
OUTPUT_FILE="estructura_root.md"
#ARCHIVOS=("models/entrenadores.py" "models/evaluaciones.py" "models/metodos_pago.py" "models/miembros_entrenadores_link.py" "models/miembros.py" "models/pagos_planes_link.py" "models/pagos.py" "models/planes.py" "models/rutinas_planes_link.py" "models/rutinas.py" "models/sedes.py")
#ARCHIVOS=("routers/entrenadores.py" "routers/evaluaciones.py" "routers/metodos_pago.py" "routers/miembros.py" "routers/pagos.py" "routers/planes.py" "routers/rutinas.py" "routers/sedes.py")
#ARCHIVOS=("schemas/entrenadores.py" "schemas/evaluaciones.py" "schemas/metodos_pago.py" "schemas/miembros.py" "schemas/pagos.py" "schemas/planes.py" "schemas/rutinas.py" "schemas/sedes.py")
ARCHIVOS=("database.py" "main.py")
TITULOS=("Modelo de Entrenadores" "Modelo de Evaluaciones" "Modelo de Metodos de Pago" "Modelo Miembros Entrenadores Link" "Modelo Miembros" "Modelo Pagos Planes Link" "Modelo Pagos" "Modelo Planes" "Modelo Rutinas Planes Link" "Modelo Rutinas" "Modelo Sedes")

# 🧹 Crear/limpiar archivo de salida
> "$OUTPUT_FILE"

# 📝 ENCABEZADO PERSONALIZADO
cat << HEADER >> "$OUTPUT_FILE"
# 📘 Documentación Técnica de los models del proyecto
> Generado automáticamente mediante script Bash

📅 Fecha: $(date +"%Y-%m-%d %H:%M:%S")
---
HEADER

# 🔄 PROCESAR CADA ARCHIVO
for i in "${!ARCHIVOS[@]}"; do
    archivo="${ARCHIVOS[$i]}"
    titulo="${TITULOS[$i]}"

    if [[ -f "$archivo" ]]; then
        echo "" >> "$OUTPUT_FILE"
        echo "## $titulo" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        cat "$archivo" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "---" >> "$OUTPUT_FILE"
    else
        echo "⚠️  [SKIP] El archivo '$archivo' no existe." >&2
    fi
done

# 📝 PIE DE PÁGINA
cat << FOOTER >> "$OUTPUT_FILE"

🤖 *Documento generado automáticamente. Revisa los contenidos antes de compartir.*
📂 Repositorio: $(basename "$(pwd)")
FOOTER

echo "✅ Documento generado exitosamente: $OUTPUT_FILE"
