"""
SmartEdge AgriGuardian — Knowledge Base Lookup Service
======================================================
File: modules/knowledge_base/kb_service.py

Provides fast, indexed lookup for disease objects and action plans from
knowledge_base.json based on YOLO class predictions or disease IDs.
"""

import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

HERE = os.path.dirname(os.path.abspath(__file__))
KB_FILE_PATH = os.path.join(HERE, "knowledge_base.json")

# Fallback path if module folder version isn't present
if not os.path.exists(KB_FILE_PATH):
    PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    KB_FILE_PATH = os.path.join(PROJECT_ROOT, "knowledge-base", "knowledge_base.json")

_disease_index: Dict[str, Dict] = {}


def _init_index() -> None:
    """Loads knowledge_base.json into memory and indexes by disease ID and name."""
    global _disease_index
    if _disease_index:
        return

    logger.info(f"Indexing Knowledge Base from: {KB_FILE_PATH}")
    if not os.path.exists(KB_FILE_PATH):
        logger.error(f"Knowledge Base file missing: {KB_FILE_PATH}")
        return

    try:
        with open(KB_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            diseases = data.get("diseases", [])
            for item in diseases:
                d_id = item.get("id", "").lower()
                d_name = item.get("name", "").lower()
                d_disease = item.get("disease", "").lower()
                
                # Index by multiple keys for reliable matching
                if d_id:
                    _disease_index[d_id] = item
                if d_name:
                    _disease_index[d_name] = item
                if d_disease:
                    _disease_index[d_disease] = item

        logger.info(f"Successfully indexed {len(diseases)} disease objects from Knowledge Base.")
    except Exception as exc:
        logger.error(f"Failed to parse Knowledge Base JSON: {exc}")


def get_disease(query: str) -> Optional[Dict]:
    """
    Retrieves the matching disease object (including action_plan) for a given disease ID or class name.

    Args:
        query: YOLO prediction class name (e.g. 'Tomato_Early_blight', 'Potato___Late_blight').

    Returns:
        The matched disease dictionary object, or None if no match found.
    """
    _init_index()
    if not query:
        return None

    query_clean = query.strip().lower()
    
    # 1. Direct key match
    if query_clean in _disease_index:
        return _disease_index[query_clean]

    # 2. Fuzzy substring match against keys
    for key, obj in _disease_index.items():
        if query_clean in key or key in query_clean:
            return obj
            
    # 3. Clean underscores and match
    normalized = query_clean.replace("___", "_").replace("__", "_")
    for key, obj in _disease_index.items():
        key_norm = key.replace("___", "_").replace("__", "_")
        if normalized in key_norm or key_norm in normalized:
            return obj

    logger.warning(f"No Knowledge Base match found for query: '{query}'")
    return None
