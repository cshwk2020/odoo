import time

def generate_trans_group_id(saleorder_id=None, picking_id=None):
    # nanosecond timestamp since epoch
    ts = int(time.time_ns())
    parts = []
    if saleorder_id:
        parts.append(f"SO{saleorder_id}")
    if picking_id:
        parts.append(f"PK{picking_id}")
    return f"{ts}_{'_'.join(parts)}"
