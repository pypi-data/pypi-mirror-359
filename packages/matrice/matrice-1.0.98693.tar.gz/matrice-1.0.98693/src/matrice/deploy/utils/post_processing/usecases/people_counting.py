"""
People counting use case implementation.

This module provides a clean implementation of people counting functionality
with zone-based analysis, tracking, and alerting capabilities.
"""

from typing import Any, Dict, List, Optional
from dataclasses import asdict
import time

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol, ResultFormat
from ..core.config import PeopleCountingConfig, ZoneConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    filter_by_categories,
    apply_category_mapping,
    count_objects_by_category,
    count_objects_in_zones,
    calculate_counting_summary,
    match_results_structure
)
from ..utils.geometry_utils import get_bbox_center, point_in_polygon


class PeopleCountingUseCase(BaseProcessor):
    """People counting use case with zone analysis and alerting."""
    
    def __init__(self):
        """Initialize people counting use case."""
        super().__init__("people_counting")
        self.category = "general"
        
        # Track ID storage for total count calculation
        self._total_track_ids = set()  # Store all unique track IDs seen across calls
        self._current_frame_track_ids = set()  # Store track IDs from current frame
        self._total_count = 0  # Cached total count
        self._last_update_time = time.time()  # Track when last updated
        
        # Zone-based tracking storage
        self._zone_current_track_ids = {}  # zone_name -> set of current track IDs in zone
        self._zone_total_track_ids = {}  # zone_name -> set of all track IDs that have been in zone
        self._zone_current_counts = {}  # zone_name -> current count in zone
        self._zone_total_counts = {}  # zone_name -> total count that have been in zone
        
        # Frame counter for tracking total frames processed
        self._total_frame_counter = 0  # Total frames processed across all calls
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for people counting."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                    "description": "Minimum confidence threshold for detections"
                },
                "enable_tracking": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable tracking for unique counting"
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
                            "description": "Zone definitions as polygons"
                        },
                        "zone_confidence_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "description": "Per-zone confidence thresholds"
                        }
                    }
                },
                "person_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["person", "people"],
                    "description": "Category names that represent people"
                },
                "enable_unique_counting": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable unique people counting using tracking"
                },
                "time_window_minutes": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 60,
                    "description": "Time window for counting analysis in minutes"
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for alerts"
                        },
                        "occupancy_thresholds": {
                            "type": "object", 
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Zone occupancy thresholds for alerts"
                        }
                    }
                }
            },
            "required": ["confidence_threshold"],
            "additionalProperties": False
        }
    
    def create_default_config(self, **overrides) -> PeopleCountingConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "enable_tracking": False,
            "enable_analytics": True,
            "enable_unique_counting": True,
            "time_window_minutes": 60,
            "person_categories": ["person", "people"],
        }
        defaults.update(overrides)
        return PeopleCountingConfig(**defaults)
    
    def process(self, data: Any, config: ConfigProtocol, 
                context: Optional[ProcessingContext] = None) -> ProcessingResult:
        """
        Process people counting use case.
        
        Args:
            data: Raw model output (detection or tracking format)
            config: People counting configuration
            context: Processing context
            
        Returns:
            ProcessingResult: Processing result with people counting analytics
        """
        start_time = time.time()
        
        try:
            # Ensure we have the right config type
            if not isinstance(config, PeopleCountingConfig):
                return self.create_error_result(
                    "Invalid configuration type for people counting",
                    usecase=self.name,
                    category=self.category,
                    context=context
                )
            
            # Initialize processing context if not provided
            if context is None:
                context = ProcessingContext()
            
            # Detect input format
            input_format = match_results_structure(data)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold
            
            # Auto-cleanup expired tracks (optional - can be disabled)
            # if config.enable_tracking:
            #     self.clear_expired_tracks(max_age_seconds=300.0)  # 5 minutes default
            
            self.logger.info(f"Processing people counting with format: {input_format.value}")
            
            # Check if data is frame-based tracking format
            is_frame_based_tracking = (isinstance(data, dict) and 
                                     all(isinstance(k, (str, int)) for k in data.keys()) and
                                     input_format == ResultFormat.OBJECT_TRACKING)
            
            if is_frame_based_tracking:
                # Process frame-wise tracking data
                return self._process_frame_wise_tracking(data, config, context)
            else:
                # Process single frame or detection data (existing logic)
                return self._process_single_frame_data(data, config, context)
                
        except Exception as e:
            self.logger.error(f"People counting failed: {str(e)}", exc_info=True)
            
            if context:
                context.mark_completed()
            
            return self.create_error_result(
                str(e), 
                type(e).__name__,
                usecase=self.name,
                category=self.category,
                context=context
            )
    
    def _process_frame_wise_tracking(self, data: Dict, config: PeopleCountingConfig, context: ProcessingContext) -> ProcessingResult:
        """Process frame-wise tracking data to generate frame-specific events and tracking stats."""
        
        frame_events = {}
        frame_tracking_stats = {}
        all_events = []
        all_tracking_stats = []
        
        # Increment total frame counter
        frames_in_this_call = len(data)
        self._total_frame_counter += frames_in_this_call
        
        # Process each frame individually
        for frame_key, frame_detections in data.items():
            # Extract frame ID from tracking data
            frame_id = self._extract_frame_id_from_tracking(frame_detections, frame_key)
            
            # Process this single frame's detections
            frame_result = self._process_single_frame_detections(frame_detections, config, context)
            
            if frame_result.is_success():
                # Get events and tracking stats for this frame
                events = frame_result.data.get("events", [])
                tracking_stats = frame_result.data.get("tracking_stats", [])
                
                # Add frame_id to each event and tracking stat
                for event in events:
                    event["frame_id"] = frame_id
                
                for stat in tracking_stats:
                    stat["frame_id"] = frame_id
                    # Add frame processing stats at the beginning
                    stat["frames_in_this_call"] = frames_in_this_call
                    stat["total_frames_processed"] = self._total_frame_counter
                    stat["current_frame_number"] = frame_id
                
                # Store frame-wise results
                if events:  # Only add if events exist
                    frame_events[frame_id] = events
                    all_events.extend(events)
                
                frame_tracking_stats[frame_id] = tracking_stats
                all_tracking_stats.extend(tracking_stats)
        
        # Create comprehensive result with frame-wise structure
        result_data = {
            "events": frame_events,           # Frame-wise events
            "tracking_stats": frame_tracking_stats,  # Frame-wise tracking stats
            "all_events": all_events,         # All events combined
            "all_tracking_stats": all_tracking_stats,  # All tracking stats combined
            "total_count": self.get_total_count(),
            "zone_tracking": self.get_zone_tracking_info()
        }
        
        # Create result
        result = self.create_result(
            result_data,
            self.name,
            self.category,
            context
        )
        
        return result
    
    def _extract_frame_id_from_tracking(self, frame_detections: List[Dict], frame_key: str) -> str:
        """Extract frame ID from tracking data."""
        # Priority 1: Check if detections have frame information
        if frame_detections and len(frame_detections) > 0:
            first_detection = frame_detections[0]
            if "frame" in first_detection:
                return str(first_detection["frame"])
            elif "timestamp" in first_detection:
                return str(int(first_detection["timestamp"]))
        
        # Priority 2: Use frame_key from input data
        return str(frame_key)
    
    def _process_single_frame_detections(self, frame_detections: List[Dict], config: PeopleCountingConfig, context: ProcessingContext) -> ProcessingResult:
        """Process detections from a single frame using existing logic."""
        
        # Step 1: Apply confidence filtering to this frame
        if config.confidence_threshold is not None:
            frame_detections = [d for d in frame_detections if d.get("confidence", 0) >= config.confidence_threshold]
        
        # Step 2: Apply category mapping if provided
        if config.index_to_category:
            frame_detections = apply_category_mapping(frame_detections, config.index_to_category)
        
        # Step 3: Filter to person categories
        if config.person_categories:
            frame_detections = [d for d in frame_detections if d.get("category") in config.person_categories]
        
        # Step 4: Create counting summary for this frame
        counting_summary = {
            "total_objects": len(frame_detections),
            "detections": frame_detections,
            "categories": {}
        }
        
        # Count by category
        for detection in frame_detections:
            category = detection.get("category", "unknown")
            counting_summary["categories"][category] = counting_summary["categories"].get(category, 0) + 1
        
        # Step 5: Zone analysis for this frame
        zone_analysis = {}
        if config.zone_config and config.zone_config.zones:
            # Convert single frame to format expected by count_objects_in_zones
            frame_data = [frame_detections]  # Wrap in list for zone analysis
            zone_analysis = count_objects_in_zones(frame_data, config.zone_config.zones)
            
            # Update zone tracking with current frame data
            if zone_analysis and config.enable_tracking:
                enhanced_zone_analysis = self._update_zone_tracking(zone_analysis, frame_detections, config)
                # Merge enhanced zone analysis with original zone analysis
                for zone_name, enhanced_data in enhanced_zone_analysis.items():
                    zone_analysis[zone_name] = enhanced_data
        
        # Step 6: Generate insights and alerts for this frame
        insights = self._generate_insights(counting_summary, zone_analysis, config)
        alerts = self._check_alerts(counting_summary, zone_analysis, config)
        
        # Step 7: Generate events for this frame
        events = self._generate_events(counting_summary, zone_analysis, alerts, config)
        
        # Step 8: Generate tracking stats for this frame
        summary = self._generate_summary(counting_summary, zone_analysis, alerts)
        tracking_stats = self._generate_tracking_stats(counting_summary, zone_analysis, insights, summary, config)
        
        return self.create_result(
            data={
                "events": events,
                "tracking_stats": tracking_stats,
                "counting_summary": counting_summary,
                "zone_analysis": zone_analysis
            },
            usecase=self.name,
            category=self.category,
            context=context
        )
    
    def _process_single_frame_data(self, data: Any, config: PeopleCountingConfig, context: ProcessingContext) -> ProcessingResult:
        """Process single frame data (existing logic unchanged)."""
        start_time = time.time()
        
        try:
            # Step 1: Apply confidence filtering
            processed_data = data
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(processed_data, config.confidence_threshold)
                self.logger.debug(f"Applied confidence filtering with threshold {config.confidence_threshold}")
            
            # Step 2: Apply category mapping if provided
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied category mapping")
            
            # Step 2.5: Filter to only include person categories
            person_processed_data = processed_data
            if config.person_categories:
                person_processed_data = filter_by_categories(processed_data.copy(), config.person_categories)
                self.logger.debug(f"Applied person category filtering for: {config.person_categories}")
            
            # Step 3: Calculate comprehensive counting summary
            zones = config.zone_config.zones if config.zone_config else None
            person_counting_summary = calculate_counting_summary(
                person_processed_data,
                zones=zones
            )
            general_counting_summary = calculate_counting_summary(
                processed_data,
                zones=zones
            )
            
            # Step 4: Zone-based analysis if zones are configured
            zone_analysis = {}
            if config.zone_config and config.zone_config.zones:
                zone_analysis = count_objects_in_zones(
                    person_processed_data, 
                    config.zone_config.zones
                )
                self.logger.debug(f"Analyzed {len(config.zone_config.zones)} zones")
                
                # Step 4.5: Update zone tracking with current frame data
                if zone_analysis and config.enable_tracking:
                    detections = self._get_detections_with_confidence(person_counting_summary)
                    enhanced_zone_analysis = self._update_zone_tracking(zone_analysis, detections, config)
                    # Merge enhanced zone analysis with original zone analysis
                    for zone_name, enhanced_data in enhanced_zone_analysis.items():
                        zone_analysis[zone_name] = enhanced_data
            
            # Step 5: Generate insights and alerts
            insights = self._generate_insights(person_counting_summary, zone_analysis, config)
            alerts = self._check_alerts(person_counting_summary, zone_analysis, config)
            
            # Step 6: Calculate detailed metrics
            metrics = self._calculate_metrics(person_counting_summary, zone_analysis, config, context)
            
            # Step 7: Extract predictions for API compatibility
            predictions = self._extract_predictions(processed_data)
            
            # Step 8: Generate human-readable summary
            summary = self._generate_summary(person_counting_summary, zone_analysis, alerts)
            
            # Step 9: Generate structured events and tracking stats
            events = self._generate_events(person_counting_summary, zone_analysis, alerts, config)
            tracking_stats = self._generate_tracking_stats(person_counting_summary, zone_analysis, insights, summary, config)
            
            # Mark processing as completed
            context.mark_completed()
            
            # Create successful result
            result = self.create_result(
                data={
                    "general_counting_summary": general_counting_summary,
                    "counting_summary": person_counting_summary,
                    "zone_analysis": zone_analysis,
                    "alerts": alerts,
                    "total_people": person_counting_summary.get("total_objects", 0),
                    "zones_count": len(config.zone_config.zones) if config.zone_config else 0,
                    "events": events,
                    "tracking_stats": tracking_stats
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            
            # Add human-readable information
            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics
            
            # Add warnings for low confidence detections
            if config.confidence_threshold and config.confidence_threshold < 0.3:
                result.add_warning(f"Low confidence threshold ({config.confidence_threshold}) may result in false positives")
            
            processing_time = context.processing_time or time.time() - start_time
            self.logger.info(f"People counting completed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"People counting failed: {str(e)}", exc_info=True)
            
            if context:
                context.mark_completed()
            
            return self.create_error_result(
                str(e), 
                type(e).__name__,
                usecase=self.name,
                category=self.category,
                context=context
            )
    
    def _generate_insights(self, counting_summary: Dict, zone_analysis: Dict, 
                          config: PeopleCountingConfig) -> List[str]:
        """Generate human-readable insights from counting results."""
        insights = []
        
        total_people = counting_summary.get("total_objects", 0)
        
        if total_people == 0:
            insights.append("No people detected in the scene")
            return insights
        
        # Basic count insight
        insights.append(f"EVENT : Detected {total_people} people in the scene")
        
        # Intensity calculation based on threshold percentage
        intensity_threshold = None
        if (config.alert_config and 
            config.alert_config.count_thresholds and 
            "all" in config.alert_config.count_thresholds):
            intensity_threshold = config.alert_config.count_thresholds["all"]
        
        if intensity_threshold is not None:
            # Calculate percentage relative to threshold
            percentage = (total_people / intensity_threshold) * 100
            
            if percentage < 20:
                insights.append(f"INTENSITY: Low occupancy in the scene ({percentage:.1f}% of capacity)")
            elif percentage <= 50:
                insights.append(f"INTENSITY: Medium occupancy in the scene ({percentage:.1f}% of capacity)")
            elif percentage <= 70:
                insights.append(f"INTENSITY: High occupancy in the scene ({percentage:.1f}% of capacity)")
            else:
                insights.append(f"INTENSITY: Very high density in the scene ({percentage:.1f}% of capacity)")
        else:
            # Fallback to hardcoded thresholds if no alert config is set
            if total_people > 10:
                insights.append(f"INTENSITY: High density in the scene with {total_people} people")
            elif total_people == 1:
                insights.append("INTENSITY: Low occupancy in the scene")
        
        # Zone-specific insights
        if zone_analysis:
            for zone_name, zone_counts in zone_analysis.items():
                zone_total = sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                if zone_total > 0:
                    percentage = (zone_total / total_people) * 100
                    insights.append(f"Zone '{zone_name}': {zone_total} people")
                    
                    # # Density insights
                    # if zone_total > 10:
                    #     insights.append(f"High density in zone '{zone_name}' with {zone_total} people")
                    # elif zone_total == 1:
                    #     insights.append(f"Low occupancy in zone '{zone_name}'")
        
        # Category breakdown insights
        if "by_category" in counting_summary:
            category_counts = counting_summary["by_category"]
            for category, count in category_counts.items():
                if count > 0 and category in config.person_categories:
                    percentage = (count / total_people) * 100
                    insights.append(f"Category '{category}': {count} detections")
        
        # Time-based insights
        if config.time_window_minutes:
            rate_per_hour = (total_people / config.time_window_minutes) * 60
            insights.append(f"Detection rate: {rate_per_hour:.1f} people per hour")
        
        # Unique counting insights
        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            if unique_count is not None:
                insights.append(f"Unique people count: {unique_count}")
                if unique_count != total_people:
                    insights.append(f"Detection efficiency: {unique_count}/{total_people} unique tracks")
        
        return insights
    
    def _check_alerts(self, counting_summary: Dict, zone_analysis: Dict, 
                     config: PeopleCountingConfig) -> List[Dict]:
        """Check for alert conditions and generate alerts."""
        alerts = []
        
        if not config.alert_config:
            return alerts
        
        total_people = counting_summary.get("total_objects", 0)
        
        # Count threshold alerts
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total_people >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"Total people count ({total_people}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": total_people,
                        "threshold": threshold
                    })
                elif category in counting_summary.get("by_category", {}):
                    count = counting_summary["by_category"][category]
                    if count >= threshold:
                        alerts.append({
                            "type": "count_threshold",
                            "severity": "warning",
                            "message": f"{category} count ({count}) exceeds threshold ({threshold})",
                            "category": category,
                            "current_count": count,
                            "threshold": threshold
                        })
        
        # Zone occupancy threshold alerts
        if config.alert_config.occupancy_thresholds:
            for zone_name, threshold in config.alert_config.occupancy_thresholds.items():
                if zone_name in zone_analysis:
                    zone_count = sum(zone_analysis[zone_name].values()) if isinstance(zone_analysis[zone_name], dict) else zone_analysis[zone_name]
                    if zone_count >= threshold:
                        alerts.append({
                            "type": "occupancy_threshold",
                            "severity": "warning",
                            "message": f"Zone '{zone_name}' occupancy ({zone_count}) exceeds threshold ({threshold})",
                            "zone": zone_name,
                            "current_occupancy": zone_count,
                            "threshold": threshold
                        })
        
        return alerts
    
    def _calculate_metrics(self, counting_summary: Dict, zone_analysis: Dict, 
                          config: PeopleCountingConfig, context: ProcessingContext) -> Dict[str, Any]:
        """Calculate detailed metrics for analytics."""
        total_people = counting_summary.get("total_objects", 0)
        
        metrics = {
            "total_people": total_people,
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
            "zones_analyzed": len(zone_analysis),
            "detection_rate": 0.0,
            "coverage_percentage": 0.0
        }
        
        # Calculate detection rate
        if config.time_window_minutes and config.time_window_minutes > 0:
            metrics["detection_rate"] = (total_people / config.time_window_minutes) * 60
        
        # Calculate zone coverage
        if zone_analysis and total_people > 0:
            people_in_zones = sum(
                sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                for zone_counts in zone_analysis.values()
            )
            metrics["coverage_percentage"] = (people_in_zones / total_people) * 100
        
        # Unique tracking metrics
        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            if unique_count is not None:
                metrics["unique_people"] = unique_count
                metrics["tracking_efficiency"] = (unique_count / total_people) * 100 if total_people > 0 else 0
        
        # Per-zone metrics
        if zone_analysis:
            zone_metrics = {}
            for zone_name, zone_counts in zone_analysis.items():
                zone_total = sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                zone_metrics[zone_name] = {
                    "count": zone_total,
                    "percentage": (zone_total / total_people) * 100 if total_people > 0 else 0
                }
            metrics["zone_metrics"] = zone_metrics
        
        return metrics
    
    def _extract_predictions(self, data: Any) -> List[Dict[str, Any]]:
        """Extract predictions from processed data for API compatibility."""
        predictions = []
        
        try:
            if isinstance(data, list):
                # Detection format
                for item in data:
                    prediction = self._normalize_prediction(item)
                    if prediction:
                        predictions.append(prediction)
            
            elif isinstance(data, dict):
                # Frame-based or tracking format
                for frame_id, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            prediction = self._normalize_prediction(item)
                            if prediction:
                                prediction["frame_id"] = frame_id
                                predictions.append(prediction)
        
        except Exception as e:
            self.logger.warning(f"Failed to extract predictions: {str(e)}")
        
        return predictions
    
    def _normalize_prediction(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a single prediction item."""
        if not isinstance(item, dict):
            return {}
        
        return {
            "category": item.get("category", item.get("class", "unknown")),
            "confidence": item.get("confidence", item.get("score", 0.0)),
            "bounding_box": item.get("bounding_box", item.get("bbox", {})),
            "track_id": item.get("track_id")
        }
    
    def _get_detections_with_confidence(self, counting_summary: Dict) -> List[Dict]:
        """Extract detection items with confidence scores."""
        return counting_summary.get("detections", [])
    
    def _count_unique_tracks(self, counting_summary: Dict) -> Optional[int]:
        """Count unique tracks if tracking is enabled."""
        detections = self._get_detections_with_confidence(counting_summary)
        
        if not detections:
            return self._total_count if self._total_count > 0 else None
        
        # Get current frame track IDs
        current_frame_tracks = set()
        for detection in detections:
            track_id = detection.get("track_id")
            if track_id is not None:
                current_frame_tracks.add(track_id)
        
        # Update total track IDs with new ones from current frame
        self._total_track_ids.update(current_frame_tracks)
        self._current_frame_track_ids = current_frame_tracks
        
        # Update total count
        self._total_count = len(self._total_track_ids)
        self._last_update_time = time.time()
        
        return self._total_count
    
    def get_total_count(self) -> int:
        """Get the total count of unique people tracked across all calls."""
        return self._total_count
    
    def get_current_frame_count(self) -> int:
        """Get the count of people in the current frame."""
        return len(self._current_frame_track_ids)
    
    def get_total_frames_processed(self) -> int:
        """Get the total number of frames processed across all calls."""
        return self._total_frame_counter
    
    def get_track_ids_info(self) -> Dict[str, Any]:
        """Get detailed information about track IDs."""
        return {
            "total_count": self._total_count,
            "current_frame_count": len(self._current_frame_track_ids),
            "total_unique_track_ids": len(self._total_track_ids),
            "current_frame_track_ids": list(self._current_frame_track_ids),
            "last_update_time": self._last_update_time,
            "total_frames_processed": self._total_frame_counter
        }
    
    def reset_tracking_state(self) -> None:
        """Reset the tracking state (clear all stored track IDs)."""
        self._total_track_ids.clear()
        self._current_frame_track_ids.clear()
        self._total_count = 0
        self._last_update_time = time.time()
        
        # Clear zone tracking data
        self._zone_current_track_ids.clear()
        self._zone_total_track_ids.clear()
        self._zone_current_counts.clear()
        self._zone_total_counts.clear()
        
        # Reset frame counter
        self._total_frame_counter = 0
        
        self.logger.info("Tracking state reset - all track IDs, zone data, and frame counter cleared")
    
    def reset_frame_counter(self) -> None:
        """Reset only the frame counter."""
        old_count = self._total_frame_counter
        self._total_frame_counter = 0
        self.logger.info(f"Frame counter reset from {old_count} to 0")
    
    def clear_expired_tracks(self, max_age_seconds: float = 300.0) -> int:
        """
        Clear track IDs that haven't been seen for a while.
        
        Args:
            max_age_seconds: Maximum age in seconds before clearing tracks
            
        Returns:
            Number of tracks cleared
        """
        current_time = time.time()
        if current_time - self._last_update_time > max_age_seconds:
            old_count = len(self._total_track_ids)
            self.reset_tracking_state()
            cleared_count = old_count
            self.logger.info(f"Cleared {cleared_count} expired tracks (age > {max_age_seconds}s)")
            return cleared_count
        return 0
    
    def _update_zone_tracking(self, zone_analysis: Dict[str, Dict[str, int]], detections: List[Dict], config: PeopleCountingConfig) -> Dict[str, Dict[str, Any]]:
        """
        Update zone tracking with current frame data.
        
        Args:
            zone_analysis: Current zone analysis results
            detections: List of detections with track IDs
            config: People counting configuration with zone polygons
            
        Returns:
            Enhanced zone analysis with tracking information
        """
        if not zone_analysis or not config.zone_config or not config.zone_config.zones:
            return {}
        
        enhanced_zone_analysis = {}
        zones = config.zone_config.zones
        
        # Get current frame track IDs in each zone
        current_frame_zone_tracks = {}
        
        # Initialize zone tracking for all zones
        for zone_name in zones.keys():
            current_frame_zone_tracks[zone_name] = set()
            if zone_name not in self._zone_current_track_ids:
                self._zone_current_track_ids[zone_name] = set()
            if zone_name not in self._zone_total_track_ids:
                self._zone_total_track_ids[zone_name] = set()
        
        # Check each detection against each zone
        for detection in detections:
            track_id = detection.get("track_id")
            if track_id is None:
                continue
            
            # Get detection bbox
            bbox = detection.get("bounding_box", detection.get("bbox"))
            if not bbox:
                continue
            
            # Get detection center point
            center_point = get_bbox_center(bbox)
            
            # Check which zone this detection is in using actual zone polygons
            for zone_name, zone_polygon in zones.items():
                # Convert polygon points to tuples for point_in_polygon function
                # zone_polygon format: [[x1, y1], [x2, y2], [x3, y3], ...]
                polygon_points = [(point[0], point[1]) for point in zone_polygon]
                
                # Check if detection center is inside the zone polygon using ray casting algorithm
                if point_in_polygon(center_point, polygon_points):
                    current_frame_zone_tracks[zone_name].add(track_id)
        
        # Update zone tracking for each zone
        for zone_name, zone_counts in zone_analysis.items():
            # Get current frame tracks for this zone
            current_tracks = current_frame_zone_tracks.get(zone_name, set())
            
            # Update current zone tracks
            self._zone_current_track_ids[zone_name] = current_tracks
            
            # Update total zone tracks (accumulate all track IDs that have been in this zone)
            self._zone_total_track_ids[zone_name].update(current_tracks)
            
            # Update counts
            self._zone_current_counts[zone_name] = len(current_tracks)
            self._zone_total_counts[zone_name] = len(self._zone_total_track_ids[zone_name])
            
            # Create enhanced zone analysis
            enhanced_zone_analysis[zone_name] = {
                "current_count": self._zone_current_counts[zone_name],
                "total_count": self._zone_total_counts[zone_name],
                "current_track_ids": list(current_tracks),
                "total_track_ids": list(self._zone_total_track_ids[zone_name]),
                "original_counts": zone_counts  # Preserve original zone counts
            }
        
        return enhanced_zone_analysis
    
    def get_zone_tracking_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed zone tracking information."""
        return {
            zone_name: {
                "current_count": self._zone_current_counts.get(zone_name, 0),
                "total_count": self._zone_total_counts.get(zone_name, 0),
                "current_track_ids": list(self._zone_current_track_ids.get(zone_name, set())),
                "total_track_ids": list(self._zone_total_track_ids.get(zone_name, set()))
            }
            for zone_name in set(self._zone_current_counts.keys()) | set(self._zone_total_counts.keys())
        }
    
    def get_zone_current_count(self, zone_name: str) -> int:
        """Get current count of people in a specific zone."""
        return self._zone_current_counts.get(zone_name, 0)
    
    def get_zone_total_count(self, zone_name: str) -> int:
        """Get total count of people who have been in a specific zone."""
        return self._zone_total_counts.get(zone_name, 0)
    
    def get_all_zone_counts(self) -> Dict[str, Dict[str, int]]:
        """Get current and total counts for all zones."""
        return {
            zone_name: {
                "current": self._zone_current_counts.get(zone_name, 0),
                "total": self._zone_total_counts.get(zone_name, 0)
            }
            for zone_name in set(self._zone_current_counts.keys()) | set(self._zone_total_counts.keys())
        }
    
    def _generate_summary(self, counting_summary: Dict, zone_analysis: Dict, alerts: List) -> str:
        """Generate human-readable summary."""
        total_people = counting_summary.get("total_objects", 0)
        
        if total_people == 0:
            return "No people detected in the scene"
        
        summary_parts = [f"{total_people} people detected"]
        
        if zone_analysis:
            zones_with_people = sum(1 for zone_counts in zone_analysis.values() 
                                  if (sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts) > 0)
            summary_parts.append(f"across {zones_with_people}/{len(zone_analysis)} zones")
        
        if alerts:
            alert_count = len(alerts)
            summary_parts.append(f"with {alert_count} alert{'s' if alert_count != 1 else ''}")
        
        return ", ".join(summary_parts)
    
    def _generate_events(self, counting_summary: Dict, zone_analysis: Dict, alerts: List, config: PeopleCountingConfig) -> List[Dict]:
        """Generate structured events for the output format."""
        from datetime import datetime, timezone
        
        events = []
        total_people = counting_summary.get("total_objects", 0)
        
        if total_people > 0:
            # Determine event level based on thresholds
            level = "info"
            intensity = 5.0
            
            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 10)
                intensity = min(10.0, (total_people / threshold) * 10)
                
                if intensity >= 7:
                    level = "critical"
                elif intensity >= 5:
                    level = "warning"
                else:
                    level = "info"
            else:
                if total_people > 20:
                    level = "critical"
                    intensity = 9.0
                elif total_people > 10:
                    level = "warning" 
                    intensity = 7.0
                else:
                    level = "info"
                    intensity = min(10.0, total_people / 2.0)
            
            # Main people counting event
            event = {
                "type": "people_counting",
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": level,
                "intensity": round(intensity, 1),
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "People Counting System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"Event: People Counting\nCount: {total_people} people detected"
            }
            events.append(event)
        
        # Add zone-specific events if applicable
        if zone_analysis:
            for zone_name, zone_count in zone_analysis.items():
                if isinstance(zone_count, dict):
                    zone_total = sum(zone_count.values())
                else:
                    zone_total = zone_count
                
                if zone_total > 0:
                    zone_intensity = min(10.0, zone_total / 5.0)
                    zone_level = "info"
                    if zone_intensity >= 7:
                        zone_level = "warning"
                    elif zone_intensity >= 5:
                        zone_level = "info"
                    
                    zone_event = {
                        "type": "zone_occupancy",
                        "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                        "level": zone_level,
                        "intensity": round(zone_intensity, 1),
                        "config": {
                            "min_value": 0,
                            "max_value": 10,
                            "level_settings": {"info": 2, "warning": 5, "critical": 7}
                        },
                        "application_name": "Zone Monitoring System",
                        "application_version": "1.2",
                        "location_info": zone_name,
                        "human_text": f"Event: Zone Occupancy\nZone: {zone_name}\nCount: {zone_total} people"
                    }
                    events.append(zone_event)
        
        # Add alert events
        for alert in alerts:
            alert_event = {
                "type": alert.get("type", "alert"),
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": alert.get("severity", "warning"),
                "intensity": 8.0,
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "Alert System",
                "application_version": "1.2",
                "location_info": alert.get("zone"),
                "human_text": 'Alert triggered'
            }
            events.append(alert_event)
        
        return events
    
    def _generate_tracking_stats(self, counting_summary: Dict, zone_analysis: Dict, insights: List[str], summary: str, config: PeopleCountingConfig) -> List[Dict]:
        """Generate structured tracking stats for the output format."""
        from datetime import datetime, timezone
        
        tracking_stats = []
        total_people = counting_summary.get("total_objects", 0)
        
        if total_people > 0 or zone_analysis:
            # Get total count from cached tracking state
            total_unique_count = self.get_total_count()
            current_frame_count = self.get_current_frame_count()
            
            # Get zone tracking information
            zone_tracking_info = self.get_zone_tracking_info()
            
            # Create main tracking stats entry
            tracking_stat = {
                "tracking_start_time": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "all_results_for_tracking": {
                    "total_people": total_people,
                    "zone_analysis": zone_analysis,
                    "counting_summary": counting_summary,
                    "detection_rate": (total_people / config.time_window_minutes * 60) if config.time_window_minutes else 0,
                    "zones_count": len(zone_analysis) if zone_analysis else 0,
                    "unique_count": self._count_unique_tracks(counting_summary),
                    "total_unique_count": total_unique_count,  # Total across all calls
                    "current_frame_count": current_frame_count,  # Current frame only
                    "track_ids_info": self.get_track_ids_info(),  # Detailed track info
                    "zone_tracking_info": zone_tracking_info  # Zone tracking information
                },
                "human_text": self._generate_human_text_for_tracking(total_people, zone_analysis, insights, summary, config)
            }
            tracking_stats.append(tracking_stat)
        
        return tracking_stats
    
    def _generate_human_text_for_tracking(self, total_people: int, zone_analysis: Dict, insights: List[str], summary: str, config: PeopleCountingConfig) -> str:
        """Generate human-readable text for tracking stats."""
        from datetime import datetime, timezone
        
        text_parts = [
            f"Tracking Start Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            f"People Detected: {total_people}"
        ]
        
        # Add total count information
        total_unique_count = self.get_total_count()
        current_frame_count = self.get_current_frame_count()
        
        if total_unique_count > 0:
            text_parts.append(f"Total Unique People: {total_unique_count}")
        
        # Add zone tracking information
        zone_tracking_info = self.get_zone_tracking_info()
        if zone_tracking_info:
            text_parts.append(f"Zone Tracking:")
            for zone_name, zone_info in zone_tracking_info.items():
                current_count = zone_info.get("current_count", 0)
                total_count = zone_info.get("total_count", 0)
                if current_count > 0 or total_count > 0:
                    text_parts.append(f"  {zone_name}: Current={current_count}, Total={total_count}")
        
        if zone_analysis:
            text_parts.append(f"Zones Analyzed: {len(zone_analysis)}")
            for zone_name, zone_count in zone_analysis.items():
                if isinstance(zone_count, dict):
                    zone_total = sum(zone_count.values())
                else:
                    zone_total = zone_count
                
                if zone_total > 0:
                    text_parts.append(f"Zone {zone_name}: {zone_total} people")
        
        return "\n".join(text_parts) 