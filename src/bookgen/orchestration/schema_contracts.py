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
Quality floor: target at least 15 pages, include at least 5 chapters, and place cover,
toc, image, graph, table, formula, hebrew_english_section, and citations.
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

MANUSCRIPT_CONTRACT = """
Return Markdown only, not JSON. The manuscript must be submission-grade:
- Hebrew-primary prose with English only for technical terms.
- At least 5 chapter headings using "## Chapter Title" and section headings using "###".
- At least 1,600 words and no placeholder/TODO/future-tense filler.
- Include citation markers [@crewai_docs], [@langchain_docs], and [@latex_project].
- Discuss the image, graph, table, formula, and Hebrew-English BiDi section concretely.
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
    {"asset_id": "agent_pipeline_graph", "kind": "graph", "target_path": "generated/assets/graphs/agent_pipeline_graph.png", "caption": "string"},
    {"asset_id": "agent_roles_table", "kind": "table", "target_path": "generated/latex/agent_roles_table.tex", "caption": "string"},
    {"asset_id": "quality_score_formula", "kind": "formula", "target_path": "generated/latex/quality_score_formula.tex", "caption": "string"}
  ],
  "bibliography_file": "data/references/references.bib",
  "bidi_required": true
}
Do not use template, asset_references, output_pdf_path, or bidi_settings.
Quality floor: engine must be lualatex and assets must include image, graph, table,
and formula.
""".strip()
