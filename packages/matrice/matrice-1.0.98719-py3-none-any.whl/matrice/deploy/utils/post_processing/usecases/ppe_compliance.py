from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
from collections import deque
from datetime import datetime, timezone

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    calculate_counting_summary,
    match_results_structure,
    apply_category_mapping,
    bbox_smoothing,
    BBoxSmoothingConfig,
    BBoxSmoothingTracker
)

@dataclass
class PPEComplianceConfig(BaseConfig):
    # Smoothing configuration
    enable_smoothing: bool = True
    smoothing_algorithm: str = "observability"  # "window" or "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5
    
    # Violation thresholds
    no_hardhat_threshold: float = 0.91
    no_mask_threshold: float = 0.4
    no_safety_vest_threshold: float = 0.4
    
    violation_categories: List[str] = field(default_factory=lambda: [
        "NO-Hardhat", "NO-Mask", "NO-Safety Vest"
    ])
    alert_config: Optional[AlertConfig] = None
    index_to_category: Optional[Dict[int, str]] = field(default_factory=lambda: {
        -1: 'Hardhat', 0: 'Mask', 1: 'NO-Hardhat', 2: 'NO-Mask', 3: 'NO-Safety Vest',
        4: 'Person', 5: 'Safety Cone', 6: 'Safety Vest', 7: 'machinery', 8: 'vehicle'
    })

class PPEComplianceUseCase(BaseProcessor):
    """PPE compliance detection use case with violation smoothing and alerting."""

    def __init__(self):
        super().__init__("ppe_compliance_detection")
        self.category = "ppe"
        
        # List of violation categories to track
        self.violation_categories = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
        
        # Initialize smoothing tracker
        self.smoothing_tracker = None

    def process(self, data: Any, config: ConfigProtocol, context: Optional[ProcessingContext] = None, stream_info: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Main entry point for PPE compliance detection post-processing.
        Applies category mapping, violation smoothing, counting, alerting, and summary generation.
        Returns a ProcessingResult with all relevant outputs.
        """
        start_time = time.time()
        # Ensure config is correct type
        if not isinstance(config, PPEComplianceConfig):
            return self.create_error_result("Invalid config type", usecase=self.name, category=self.category, context=context)
        if context is None:
            context = ProcessingContext()

        # Detect input format and store in context
        input_format = match_results_structure(data)
        context.input_format = input_format
        context.no_hardhat_threshold = config.no_hardhat_threshold

        # Map detection indices to category names if needed
        processed_data = apply_category_mapping(data, config.index_to_category)
        
        # Apply bbox smoothing if enabled
        if config.enable_smoothing:
            # Initialize smoothing tracker if not exists
            if self.smoothing_tracker is None:
                smoothing_config = BBoxSmoothingConfig(
                    smoothing_algorithm=config.smoothing_algorithm,
                    window_size=config.smoothing_window_size,
                    cooldown_frames=config.smoothing_cooldown_frames,
                    confidence_threshold=config.no_mask_threshold,  # Use mask threshold as default
                    confidence_range_factor=config.smoothing_confidence_range_factor,
                    enable_smoothing=True
                )
                self.smoothing_tracker = BBoxSmoothingTracker(smoothing_config)
            
            # Apply smoothing to violation detections
            violation_detections = [d for d in processed_data if d.get('category') in self.violation_categories]
            smoothed_violations = bbox_smoothing(violation_detections, self.smoothing_tracker.config, self.smoothing_tracker)
            
            # Replace violation detections with smoothed ones
            non_violation_detections = [d for d in processed_data if d.get('category') not in self.violation_categories]
            processed_data = non_violation_detections + smoothed_violations

        # Extract frame information from stream_info
        frame_number = None
        if stream_info:
            input_settings = stream_info.get("input_settings", {})
            start_frame = input_settings.get("start_frame")
            end_frame = input_settings.get("end_frame")
            # If start and end frame are the same, it's a single frame
            if start_frame is not None and end_frame is not None and start_frame == end_frame:
                frame_number = start_frame

        # Compute summaries and alerts
        general_counting_summary = calculate_counting_summary(data)
        counting_summary = self._count_categories(processed_data, config)
        insights = self._generate_insights(counting_summary, config)
        alerts = self._check_alerts(counting_summary, config)
        predictions = self._extract_predictions(processed_data)
        summary = self._generate_summary(counting_summary, alerts)

        # Step: Generate structured events and tracking stats with frame-based keys
        events_list = self._generate_events(counting_summary, alerts, config, frame_number)
        tracking_stats_list = self._generate_tracking_stats(counting_summary, insights, summary, config, frame_number)

        # Extract frame-based dictionaries from the lists
        events = events_list[0] if events_list else {}
        tracking_stats = tracking_stats_list[0] if tracking_stats_list else {}

        context.mark_completed()

        # Build result object
        result = self.create_result(
            data={
                "counting_summary": counting_summary,
                "general_counting_summary": general_counting_summary,
                "alerts": alerts,
                "total_violations": counting_summary.get("total_count", 0),
                "events": events,
                "tracking_stats": tracking_stats,
            },
            usecase=self.name,
            category=self.category,
            context=context
        )
        result.summary = summary
        result.insights = insights
        result.predictions = predictions
        return result
        
    def _generate_events(self, counting_summary: Dict, alerts: List, config: PPEComplianceConfig, frame_number: Optional[int] = None) -> List[Dict]:
        """Generate structured events for the output format with frame-based keys."""
        from datetime import datetime, timezone

        # Use frame number as key, fallback to 'current_frame' if not available
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        events = [{frame_key: []}]
        frame_events = events[0][frame_key]
        total_violations = counting_summary.get("total_count", 0)

        if total_violations > 0:
            event = {
                "type": "ppe_violation",
                "severity": "info",
                "category": "ppe",
                "count": total_violations,
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC'),
                "location_info": None,
                "human_text": f"{total_violations} PPE violations detected"
            }
            frame_events.append(event)

        # Add alert events
        for alert in alerts:
            alert_event = {
                "type": alert.get("type", "alert"),
                "severity": alert.get("severity", "warning"),
                "category": alert.get("category", "ppe"),
                "count": alert.get("current_count", 0),
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC'),
                "location_info": alert.get("zone"),
                "human_text": alert.get("human_text", "PPE alert triggered")
            }
            frame_events.append(alert_event)

        return events

    def _generate_tracking_stats(self, counting_summary: Dict, insights: List[str], summary: str, config: PPEComplianceConfig, frame_number: Optional[int] = None) -> List[Dict]:
        """Generate structured tracking stats for the output format with frame-based keys."""
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        tracking_stats = [{frame_key: []}]
        frame_tracking_stats = tracking_stats[0][frame_key]
        total_violations = counting_summary.get("total_count", 0)

        if total_violations > 0:
            tracking_stat = {
                "type": "ppe_tracking",
                "category": "ppe",
                "count": total_violations,
                "insights": insights,
                "summary": summary,
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC'),
                "human_text": summary
            }
            frame_tracking_stats.append(tracking_stat)

        return tracking_stats



    def _count_categories(self, detections: list, config: PPEComplianceConfig) -> dict:
        """
        Count the number of detections per category and return a summary dict.
        """
        counts = {}
        for det in detections:
            cat = det.get('category', 'unknown')
            counts[cat] = counts.get(cat, 0) + 1
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "detections": [
                {"bounding_box": det.get("bounding_box"), "category": det.get("category")}
                for det in detections
            ]
        }

    # Human-friendly display names for violation categories
    CATEGORY_DISPLAY = {
        "NO-Hardhat": "No Hardhat Violations",
        "NO-Mask": "No Mask Violations",
        "NO-Safety Vest": "No Safety Vest Violations"
    }

    def _generate_insights(self, summary: dict, config: PPEComplianceConfig) -> List[str]:
        """
        Generate human-readable insights for each violation category.
        """
        insights = []
        per_cat = summary.get("per_category_count", {})
        for cat, count in per_cat.items():
            display = self.CATEGORY_DISPLAY.get(cat, cat)
            insights.append(f"{display}:{count}")
        return insights

    def _check_alerts(self, summary: dict, config: PPEComplianceConfig) -> List[Dict]:
        """
        Check if any alert thresholds are exceeded and return alert dicts.
        """
        alerts = []
        if not config.alert_config:
            return alerts
        total = summary.get("total_count", 0)
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total >= threshold:
                    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')
                    alert_description = f"PPE violation count ({total}) exceeds threshold ({threshold})"
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": alert_description,
                        "category": category,
                        "current_count": total,
                        "threshold": threshold,
                        "human_text": f"Time: {timestamp}\n{alert_description}"
                    })
        return alerts

    def _extract_predictions(self, detections: list) -> List[Dict[str, Any]]:
        """
        Extract prediction details for output (category, confidence, bounding box).
        """
        return [
            {
                "category": det.get("category", "unknown"),
                "confidence": det.get("confidence", 0.0),
                "bounding_box": det.get("bounding_box", {})
            }
            for det in detections
        ]

    def _generate_summary(self, summary: dict, alerts: List) -> str:
        """
        Generate a human_text string for the result, including per-category insights if available.
        """
        total = summary.get("total_count", 0)
        lines = [f"{total} PPE violation(s) detected"] if total else []
        # Add per-category insights in new lines
        per_cat = summary.get("per_category_count", {})
        for cat, count in per_cat.items():
            display = self.CATEGORY_DISPLAY.get(cat, cat)
            lines.append(f"{display}:{count}")
        if alerts:
            lines.append(f"{len(alerts)} alert(s)")
        return "\n".join(lines)


