#!/usr/bin/env python3
"""Analyze coverage gaps and suggest improvements."""

import json


def analyze_coverage():
    """Analyze coverage.json and identify low-coverage files."""
    with open("coverage.json") as f:
        data = json.load(f)

    print("Files with <90% coverage:\n")
    print(f"{'File':<60} {'Coverage':>10} {'Lines':>15}")
    print("=" * 87)

    files = []
    for filepath, filedata in data["files"].items():
        summary = filedata["summary"]
        pct = summary["percent_covered"]
        if pct < 90:
            covered = summary["covered_lines"]
            total = summary["num_statements"]
            files.append((filepath, pct, covered, total))

    # Sort by coverage percentage (lowest first)
    files.sort(key=lambda x: x[1])

    for filepath, pct, covered, total in files:
        # Shorten path for display
        short_path = filepath.replace("custom_components\\imou_life\\", "").replace(
            "custom_components/imou_life/", ""
        )
        print(f"{short_path:<60} {pct:>9.1f}% {covered:>7}/{total:<6}")

    print("\n" + "=" * 87)
    print(f"\nTotal coverage: {data['totals']['percent_covered']:.2f}%")
    print(
        f"Total lines: {data['totals']['covered_lines']}/{data['totals']['num_statements']}"
    )

    # Calculate potential improvement
    print("\nPriority Improvements:")
    for filepath, pct, covered, total in files[:5]:
        short_path = filepath.replace("custom_components\\imou_life\\", "").replace(
            "custom_components/imou_life/", ""
        )
        missing = total - covered
        potential = (missing / total) * 100
        print(
            f"  - {short_path}: +{potential:.1f}% possible ({missing} uncovered lines)"
        )


if __name__ == "__main__":
    analyze_coverage()
