# Bimsa_Cli.py
import argparse
import sys
from pathlib import Path

from BIMSA_pipeline import process_bimsa


def main() -> int:
    p = argparse.ArgumentParser(description="BIMSA ETL: XML(string) -> Excel(.xlsx)")

    # Requeridos
    p.add_argument("--tipo", required=True, help="Tipo de reporte (ej: MENSAJERO)")
    p.add_argument("--out-xlsx", required=True, help="Ruta destino del Excel .xlsx")

    # Runs / artifacts
    p.add_argument("--output-root", default="bimsa_runs", help="Carpeta donde se guardan artefactos (json/runs)")
    p.add_argument("--save-json", action="store_true", help="Guardar JSON en disco (silencioso)")
    p.add_argument("--debug-save-excel", action="store_true", help="Guardar copia del Excel en output-root (QA)")

    # Entrada XML
    p.add_argument("--xml", default=None, help="XML directo como argumento (no recomendado; usa STDIN).")

    args = p.parse_args()

    out_path = Path(args.out_xlsx)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 1) Obtener XML
    if args.xml is not None:
        xml_string = args.xml
    else:
        raw = sys.stdin.buffer.read()

        # Decodificación robusta
        xml_string = None
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                xml_string = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if xml_string is None:
            xml_string = raw.decode("latin-1", errors="replace")

    if not xml_string or not xml_string.strip():
        print("[BIMSA_ETL_ERROR] No se recibió XML. Pásalo por STDIN o con --xml.", file=sys.stderr)
        return 3

    try:

        nombre_excel, excel_bytes = process_bimsa(
            xml_string,
            args.tipo,
            output_root=args.output_root,
            guardar_json=args.save_json,
            guardar_excel_en_disco=args.debug_save_excel,
        )

        # 3) Escribir Excel final
        out_path.write_bytes(excel_bytes)

        # útil para integraciones
        print(nombre_excel)
        return 0

    except Exception as e:
        print(f"[BIMSA_ETL_ERROR] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())