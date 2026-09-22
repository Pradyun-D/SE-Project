import os
import logging
from pathlib import Path

from pypdf import PdfReader


logger = logging.getLogger(__name__)

DOC_NAME_MAP = {
    "2-API_Specifications_v2.0.0.pdf": "ReBIT API Specifications v2.0.0",
    "3Clarification_on_Mandatory_and_Optional_fields_V1.0.pdf": "ReBIT Clarification on Mandatory/Optional Fields",
    "4-Guidelines_Use_of_PAN_DOB_Account_Discovery.pdf": "ReBIT Guidelines - PAN/DOB Account Discovery",
    "5-Guidelines_Adoption_Deposit_RD_TD_FI_Type_Schema_Version_2.0.0.pdf": "ReBIT Deposit/RD/TD Schema Guidelines v2.0.0",
    "Design-Guidelines-1.pdf": "Sahamati Customer Consent Design Guidelines",
    "Framework-for-recognising-SROs-for-the-AA-Ecosystem-1.pdf": "Sahamati SRO Recognition Framework",
    "Master Direction - NBFC-AA Directions, 2016.pdf": "RBI Master Direction - NBFC-AA Directions 2016",
    "MeitY-Consent-Tech-Framework v1.1.pdf": "MeitY Electronic Consent Framework v1.1",
    "Reserve Bank of India (NBFC – Account Aggregator) Directions, 2025.pdf": "RBI NBFC-AA Directions 2025",
}


def resolve_doc_title(filename: str) -> str:
    name = os.path.basename(filename)
    return DOC_NAME_MAP.get(name, Path(name).stem.replace("_", " ").strip())


def parse_pdf_directory(folder_path: str) -> tuple[list[dict], int]:
    folder = Path(folder_path)
    if not folder.is_dir():
        raise FileNotFoundError(f"Directory '{folder_path}' does not exist")

    chunks: list[dict] = []
    document_count = 0
    pdf_files = sorted(folder.glob("*.pdf"))
    logger.info("Step 1/3: Found %d PDF documents in %s", len(pdf_files), folder)

    for pdf_path in pdf_files:
        document_count += 1
        logger.info("Step 2/3: Parsing %s (%d/%d)", pdf_path.name, document_count, len(pdf_files))
        reader = PdfReader(str(pdf_path))
        for page_number, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            for start in range(0, len(text), 1800):
                chunk_text = text[start : start + 2000].strip()
                if chunk_text:
                    chunks.append(
                        {
                            "text": chunk_text,
                            "meta": {
                                "doc": resolve_doc_title(pdf_path.name),
                                "section": f"Page {page_number}",
                            },
                        }
                    )
    logger.info("Step 3/3: Created %d chunks from %d documents", len(chunks), document_count)
    return chunks, document_count