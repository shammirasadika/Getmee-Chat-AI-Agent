# Ingestion Pipeline Overview

## Purpose
The ingestion pipeline processes client-uploaded documents of various formats, extracts and cleans their content, detects document structure (FAQ/Q&A vs. general), chunks the text for retrieval, generates embeddings, and stores the results in ChromaDB for efficient search and retrieval.

---

## Pipeline Steps

1. **File Upload**
   - Users upload files (PDF, DOCX, TXT, XLSX, CSV, JSON) via the `/api/upload` endpoint.
   - The file is saved temporarily for processing.

2. **Text Extraction**
   - The file is passed to the extraction logic, which detects the file type and uses the appropriate extraction method.
   - Supported formats: PDF, DOCX, TXT, XLSX, CSV, JSON.

3. **Text Cleaning**
   - Lightweight cleaning is applied:
     - Non-printable characters are removed.
     - Multiple spaces are normalized to a single space.
     - Excessive newlines are reduced to a maximum of two.
     - Line breaks are preserved to maintain document structure.

4. **Document Structure Detection**
   - The cleaned text is analyzed to detect if it is FAQ/Q&A style or a general document.
   - Detection uses flexible regex patterns for Q/A markers (Q1:, Q:, Question:, A:, Answer:).
   - At least 3 question and 3 answer markers are required to classify as FAQ/Q&A.

5. **Chunking**
   - **FAQ/Q&A Documents:**
     - Each chunk contains one question and its corresponding answer.
     - Handles multi-line answers and ignores category headers.
     - Failsafe: If parsing fails or no chunks are found, falls back to general chunking.
   - **General Documents:**
     - Text is chunked into segments of ~500 words with 100-word overlap.
     - Paragraph structure is not assumed to be perfect.

6. **Embedding & Storage**
   - Each chunk is embedded (vectorized) using the embedding service.
   - Chunks and their embeddings are stored in ChromaDB with metadata.

7. **Completion**
   - The API returns a response indicating success or failure.
   - Logs provide timing and status for each step.

---

## Special Key Points

- **Multi-format Support:** Handles PDF, DOCX, TXT, XLSX, CSV, and JSON files.
- **Robust FAQ/Q&A Detection:** Uses flexible, real-world patterns and thresholds to accurately detect FAQ documents.
- **Preserves Structure:** Cleaning logic maintains line breaks and document structure, which is critical for correct Q&A detection and chunking.
- **Failsafe Mechanism:** If FAQ detection or chunking fails, the system automatically falls back to general chunking and logs a warning.
- **Debug Logging:** Logs document type detection, chunking mode, number of chunks, and previews of the first few chunks for transparency and troubleshooting.
- **No Change to API or Storage:** The improvements are internal to extraction, cleaning, and chunking logic—API, embedding, and storage flows remain unchanged.

---

## Example Log Output

```
INFO: Detected FAQ/Q&A style document
INFO: Chunking mode: Q&A
INFO: Number of chunks: 52
INFO: Chunk 1 preview: Question: ...\nAnswer: ...
INFO: Chunk 2 preview: ...
```

---

## Success Criteria
- FAQ datasets are chunked into one Q&A pair per chunk (40–60 chunks typical).
- General documents are chunked by size/overlap.
- Retrieval returns the correct Q&A chunk for relevant queries.

---

For further details, see the code in `ingestion_pipeline/services/text_extractor.py`.
