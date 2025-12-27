from typing import List, Dict, Any


def normalize_blocks(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Wrap raw extracted blocks into diff-compatible structure.
    """
    normalized = []
    for b in blocks:
        normalized.append(
            {
                "change": "unchanged",
                "old": b,
                "new": b,
            }
        )
    return normalized
