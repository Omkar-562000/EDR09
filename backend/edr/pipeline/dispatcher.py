from __future__ import annotations

from backend.edr.database.storage import Storage
from backend.edr.detection.engine import DetectionEngine
from backend.edr.models import Event
from backend.edr.response.engine import ResponseEngine


class Dispatcher:
    def __init__(
        self,
        storage: Storage,
        detection_engine: DetectionEngine,
        response_engine: ResponseEngine,
    ) -> None:
        self.storage = storage
        self.detection_engine = detection_engine
        self.response_engine = response_engine

    def dispatch(self, event: Event) -> None:
        self.storage.log_event(event)
        detections = self.detection_engine.evaluate(event)
        for detection in detections:
            self.storage.log_detection(detection)
            actions = self.response_engine.execute(detection)
            for action in actions:
                self.storage.log_action(action)
