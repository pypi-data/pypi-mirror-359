from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
from datetime import datetime, timezone

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..core.config import BaseConfig, AlertConfig, ZoneConfig
from ..utils import (
    filter_by_confidence,
    filter_by_categories,
    apply_category_mapping,
    count_objects_in_zones,
    calculate_counting_summary,
    match_results_structure,
    bbox_smoothing,
    BBoxSmoothingConfig,
    BBoxSmoothingTracker
)

@dataclass
class VehicleMonitoringConfig(BaseConfig):
    """Configuration for vehicle monitoring use case."""
    enable_smoothing: bool = True
    smoothing_algorithm: str = "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5
    enable_tracking: bool = True
    tracking_threshold: float = 0.6
    max_track_age_frames: int = 50  # Reduced to match short video duration (~13s at 30 fps)
    zone_config: Optional[ZoneConfig] = None
    confidence_threshold: float = 0.6
    vehicle_categories: List[str] = field(
        default_factory=lambda: ['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow']
    )
    target_vehicle_categories: List[str] = field(
        default_factory=lambda: ['car', 'bicycle', 'bus', 'garbagevan', 'truck', 'motorbike', 'van']
    )
    alert_config: Optional[AlertConfig] = None
    time_window_minutes: int = 60
    enable_unique_counting: bool = True
    index_to_category: Optional[Dict[int, str]] = field(
        default_factory=lambda: {
            1: "bicycle",
            2: "car",
            3: "motorbike",
            4: "auto rickshaw",
            5: "bus",
            6: "garbagevan",
            7: "truck",
            8: "minibus",
            10: "army vehicle",
            11: "pickup",
            12: "policecar",
            13: "rickshaw",
            14: "scooter",
            15: "suv",
            16: "taxi",
            17: "three wheelers -CNG-",
            18: "human hauler",
            19: "van",
            20: "wheelbarrow",
        }
    )

    def _post_init_(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        if self.tracking_threshold < 0.0 or self.tracking_threshold > 1.0:
            raise ValueError("tracking_threshold must be between 0.0 and 1.0")

class VehicleMonitoringUseCase(BaseProcessor):
    """Vehicle monitoring use case with zone analysis, tracking, and alerting."""
    
    def __init__(self):
        """Initialize vehicle monitoring use case."""
        super().__init__("vehicle_monitoring")
        self.category = "traffic"
        self.smoothing_tracker = None
        self.tracker = None
        self.vehicle_categories = ['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow']
        self._vehicle_total_track_ids = {cat: set() for cat in self.vehicle_categories}
        self._vehicle_current_frame_track_ids = {cat: set() for cat in self.vehicle_categories}
        self._track_last_seen = {cat: {} for cat in self.vehicle_categories}
        self._total_frame_counter = 0
        self._global_frame_offset = 0

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for vehicle monitoring."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.6,
                    "description": "Minimum confidence threshold for vehicle detections"
                },
                "tracking_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.6,
                    "description": "Minimum confidence threshold for vehicle tracking"
                },
                "enable_tracking": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable tracking for unique vehicle counting"
                },
                "max_track_age_frames": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 50,
                    "description": "Maximum number of frames a track ID is kept before being removed"
                },
                "zone_config": {
                    "type": "object",
                    "properties": {
                        "zones": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 2,
                                    "maxItems": 2
                                },
                                "minItems": 3
                            },
                            "description": "Zone definitions as polygons for congestion monitoring"
                        },
                        "zone_confidence_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "description": "Per-zone confidence thresholds"
                        }
                    }
                },
                "vehicle_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow'],
                    "description": "Category names that represent vehicles"
                },
                "enable_unique_counting": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable unique vehicle counting using tracking"
                },
                "time_window_minutes": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 60,
                    "description": "Time window for vehicle counting analysis in minutes"
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for vehicle alerts"
                        },
                        "occupancy_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Zone occupancy thresholds for vehicle alerts"
                        }
                    }
                }
            },
            "required": ["confidence_threshold", "tracking_threshold"],
            "additionalProperties": False
        }
    
    def create_default_config(self, **overrides) -> VehicleMonitoringConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.6,
            "tracking_threshold": 0.6,
            "enable_tracking": True,
            "max_track_age_frames": 50,
            "enable_analytics": True,
            "enable_unique_counting": True,
            "time_window_minutes": 60,
            "vehicle_categories": ['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow'],
        }
        defaults.update(overrides)
        return VehicleMonitoringConfig(**defaults)
    
    def _get_track_ids_info(self, detections: list, frame_number: Optional[int] = None) -> Dict[str, Any]:
        """Get detailed information about track IDs for vehicles (per frame)."""
        frame_track_ids = set()
        for det in detections:
            tid = det.get('track_id')
            if tid is not None:
                frame_track_ids.add(tid)
        
        total_track_ids = set()
        for cat, track_ids in self._vehicle_total_track_ids.items():
            total_track_ids.update(track_ids)
        
        self.logger.debug(f"Track IDs info: frame_track_ids={frame_track_ids}, total_track_ids={total_track_ids}")
        return {
            "total_count": len(total_track_ids),
            "current_frame_count": len(frame_track_ids),
            "total_unique_track_ids": len(total_track_ids),
            "current_frame_track_ids": list(frame_track_ids),
            "last_update_time": time.time(),
            "total_frames_processed": self._total_frame_counter,
            "frame_number": frame_number
        }
    
    @staticmethod
    def _iou(bbox1, bbox2):
        """Compute IoU between two bboxes (dicts with xmin/ymin/xmax/ymax)."""
        x1 = max(bbox1["xmin"], bbox2["xmin"])
        y1 = max(bbox1["ymin"], bbox2["ymin"])
        x2 = min(bbox1["xmax"], bbox2["xmax"])
        y2 = min(bbox1["ymax"], bbox2["ymax"])
        inter_w = max(0, x2 - x1)
        inter_h = max(0, y2 - y1)
        inter_area = inter_w * inter_h
        area1 = (bbox1["xmax"] - bbox1["xmin"]) * (bbox1["ymax"] - bbox1["ymin"])
        area2 = (bbox2["xmax"] - bbox2["xmin"]) * (bbox2["ymax"] - bbox2["ymin"])
        union = area1 + area2 - inter_area
        if union == 0:
            return 0.0
        return inter_area / union
    
    @staticmethod
    def _deduplicate_vehicles(detections, iou_thresh=0.7):
        """Suppress duplicate/overlapping vehicles with same label and high IoU."""
        filtered = []
        used = [False] * len(detections)
        for i, det in enumerate(detections):
            if used[i]:
                continue
            group = [i]
            for j in range(i+1, len(detections)):
                if used[j]:
                    continue
                if det.get("category") == detections[j].get("category"):
                    bbox1 = det.get("bounding_box")
                    bbox2 = detections[j].get("bounding_box")
                    if bbox1 and bbox2:
                        iou = VehicleMonitoringUseCase._iou(bbox1, bbox2)
                        if iou > iou_thresh:
                            used[j] = True
                            group.append(j)
            best_idx = max(group, key=lambda idx: detections[idx].get("confidence", 0))
            filtered.append(detections[best_idx])
            used[best_idx] = True
        return filtered
    
    def _update_vehicle_tracking_state(self, detections: list, frame_number: Optional[int] = None):
        """Track unique vehicle track_ids per category for total count after tracking."""
        self._vehicle_current_frame_track_ids = {cat: set() for cat in self.vehicle_categories}
        config = getattr(self, '_config', None)
        current_frame = frame_number if frame_number is not None else self._total_frame_counter
        
        for det in detections:
            cat = det.get('category')
            track_id = det.get('track_id')
            if cat in self.vehicle_categories and track_id is not None:
                self._vehicle_total_track_ids[cat].add(track_id)
                self._vehicle_current_frame_track_ids[cat].add(track_id)
                self._track_last_seen[cat][track_id] = current_frame
        
        if config and config.max_track_age_frames:
            for cat in self.vehicle_categories:
                tracks_to_remove = [
                    track_id for track_id, last_seen in self._track_last_seen[cat].items()
                    if current_frame - last_seen > config.max_track_age_frames
                ]
                for track_id in tracks_to_remove:
                    self._vehicle_total_track_ids[cat].discard(track_id)
                    del self._track_last_seen[cat][track_id]
                if tracks_to_remove:
                    self.logger.debug(f"Removed {len(tracks_to_remove)} expired tracks for category {cat}")

    def get_total_vehicle_counts(self):
        """Return total unique track_id count for each vehicle category."""
        return {cat: len(ids) for cat, ids in self._vehicle_total_track_ids.items()}
    
    def reset_tracker(self) -> None:
        """Reset the advanced tracker instance."""
        if self.tracker is not None:
            self.tracker.reset()
            self.logger.info("AdvancedTracker reset for new tracking session")
    
    def reset_vehicle_tracking(self) -> None:
        """Reset vehicle tracking state."""
        self._vehicle_total_track_ids = {cat: set() for cat in self.vehicle_categories}
        self._vehicle_current_frame_track_ids = {cat: set() for cat in self.vehicle_categories}
        self._track_last_seen = {cat: {} for cat in self.vehicle_categories}
        self._total_frame_counter = 0
        self._global_frame_offset = 0
        self.logger.info("Vehicle tracking state reset")
    
    def reset_all_tracking(self) -> None:
        """Reset both advanced tracker and vehicle tracking state."""
        self.reset_tracker()
        self.reset_vehicle_tracking()
        self.logger.info("All vehicle tracking state reset")
    
    def process(self, data: Any, config: ConfigProtocol, context: Optional[ProcessingContext] = None, stream_info: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Process vehicle monitoring use case with tracking.
        """
        start_time = time.time()
        self._config = config
        
        try:
            if not isinstance(config, VehicleMonitoringConfig):
                return self.create_error_result(
                    "Invalid configuration type for vehicle monitoring",
                    usecase=self.name,
                    category=self.category,
                    context=context
                )
            
            if context is None:
                context = ProcessingContext()
            
            # Reset tracker for new video
            self.reset_all_tracking()
            self.logger.info("Reset tracking for new video processing")
            
            input_format = match_results_structure(data)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold
            context.tracking_threshold = config.tracking_threshold
            
            self.logger.info(f"Processing vehicle monitoring with format: {input_format.value}")
            
            processed_data = data
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(processed_data, config.confidence_threshold)
                self.logger.debug(f"Filtered {len(processed_data)} detections by confidence {config.confidence_threshold}")
            
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied category mapping")
            
            vehicle_processed_data = processed_data
            if config.target_vehicle_categories:
                vehicle_processed_data = filter_by_categories(processed_data.copy(), config.target_vehicle_categories)
                self.logger.debug(f"Filtered {len(vehicle_processed_data)} detections to target categories")
            
            if config.enable_smoothing:
                if self.smoothing_tracker is None:
                    smoothing_config = BBoxSmoothingConfig(
                        smoothing_algorithm=config.smoothing_algorithm,
                        window_size=config.smoothing_window_size,
                        cooldown_frames=config.smoothing_cooldown_frames,
                        confidence_threshold=config.tracking_threshold,
                        confidence_range_factor=config.smoothing_confidence_range_factor,
                        enable_smoothing=True
                    )
                    self.smoothing_tracker = BBoxSmoothingTracker(smoothing_config)
                
                vehicle_detections = [d for d in vehicle_processed_data if d.get('category') in self.vehicle_categories]
                smoothed_vehicles = bbox_smoothing(vehicle_detections, self.smoothing_tracker.config, self.smoothing_tracker)
                non_vehicle_detections = [d for d in vehicle_processed_data if d.get('category') not in self.vehicle_categories]
                vehicle_processed_data = non_vehicle_detections + smoothed_vehicles
                self.logger.debug(f"Applied smoothing to {len(smoothed_vehicles)} vehicle detections")
            
            if config.enable_tracking:
                try:
                    from ..advanced_tracker import AdvancedTracker
                    from ..advanced_tracker.config import TrackerConfig
                    
                    if self.tracker is None:
                        tracker_config = TrackerConfig(
                            track_high_thresh=config.tracking_threshold,
                            track_low_thresh=max(0.1, config.tracking_threshold - 0.5),
                            new_track_thresh=config.tracking_threshold,
                            match_thresh=0.6,  # Lowered for better track matching
                            track_buffer=config.max_track_age_frames,
                            max_time_lost=config.max_track_age_frames,
                            frame_rate=30
                        )
                        self.tracker = AdvancedTracker(tracker_config)
                        self.logger.info(f"Initialized AdvancedTracker with max_time_lost={config.max_track_age_frames}")
                    
                    vehicle_processed_data = self.tracker.update(vehicle_processed_data)
                    self.logger.debug(f"Tracked {len(vehicle_processed_data)} detections with track IDs: {[d.get('track_id') for d in vehicle_processed_data]}")
                
                except Exception as e:
                    self.logger.warning(f"AdvancedTracker failed: {e}")
            
            vehicle_processed_data = self._deduplicate_vehicles(vehicle_processed_data, iou_thresh=0.7)
            self.logger.debug(f"Deduplicated to {len(vehicle_processed_data)} detections")
            
            frame_number = None
            if stream_info and isinstance(stream_info, dict):
                input_settings = stream_info.get("input_settings", [{}])[0]
                start_frame = input_settings.get("start_frame")
                end_frame = input_settings.get("end_frame")
                if start_frame is not None and end_frame is not None and start_frame == end_frame:
                    frame_number = start_frame
            
            self._update_vehicle_tracking_state(vehicle_processed_data, frame_number)
            self._total_frame_counter += 1
            
            zones = config.zone_config.zones if config.zone_config else None
            vehicle_counting_summary = self._count_categories(vehicle_processed_data, config)
            vehicle_counting_summary['total_vehicle_counts'] = self.get_total_vehicle_counts()
            general_counting_summary = calculate_counting_summary(processed_data, zones=zones)
            
            zone_analysis = {}
            if config.zone_config and config.zone_config.zones:
                zone_analysis = count_objects_in_zones(vehicle_processed_data, config.zone_config.zones)
                self.logger.debug(f"Analyzed {len(zone_analysis)} zones")
            
            insights = self._generate_insights(vehicle_counting_summary, zone_analysis, config)
            alerts = self._check_alerts(vehicle_counting_summary, zone_analysis, config)
            metrics = self._calculate_metrics(vehicle_counting_summary, zone_analysis, config, context)
            predictions = self._extract_predictions(vehicle_processed_data)
            summary = self._generate_summary(vehicle_counting_summary, zone_analysis, alerts)
            
            events_list = self._generate_events(vehicle_counting_summary, zone_analysis, alerts, config, frame_number)
            tracking_stats_list = self._generate_tracking_stats(vehicle_processed_data, zone_analysis, insights, summary, config, frame_number)
            
            events = events_list[0] if events_list else {}
            tracking_stats = tracking_stats_list[0] if tracking_stats_list else {}
            
            context.mark_completed()
            
            result = self.create_result(
                data={
                    "general_counting_summary": general_counting_summary,
                    "counting_summary": vehicle_counting_summary,
                    "zone_analysis": zone_analysis,
                    "alerts": alerts,
                    "total_vehicles": vehicle_counting_summary.get("total_count", 0),
                    "zones_count": len(zone_analysis),
                    "events": events,
                    "tracking_stats": tracking_stats
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            
            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics
            
            if config.confidence_threshold < 0.3:
                result.add_warning(f"Low confidence threshold ({config.confidence_threshold}) may result in false positives")
            if config.tracking_threshold < 0.3:
                result.add_warning(f"Low tracking threshold ({config.tracking_threshold}) may result in tracking inconsistencies")
            
            processing_time = time.time() - start_time
            self.logger.info(f"Vehicle monitoring completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Vehicle monitoring failed: {str(e)}", exc_info=True)
            if context:
                context.mark_completed()
            return self.create_error_result(
                str(e), 
                type(e).__name__,
                usecase=self.name,
                category=self.category,
                context=context
            )
    
    def _count_categories(self, detections: list, config: VehicleMonitoringConfig) -> dict:
        """Count detections per category and return a summary dict."""
        counts = {}
        valid_detections = []
        for det in detections:
            cat = det.get('category', 'unknown')
            if cat in config.target_vehicle_categories:
                counts[cat] = counts.get(cat, 0) + 1
                valid_detections.append({
                    "bounding_box": det.get("bounding_box"),
                    "category": cat,
                    "confidence": det.get("confidence"),
                    "track_id": det.get("track_id"),
                    "frame_id": det.get("frame_id")
                })
        self.logger.debug(f"Counted {sum(counts.values())} detections: {counts}")
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "detections": valid_detections
        }
    
    CATEGORY_DISPLAY = {
        category: f"{category.title()} Vehicles" 
        for category in ['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow']
    }
    
    def _generate_insights(self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig) -> List[str]:
        """Generate human-readable insights from vehicle counting results."""
        insights = []
        total_vehicles = counting_summary.get("total_count", 0)
        
        if total_vehicles == 0:
            insights.append("No vehicles detected in the scene")
            return insights
        
        insights.append(f"EVENT: Detected {total_vehicles} vehicles in the scene")
        
        intensity_threshold = None
        if config.alert_config and config.alert_config.count_thresholds and "all" in config.alert_config.count_thresholds:
            intensity_threshold = config.alert_config.count_thresholds["all"]
        
        if intensity_threshold is not None:
            percentage = (total_vehicles / intensity_threshold) * 100
            if percentage < 20:
                insights.append(f"INTENSITY: Low congestion in the scene ({percentage:.1f}% of capacity)")
            elif percentage <= 50:
                insights.append(f"INTENSITY: Moderate congestion in the scene ({percentage:.1f}% of capacity)")
            elif percentage <= 70:
                insights.append(f"INTENSITY: Heavy congestion in the scene ({percentage:.1f}% of capacity)")
            else:
                insights.append(f"INTENSITY: Severe congestion in the scene ({percentage:.1f}% of capacity)")
        else:
            if total_vehicles > 15:
                insights.append(f"INTENSITY: Heavy congestion in the scene with {total_vehicles} vehicles")
            elif total_vehicles == 1:
                insights.append(f"INTENSITY: Low congestion in the scene")
        
        if zone_analysis:
            for zone_name, zone_counts in zone_analysis.items():
                zone_total = sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                if zone_total > 0:
                    percentage = (zone_total / total_vehicles) * 100
                    insights.append(f"Zone '{zone_name}': {zone_total} vehicles ({percentage:.1f}% of total)")
                    if zone_total > 10:
                        insights.append(f"High congestion density in zone '{zone_name}' with {zone_total} vehicles")
                    elif zone_total == 1:
                        insights.append(f"Low congestion in zone '{zone_name}'")
        
        if "per_category_count" in counting_summary:
            category_counts = counting_summary["per_category_count"]
            for category, count in category_counts.items():
                if count > 0 and category in config.target_vehicle_categories:
                    percentage = (count / total_vehicles) * 100
                    display_name = self.CATEGORY_DISPLAY.get(category, category)
                    insights.append(f"{display_name}: {count} detections ({percentage:.1f}% of total)")
        
        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            if unique_count is not None:
                insights.append(f"Unique vehicle count: {unique_count}")
                if unique_count != total_vehicles:
                    insights.append(f"Detection efficiency: {unique_count}/{total_vehicles} unique tracks")
        
        return insights
    
    def _check_alerts(self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig) -> List[Dict]:
        """Check for alert conditions and generate vehicle alerts."""
        alerts = []
        if not config.alert_config:
            return alerts
        
        total_vehicles = counting_summary.get("total_count", 0)
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')
        
        for category, threshold in config.alert_config.count_thresholds.items():
            if category == "all" and total_vehicles >= threshold:
                alerts.append({
                    "type": "count_threshold",
                    "severity": "warning",
                    "message": f"Total vehicle count ({total_vehicles}) exceeds threshold ({threshold})",
                    "category": category,
                    "current_count": total_vehicles,
                    "threshold": threshold,
                    "human_text": f"Time: {timestamp}\nTotal vehicle count ({total_vehicles}) exceeds threshold ({threshold})"
                })
            elif category in counting_summary.get("per_category_count", {}):
                count = counting_summary["per_category_count"][category]
                if count >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"{category} count ({count}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": count,
                        "threshold": threshold,
                        "human_text": f"Time: {timestamp}\n{category} count ({count}) exceeds threshold ({threshold})"
                    })
        
        for zone_name, threshold in config.alert_config.occupancy_thresholds.items():
            if zone_name in zone_analysis:
                zone_count = sum(zone_analysis[zone_name].values()) if isinstance(zone_analysis[zone_name], dict) else zone_analysis[zone_name]
                if zone_count >= threshold:
                    alerts.append({
                        "type": "occupancy_threshold",
                        "severity": "warning",
                        "message": f"Zone '{zone_name}' vehicle occupancy ({zone_count}) exceeds threshold ({threshold})",
                        "zone": zone_name,
                        "current_count": zone_count,
                        "threshold": threshold,
                        "human_text": f"Time: {timestamp}\nZone '{zone_name}' vehicle occupancy ({zone_count}) exceeds threshold ({threshold})"
                    })
        
        return alerts
    
    def _calculate_metrics(self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig, context: ProcessingContext) -> Dict[str, Any]:
        """Calculate detailed metrics for vehicle analytics."""
        total_vehicles = counting_summary.get("total_count", 0)
        metrics = {
            "total_vehicles": total_vehicles,
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
            "tracking_threshold": config.tracking_threshold,
            "zones_analyzed": len(zone_analysis),
            "detection_rate": (total_vehicles / config.time_window_minutes * 60) if config.time_window_minutes else 0,
            "coverage_percentage": 0.0,
            "total_unique_vehicles": sum(len(ids) for ids in self._vehicle_total_track_ids.values())
        }
        
        if zone_analysis and total_vehicles > 0:
            vehicles_in_zones = sum(
                sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                for zone_counts in zone_analysis.values()
            )
            metrics["coverage_percentage"] = (vehicles_in_zones / total_vehicles) * 100
        
        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            metrics["unique_vehicles"] = unique_count
            metrics["tracking_efficiency"] = (unique_count / total_vehicles) * 100 if total_vehicles > 0 else 0
        
        if zone_analysis:
            zone_metrics = {
                zone_name: {
                    "count": sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts,
                    "percentage": (sum(zone_counts.values()) / total_vehicles * 100) if total_vehicles > 0 else 0
                } for zone_name, zone_counts in zone_analysis.items()
            }
            metrics["zone_metrics"] = zone_metrics
        
        return metrics
    
    def _extract_predictions(self, data: Any) -> List[Dict[str, Any]]:
        """Extract predictions from processed data for API compatibility."""
        predictions = []
        try:
            if isinstance(data, list):
                for item in data:
                    prediction = self._normalize_prediction(item)
                    if prediction:
                        predictions.append(prediction)
            elif isinstance(data, dict):
                for frame_id, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            prediction = self._normalize_prediction(item)
                            if prediction:
                                prediction["frame_id"] = frame_id
                                predictions.append(prediction)
        except Exception as e:
            self.logger.warning(f"Failed to extract predictions: {e}")
        return predictions
    
    def _normalize_prediction(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a single prediction item."""
        if not isinstance(item, dict):
            return {}
        category = item.get("category", item.get("class", "unknown"))
        if str(category) == "0" or category == "human":
            self.logger.debug(f"Skipping human detection (category: {category})")
            return {}
        return {
            "category": category,
            "confidence": item.get("confidence", item.get("score", 0.0)),
            "bounding_box": item.get("bounding_box", item.get("bbox", {})),
            "track_id": item.get("track_id"),
            "frame_id": item.get("frame_id")
        }
    
    def _count_unique_tracks(self, counting_summary: Dict) -> int:
        """Count unique tracks in the current frame."""
        detections = counting_summary.get("detections", [])
        unique_tracks = {det.get("track_id") for det in detections if det.get("track_id") is not None}
        return len(unique_tracks)
    
    def _generate_summary(self, counting_summary: Dict, zone_analysis: Dict, alerts: List) -> str:
        """Generate human-readable summary."""
        total_vehicles = counting_summary.get("total_count", 0)
        lines = [f"{total_vehicles} vehicle(s) detected"] if total_vehicles else []
        per_cat = counting_summary.get("per_category_count", {})
        if per_cat:
            lines.append("vehicles:")
            for cat, count in per_cat.items():
                display = self.CATEGORY_DISPLAY.get(cat, cat)
                label = display.replace(" Vehicles", "").title()
                lines.append(f"\t{label}:{count}")
        if alerts:
            lines.append(f"{len(alerts)} alert(s)")
        return "\n".join(lines) if lines else "No vehicles detected"
    
    def _generate_events(self, counting_summary: Dict, zone_analysis: Dict, alerts: List, config: VehicleMonitoringConfig, frame_number: Optional[int] = None) -> List[Dict]:
        """Generate structured events for the output format with frame-based keys."""
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        events = [{frame_key: []}]
        frame_events = events[0][frame_key]
        total_vehicles = counting_summary.get("total_count", 0)
        
        if total_vehicles > 0:
            level = "info"
            intensity = 5.0
            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 15)
                intensity = min(10.0, (total_vehicles / threshold) * 10)
                if intensity >= 7:
                    level = "critical"
                elif intensity >= 5:
                    level = "warning"
            else:
                if total_vehicles > 25:
                    level = "critical"
                    intensity = 9.0
                elif total_vehicles > 15:
                    level = "warning"
                    intensity = 7.0
                else:
                    intensity = min(10.0, total_vehicles / 3.0)
            
            event = {
                "type": "vehicle_monitoring",
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": level,
                "intensity": round(intensity, 1),
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "Vehicle Monitoring System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"{total_vehicles} vehicles detected",
                "count": total_vehicles
            }
            frame_events.append(event)
        
        if zone_analysis:
            for zone_name, zone_count in zone_analysis.items():
                zone_total = sum(zone_count.values()) if isinstance(zone_count, dict) else zone_count
                if zone_total > 0:
                    zone_intensity = min(10.0, zone_total / 8.0)
                    zone_level = "info" if zone_intensity < 5 else "warning" if zone_intensity < 7 else "critical"
                    zone_event = {
                        "type": "congestion_zone_monitoring",
                        "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                        "level": zone_level,
                        "intensity": round(zone_intensity, 1),
                        "config": {
                            "min_value": 0,
                            "max_value": 10,
                            "level_settings": {"info": 2, "warning": 5, "critical": 7}
                        },
                        "application_name": "Congestion Zone Monitoring System",
                        "application_version": "1.2",
                        "location_info": zone_name,
                        "human_text": f"Event: Congestion Zone Monitoring\nLevel: {zone_level.title()}\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')}\nZone: {zone_name}\nCount: {zone_total} vehicles",
                        "count": zone_total
                    }
                    frame_events.append(zone_event)
        
        for alert in alerts:
            intensity_message = "Low congestion in the scene"
            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 15)
                percentage = (total_vehicles / threshold) * 100 if threshold > 0 else 0
                if percentage < 20:
                    intensity_message = "Low congestion in the scene"
                elif percentage <= 50:
                    intensity_message = "Moderate congestion in the scene"
                elif percentage <= 70:
                    intensity_message = "Heavy congestion in the scene"
                else:
                    intensity_message = "Severe congestion in the scene"
            else:
                if total_vehicles > 15:
                    intensity_message = "Heavy congestion in the scene"
                elif total_vehicles == 1:
                    intensity_message = "Low congestion in the scene"
                else:
                    intensity_message = "Moderate congestion in the scene"
            
            alert_event = {
                "type": alert.get("type", "congestion_alert"),
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": alert.get("severity", "warning"),
                "intensity": 8.0,
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "Congestion Alert System",
                "application_version": "1.2",
                "location_info": alert.get("zone"),
                "human_text": f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')} : {intensity_message}",
                "count": alert.get("current_count", alert.get("current_occupancy", 0))
            }
            frame_events.append(alert_event)
        
        return events
    
    def _generate_tracking_stats(self, vehicle_processed_data: List[Dict], zone_analysis: Dict, insights: List[str], summary: str, config: VehicleMonitoringConfig, frame_number: Optional[int] = None) -> List[Dict]:
        """Generate structured tracking stats for the output format with frame-based keys."""
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        tracking_stats = [{frame_key: []}]
        frame_tracking_stats = tracking_stats[0][frame_key]
        total_vehicles = len(vehicle_processed_data)
        
        if total_vehicles > 0 or zone_analysis:
            track_ids_info = self._get_track_ids_info(vehicle_processed_data, frame_number)
            counting_summary = self._count_categories(vehicle_processed_data, config)
            tracking_stat = {
                "type": "vehicle_tracking",
                "category": "traffic",
                "count": total_vehicles,
                "insights": insights,
                "summary": summary,
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC'),
                "human_text": self._generate_human_text_for_tracking(counting_summary, zone_analysis, insights, summary, config),
                "track_ids_info": track_ids_info,
                "global_frame_offset": self._global_frame_offset,
                "local_frame_id": frame_key,
                "all_results_for_tracking": {
                    "total_vehicles": total_vehicles,
                    "zone_analysis": zone_analysis,
                    "counting_summary": counting_summary,
                    "detection_rate": (total_vehicles / config.time_window_minutes) if config.time_window_minutes else 0,
                    "zones_count": len(zone_analysis) if zone_analysis else 0,
                    "unique_count": self._count_unique_tracks(counting_summary),
                    "congestion_flow_rate": (total_vehicles / config.time_window_minutes) if config.time_window_minutes else 0
                }
            }
            frame_tracking_stats.append(tracking_stat)
        
        return tracking_stats
    
    def _generate_human_text_for_tracking(self, counting_summary: Dict, zone_analysis: Dict, insights: List[str], summary: str, config: VehicleMonitoringConfig) -> str:
        """Generate human-readable text for tracking stats."""
        category_counts = counting_summary.get("per_category_count", {})
        if not category_counts:
            return "No vehicles detected"
        lines = ["vehicles:"]
        for category, count in category_counts.items():
            if count > 0 and category in config.target_vehicle_categories:
                display = self.CATEGORY_DISPLAY.get(category, category)
                label = display.replace(" Vehicles", "").title()
                if count == 1:
                    lines.append(f"\t{label}")
                else:
                    lines.append(f"\t{label}:{count}")
        return "\n".join(lines) if lines[1:] else "No vehicles detected"