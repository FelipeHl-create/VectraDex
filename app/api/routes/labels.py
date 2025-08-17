from io import BytesIO
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from PIL import Image
import barcode
from barcode.writer import ImageWriter
from ...models.product import Product
from ..deps import get_db

router = APIRouter()


def _generate_barcode_image(code: str) -> Image.Image:
    try:
        code128 = barcode.get("code128", code, writer=ImageWriter())
        buf = BytesIO()
        code128.write(buf, options={"module_height": 15.0, "text_distance": 1.0})
        buf.seek(0)
        return Image.open(buf).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Erro ao gerar código de barras: {exc}")


@router.get("/{product_id}/png")

def product_label_png(
    product_id: int,
    db: Session = Depends(get_db),
    decrement_qty: int = Query(default=0, ge=0, description="Quantidade a decrementar após impressão"),
):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    img = _generate_barcode_image(product.code)
    # Compor etiqueta simples (nome + código)
    canvas = Image.new("RGB", (max(300, img.width + 20), img.height + 60), "white")
    canvas.paste(img, (10, 40))
    # Deixar simples para MVP; texto básico usando PIL default (sem fonte TTF)
    from PIL import ImageDraw

    draw = ImageDraw.Draw(canvas)
    draw.text((10, 5), f"{product.name}", fill="black")
    draw.text((10, img.height + 40), f"{product.code}", fill="black")

    if decrement_qty > 0:
        if product.quantity < decrement_qty:
            raise HTTPException(status_code=400, detail="Quantidade insuficiente para decrementar")
        product.quantity -= decrement_qty
        db.add(product)
        db.commit()

    out = BytesIO()
    canvas.save(out, format="PNG")
    out.seek(0)
    return StreamingResponse(out, media_type="image/png")


@router.post("/batch/png")

def batch_labels_png(
    ids: List[int],
    db: Session = Depends(get_db),
    decrement: bool = Query(default=False, description="Se true, decrementa 1 por produto impresso"),
    qty: int = Query(default=1, ge=1, description="Quantidade de etiquetas por produto; usada para decremento"),
):
    products = db.query(Product).filter(Product.id.in_(ids)).all()
    if not products:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado")
    # Gera um zip em memória de PNGs
    import zipfile

    mem = BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in products:
            img = _generate_barcode_image(p.code)
            canvas = Image.new("RGB", (max(300, img.width + 20), img.height + 60), "white")
            canvas.paste(img, (10, 40))
            from PIL import ImageDraw

            draw = ImageDraw.Draw(canvas)
            draw.text((10, 5), f"{p.name}", fill="black")
            draw.text((10, img.height + 40), f"{p.code}", fill="black")

            buf = BytesIO()
            canvas.save(buf, format="PNG")
            buf.seek(0)
            zf.writestr(f"label_{p.code}.png", buf.read())
            if decrement:
                if p.quantity < qty:
                    raise HTTPException(status_code=400, detail=f"Quantidade insuficiente para {p.code}")
                p.quantity -= qty
                db.add(p)
    if decrement:
        db.commit()
    mem.seek(0)
    return StreamingResponse(mem, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=labels.zip"})
