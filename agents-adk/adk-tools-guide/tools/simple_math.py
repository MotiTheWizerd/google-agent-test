from typing import Optional, Dict, Any

def add(a: float, b: float, hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Add two numbers.
    Use when the user asks for precise numeric addition.

    Args:
      a (float): First term.
      b (float): Second term.
      hint (str, optional): Extra guidance (e.g., units).

    Returns:
      dict: {"status":"success","sum":<float>,"hint_used":<bool>}
    """
    return {"status": "success", "sum": a + b, "hint_used": hint is not None}
