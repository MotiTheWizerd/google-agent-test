from typing import Any, Dict

# Sketch of a long-running job initiator.
# In real ADK, you'd wrap with LongRunningFunctionTool and resume via updates.
def begin_reimbursement(purpose: str, amount: float) -> Dict[str, Any]:
    """
    Start an approval flow for reimbursement and return a ticket id.
    Use for multi-step flows that require human/system approval.

    Returns:
      {"status":"pending","ticket_id":"appr-001","purpose":..., "amount":...}
    """
    return {
        "status": "pending",
        "ticket_id": "appr-001",
        "purpose": purpose,
        "amount": amount,
    }
