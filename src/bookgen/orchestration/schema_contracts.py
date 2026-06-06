"""Explicit JSON contracts embedded in real CrewAI task prompts."""

BOOK_PLAN_CONTRACT = """
Return ONLY one JSON object with these exact snake_case fields:
{
  "title": "string",
  "subtitle": "string or null",
  "audience": "single string",
  "chapters": [
    {
      "title": "string",
      "summary": "string",
      "sections": [{"title": "string", "purpose": "string"}]
    }
  ],
  "required_feature_placement": {"cover": "string", "toc": "string"},
  "acceptance_checklist": ["string"],
  "estimated_pages": 16
}
Do not use chapterOutline, chapterTitle, requiredFeaturePlacement, estimatedPageCount,
or nested audience objects.
""".strip()

RESEARCH_PACK_CONTRACT = """
Return ONLY one JSON object with these exact snake_case fields:
{
  "topic": "string",
  "key_concepts": ["string"],
  "terminology": {"term": "definition"},
  "source_candidates": [
    {"source_id": "string", "title": "string", "url": "string or null", "notes": "string"}
  ],
  "chapter_notes": {"chapter title": "research note"},
  "unsupported_claim_warnings": ["string"]
}
Do not return a copied book plan, per-chapter nested research objects, or source strings without
source_id/title fields.
""".strip()

REVIEW_REPORT_CONTRACT = """
Return ONLY one JSON object with these exact snake_case fields:
{
  "approved": true,
  "checklist": {"cover": true, "toc": true},
  "notes": ["string"],
  "required_fixes": ["string"]
}
Do not use approval_status, checklist_results, object-valued notes, or object-valued
required_fixes.
""".strip()

LATEX_SPEC_CONTRACT = """
Return ONLY one JSON object with these exact snake_case fields:
{
  "title": "string",
  "engine": "lualatex",
  "main_template": "main.tex.j2",
  "output_pdf": "generated/pdf/final.pdf",
  "chapter_files": ["chapters/chapter_01.tex"],
  "assets": [
    {
      "asset_id": "course_concept_image",
      "kind": "image",
      "target_path": "generated/assets/images/course_concept_image.png",
      "caption": "string"
    },
    {
      "asset_id": "agent_pipeline_graph",
      "kind": "graph",
      "target_path": "generated/assets/graphs/agent_pipeline_graph.png",
      "caption": "string"
    }
  ],
  "bibliography_file": "data/references/references.bib",
  "bidi_required": true
}
Do not use template, asset_references, output_pdf_path, or bidi_settings.
""".strip()
