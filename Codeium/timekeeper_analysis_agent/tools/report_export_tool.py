# Copyright 2025 DatSciX
# Report Export Tool

"""Tool for exporting analysis reports in various formats."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def export_report(
    report_data: Dict[str, Any],
    output_path: str,
    format: str = "markdown",
    include_timestamp: bool = True
) -> Dict[str, Any]:
    """
    Export analysis report to specified format.

    Args:
        report_data: Dictionary containing report sections and data
        output_path: Path where report should be saved
        format: Output format ("markdown", "json", "text")
        include_timestamp: Whether to include timestamp in filename

    Returns:
        Dictionary containing:
        - success: boolean indicating if export succeeded
        - output_file: path to exported file
        - message: status message
    """
    try:
        path = Path(output_path)

        # Add timestamp to filename if requested
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = path.stem
            path = path.with_stem(f"{stem}_{timestamp}")

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "markdown":
            content = _generate_markdown_report(report_data)
            path = path.with_suffix(".md")
        elif format == "json":
            content = json.dumps(report_data, indent=2, default=str)
            path = path.with_suffix(".json")
        elif format == "text":
            content = _generate_text_report(report_data)
            path = path.with_suffix(".txt")
        else:
            return {
                "success": False,
                "output_file": None,
                "message": f"Unsupported format: {format}"
            }

        # Write content to file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "output_file": str(path),
            "message": f"Report exported successfully to {path}"
        }

    except Exception as e:
        return {
            "success": False,
            "output_file": None,
            "message": f"Error exporting report: {str(e)}"
        }


def _generate_markdown_report(data: Dict[str, Any]) -> str:
    """Generate Markdown formatted report."""
    lines = []

    # Title
    lines.append("# Timekeeper Analysis Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Executive Summary
    if "executive_summary" in data:
        lines.append("## Executive Summary\n")
        summary = data["executive_summary"]
        if isinstance(summary, dict):
            for key, value in summary.items():
                lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        elif isinstance(summary, list):
            for item in summary:
                lines.append(f"- {item}")
        else:
            lines.append(str(summary))
        lines.append("")

    # Data Overview
    if "data_overview" in data:
        lines.append("## Data Overview\n")
        overview = data["data_overview"]
        if isinstance(overview, dict):
            for key, value in overview.items():
                lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        lines.append("")

    # Productivity Analysis
    if "productivity_analysis" in data:
        lines.append("## Productivity Analysis\n")
        lines.append(_format_section(data["productivity_analysis"]))
        lines.append("")

    # Billing Anomalies
    if "billing_anomaly_analysis" in data:
        lines.append("## Billing Anomaly Detection\n")
        lines.append(_format_section(data["billing_anomaly_analysis"]))
        lines.append("")

    # Resource Optimization
    if "resource_optimization_analysis" in data:
        lines.append("## Resource Optimization Recommendations\n")
        lines.append(_format_section(data["resource_optimization_analysis"]))
        lines.append("")

    # Action Plan
    if "action_plan" in data:
        lines.append("## Action Plan\n")
        lines.append(_format_section(data["action_plan"]))
        lines.append("")

    return "\n".join(lines)


def _generate_text_report(data: Dict[str, Any]) -> str:
    """Generate plain text formatted report."""
    lines = []

    lines.append("=" * 80)
    lines.append("TIMEKEEPER ANALYSIS REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")

    for section_name, section_data in data.items():
        lines.append("-" * 80)
        lines.append(section_name.replace("_", " ").upper())
        lines.append("-" * 80)
        lines.append(_format_section(section_data, indent=0))
        lines.append("")

    return "\n".join(lines)


def _format_section(data: Any, indent: int = 0) -> str:
    """Recursively format section data."""
    lines = []
    prefix = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}**{key.replace('_', ' ').title()}:**")
                lines.append(_format_section(value, indent + 1))
            else:
                lines.append(f"{prefix}- **{key.replace('_', ' ').title()}:** {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(_format_section(item, indent))
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{data}")

    return "\n".join(lines)