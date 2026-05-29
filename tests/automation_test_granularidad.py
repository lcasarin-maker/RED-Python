"""
TEST: test_granularidad.py
Parte de la suite de validacion de Coder Cerberus V0.1.
"""
import os
import sys

def test_file_lengths():
    # Protocol docs (SPEC, PROTOCOL_*, etc.) are legitimately large — limit 500 lines
    # Source scripts limit remains 400 lines (warning only, not fatal)
    MD_LIMIT = 500
    # Documents that grow unboundedly by design (audit trails, planning archives)
    EXCLUDE_DOCS = {"MATRIZ_AUTOMATIZACION_COMPLETA.md", "PLAN_REMEDIACION.md", "HISTORIAL.md", "PLAN.md"}
    print(f"--- INICIANDO TEST DE GRANULARIDAD (LÍMITE .md={MD_LIMIT} LÍNEAS) ---")
    fail_count = 0
    total_files = 0

    # Directorios operativos a auditar
    targets = ['.', 'N1_MODULOS', 'N2_MODULOS', 'N4_MODULOS', 'N5_MODULOS', 'docs', 'scripts']

    for target in targets:
        if not os.path.exists(target):
            continue

        for file in os.listdir(target):
            if file.endswith('.md') or file.endswith('.py'):
                path = os.path.join(target, file)
                if os.path.isdir(path): continue

                total_files += 1
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        count = len(lines)

                        if path.endswith('.md') and count > MD_LIMIT and file not in EXCLUDE_DOCS:
                            print(f"FALLO: Documento {path} tiene {count} lineas (Limite: {MD_LIMIT}).")
                            fail_count += 1
                        elif (path.endswith('.py') or path.endswith('.js')) and count > 400:
                            print(f"ADVERTENCIA: Codigo {path} tiene {count} lineas. Evaluar SRP.")
                except Exception as e:
                    print(f"ERROR leyendo {path}: {e}")

    print(f"\nRESUMEN: {fail_count} fallos detectados en {total_files} archivos.")
    print("---------------------------------------------------------")

    assert fail_count == 0, f"Granularidad: {fail_count} documento(s) superan {MD_LIMIT} lineas."
    print("INTEGRIDAD DE GRANULARIDAD VERIFICADA.")

if __name__ == "__main__":
    test_file_lengths()
