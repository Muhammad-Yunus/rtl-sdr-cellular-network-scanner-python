"""Terminal output for scan results."""

from __future__ import annotations

from cellscan.model.spectrum import CarrierPeak, ScanResult


def format_terminal(results: list[CarrierPeak]) -> str:
    """Format detected carriers for terminal display.

    Output format:
        <FREQ_MHZ>  <POWER_DBM>  <TECHNOLOGY>  <ESTIMATED OPERATORS>
    """
    lines = []
    lines.append("CELLSCAN - RF Carrier Discovery")
    lines.append("-" * 80)
    if not results:
        lines.append("No carriers detected.")
        return "\n".join(lines)

    lines.append(f"{'FREQ (MHz)':>12}  {'POW (dBm)':>10}  {'TECHNOLOGY':<14}  {'ESTIMATED OPERATORS'}")
    lines.append("-" * 80)
    for c in sorted(results, key=lambda x: x.frequency_mhz):
        if c.candidates:
            op_parts = []
            for o in c.candidates:
                if o.mnc:
                    op_parts.append(f"{o.name} ({o.mnc})")
                else:
                    op_parts.append(o.name)
            ops_str = ", ".join(op_parts)
        else:
            ops_str = "—"
        lines.append(f"{c.frequency_mhz:>12.3f}  {c.power_dbm:>+10.1f}  {c.technology.value:<14}  {ops_str}")
    lines.append("-" * 80)
    lines.append(f"Total: {len(results)} carrier(s) detected")
    return "\n".join(lines)
