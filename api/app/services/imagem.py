"""Limpeza de fotos enviadas pelo cidadão.

Remove os metadados (EXIF com GPS e modelo do aparelho, XMP, comentários e perfil de cor)
antes de gravar a foto. A orientação do EXIF é aplicada nos pixels, para a foto não girar.
"""

import io

from PIL import Image, ImageOps, UnidentifiedImageError

FORMATOS = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}


class FotoInvalida(ValueError):
    pass


def limpar(conteudo: bytes, content_type: str) -> bytes:
    formato = FORMATOS[content_type]
    try:
        with Image.open(io.BytesIO(conteudo)) as origem:
            if origem.format != formato:
                raise FotoInvalida("o conteúdo da foto não corresponde ao tipo informado")
            foto = ImageOps.exif_transpose(origem)  # cópia sem a tag de orientação
            if formato == "JPEG" and foto.mode not in ("RGB", "L"):
                foto = foto.convert("RGB")
            saida = io.BytesIO()
            opcoes = {"quality": 90} if formato in ("JPEG", "WEBP") else {}
            foto.save(saida, format=formato, **opcoes)  # sem exif=, icc_profile= ou pnginfo=
            return saida.getvalue()
    except FotoInvalida:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError) as erro:
        raise FotoInvalida("arquivo não é uma imagem válida") from erro
