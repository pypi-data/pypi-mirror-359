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
    apply_category_mapping
)

@dataclass
class PPEComplianceConfig(BaseConfig):
    smoothing_algorithm: str = "observability"  # "window" or "observability"
    no_hardhat_threshold: float = 0.91
    no_mask_threshold: float = 0.2
    no_safety_vest_threshold: float = 0.2
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
        # Number of frames to use for smoothing (window size)
        self.window_size = 20
        # Number of frames to persist a violation after it disappears (cooldown)
        self.cooldown_frames = 5
        # List of violation categories to track (should match config, but kept here for internal use)
        self.violation_categories = ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
        # For each violation category, track {instance_id: deque of detections}
        self.violation_windows = {cat: {} for cat in self.violation_categories}
        # For each violation category, track cooldowns: {cat: {instance_id: cooldown_counter}}
        self.violation_cooldowns = {cat: {} for cat in self.violation_categories}

    def process(self, data: Any, config: ConfigProtocol, context: Optional[ProcessingContext] = None) -> ProcessingResult:
        """
        Main entry point for PPE compliance detection post-processing.
        Applies category mapping, violation smoothing, counting, alerting, and summary generation.
        Returns a ProcessingResult with all relevant outputs.
        """
        start_time = time.time()
        try:
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
            # Apply violation smoothing (window or observability)
            processed_data = self._filter_ppe_violations(processed_data, config)

            # Compute summaries and alerts
            general_counting_summary = calculate_counting_summary(data)
            counting_summary = self._count_categories(processed_data, config)
            insights = self._generate_insights(counting_summary, config)
            alerts = self._check_alerts(counting_summary, config)
            predictions = self._extract_predictions(processed_data)
            summary = self._generate_summary(counting_summary, alerts)

            context.mark_completed()

            # Build result object
            result = self.create_result(
                data={
                    "counting_summary": counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "alerts": alerts,
                    "total_violations": counting_summary.get("total_count", 0),
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            return result

        except Exception as e:
            # Log and return error result on failure
            self.logger.error(f"Error in PPE compliance: {str(e)}")
            return self.create_error_result(
                f"PPE compliance processing failed: {str(e)}",
                error_type="PPEComplianceProcessingError",
                usecase=self.name,
                category=self.category,
                context=context
            )

    def _filter_ppe_violations(self, detections: list, config: PPEComplianceConfig) -> list:
        """
        Selects and applies the configured smoothing algorithm for PPE violations.
        - "window": original window+cooldown smoothing
        - "observability": observability/confidence tradeoff smoothing
        """
        if getattr(config, "smoothing_algorithm", "window") == "observability":
            return self._filter_ppe_violations_observability(detections, config)
        else:
            return self._filter_ppe_violations_window(detections, config)

    def _filter_ppe_violations_window(self, detections: list, config: PPEComplianceConfig) -> list:
        """
        Smoothing algorithm 1: window+cooldown.
        For each violation category, track each unique instance (by track_id or quantized centroid).
        - Maintain a sliding window of detections for each instance.
        - If an instance disappears, keep it for cooldown_frames.
        - Output the most recent detection if the average confidence in the window exceeds the threshold.
        """
        output = []
        for cat in self.violation_categories:
            # Track all current instance IDs for this frame
            current_ids = set()
            for det in [d for d in detections if d.get('category') == cat]:
                # Use track_id if available, else quantized centroid as fallback
                if 'track_id' in det and det['track_id'] is not None:
                    instance_id = (cat, det['track_id'])
                else:
                    bbox = det.get('bounding_box', None)
                    if bbox:
                        x = bbox.get('x', 0)
                        y = bbox.get('y', 0)
                        w = bbox.get('width', 0)
                        h = bbox.get('height', 0)
                        # Quantize centroid to reduce jitter
                        cx = int((x + w / 2) // 10)
                        cy = int((y + h / 2) // 10)
                        instance_id = (cat, cx, cy)
                    else:
                        instance_id = (cat, None)
                current_ids.add(instance_id)
                # Initialize window and cooldown if new instance
                if instance_id not in self.violation_windows[cat]:
                    self.violation_windows[cat][instance_id] = deque(maxlen=self.window_size)
                self.violation_windows[cat][instance_id].append(det)
                self.violation_cooldowns[cat][instance_id] = self.cooldown_frames

            # Handle expired instances (not seen in this frame)
            expired = []
            for instance_id, window in list(self.violation_windows[cat].items()):
                if instance_id not in current_ids:
                    self.violation_cooldowns[cat][instance_id] -= 1
                if self.violation_cooldowns[cat][instance_id] <= 0:
                    expired.append(instance_id)
                    continue
                # Compute average confidence in window
                confs = [d.get('confidence', 0.0) for d in window]
                avg_conf = sum(confs) / len(confs) if confs else 0.0
                # Get threshold for this category
                threshold_name = f"{cat.lower().replace('-', '_')}_threshold"
                threshold = getattr(config, threshold_name, 0.2)
                if avg_conf >= threshold:
                    # Output the most recent detection for this instance
                    output.append(window[-1])
            # Remove expired instances
            for instance_id in expired:
                self.violation_windows[cat].pop(instance_id, None)
                self.violation_cooldowns[cat].pop(instance_id, None)
        return output

    def _filter_ppe_violations_observability(self, detections: list, config: PPEComplianceConfig) -> list:
        """
        Smoothing algorithm 2: observability/confidence tradeoff.
        For each instance, keep if (confidence_factor <= observability_score).
        - High-confidence detections are always kept.
        - Borderline detections are kept if they are consistent over time (observability).
        """
        output = []
        for cat in self.violation_categories:
            current_ids = set()
            for det in [d for d in detections if d.get('category') == cat]:
                # Use track_id if available, else quantized centroid as fallback
                if 'track_id' in det and det['track_id'] is not None:
                    instance_id = (cat, det['track_id'])
                else:
                    bbox = det.get('bounding_box', None)
                    if bbox:
                        x = bbox.get('x', 0)
                        y = bbox.get('y', 0)
                        w = bbox.get('width', 0)
                        h = bbox.get('height', 0)
                        cx = int((x + w / 2) // 10)
                        cy = int((y + h / 2) // 10)
                        instance_id = (cat, cx, cy)
                    else:
                        instance_id = (cat, None)
                current_ids.add(instance_id)
                # Initialize window and cooldown if new instance
                if instance_id not in self.violation_windows[cat]:
                    self.violation_windows[cat][instance_id] = deque(maxlen=self.window_size)
                self.violation_windows[cat][instance_id].append(det)
                self.violation_cooldowns[cat][instance_id] = self.cooldown_frames

            # Handle expired instances (not seen in this frame)
            expired = []
            for instance_id, window in list(self.violation_windows[cat].items()):
                if instance_id not in current_ids:
                    self.violation_cooldowns[cat][instance_id] -= 1
                if self.violation_cooldowns[cat][instance_id] <= 0:
                    expired.append(instance_id)
                    continue
                # Observability score: fraction of frames in window where detection was present
                observability_score = len(window) / self.window_size
                # Use the most recent detection for confidence
                det = window[-1]
                conf = det.get('confidence', 0.0)
                threshold_name = f"{cat.lower().replace('-', '_')}_threshold"
                conf_thres = getattr(config, threshold_name, 0.2)
                conf_range = conf_thres / 2.0
                if conf >= conf_thres:
                    # High confidence, always keep
                    output.append(det)
                elif conf >= conf_thres - conf_range:
                    # Borderline: apply observability/confidence tradeoff
                    confidence_factor = (conf_thres - conf) / conf_range if conf_range > 0 else 1.0
                    if confidence_factor <= observability_score:
                        output.append(det)
                # else: too low confidence, discard
            # Remove expired instances
            for instance_id in expired:
                self.violation_windows[cat].pop(instance_id, None)
                self.violation_cooldowns[cat].pop(instance_id, None)
        return output

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
        Generate a short summary string for the result.
        """
        total = summary.get("total_count", 0)
        parts = [f"{total} PPE violation(s) detected"] if total else []
        if alerts:
            parts.append(f"{len(alerts)} alert(s)")
        return ", ".join(parts)


