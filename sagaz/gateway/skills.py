"""One-skill routing by deterministic keyword score."""
from dataclasses import dataclass
import re
import unicodedata


def norm(value: str):
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in value if not unicodedata.combining(char))


TRIGGERS = {
    "rataria": ("youtube", "video", "engenharia reversa", "analisar edicao", "tiktok"),
    "merovingian": ("copy", "cta", "vender", "oferta", "conversao"),
    "keymaker": ("thumbnail", "titulo", "thumb", "capa"),
    "niobe": ("nicho hot", "adulto", "conteudo adulto"),
    "forge": ("prompt", "especificacao", "sistema", "agent"),
}


@dataclass(frozen=True)
class Selection:
    name: str | None
    score: int
    reason: str


def select_skill(request: str) -> Selection:
    if not isinstance(request, str) or len(request) > 20000:
        raise ValueError("Invalid request")
    text = norm(request)
    padded = " " + re.sub(r"[^a-z0-9]+", " ", text) + " "
    scores = {}
    for name, words in TRIGGERS.items():
        score = 0
        for word in words:
            key = " " + re.sub(r"[^a-z0-9]+", " ", norm(word)).strip() + " "
            if key in padded:
                score += 1
        scores[name] = score
    rank = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    if not rank or rank[0][1] == 0:
        return Selection(None, 0, "No matching skill trigger")
    return Selection(rank[0][0], rank[0][1], "Highest matching trigger score")
