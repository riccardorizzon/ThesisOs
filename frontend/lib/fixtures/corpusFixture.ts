import type { CorpusSource } from "@/lib/corpusClient";

export const FIXTURE_APPROVED_CORPUS_SOURCE: CorpusSource = {
  id: "benjamin-opera-arte",
  title: "L'opera d'arte nell'epoca della riproducibilità tecnica",
  subtitle: "Walter Benjamin",
  meta: "1936 · Libro",
  status: "approvata",
  relatedConceptIds: ["aura", "riproducibilita"],
  body:
    "L'opera d'arte nell'epoca della sua riproducibilità tecnica perde la sua presenza unica nel tempo e nello spazio.",
};

export const FIXTURE_EXCLUDED_CORPUS_SOURCE: CorpusSource = {
  id: "barthes-mythologies",
  title: "Mythologies",
  subtitle: "Roland Barthes",
  meta: "1957 · Saggio",
  status: "esclusa",
  relatedConceptIds: ["mito", "stigmata"],
  body: "Il mito è un sistema di comunicazione, un messaggio.",
  exclusionReason: "Esclusa da CORPUS-02/03.",
};
