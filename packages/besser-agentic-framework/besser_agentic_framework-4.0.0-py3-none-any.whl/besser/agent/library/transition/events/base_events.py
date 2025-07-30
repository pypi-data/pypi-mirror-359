import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

from besser.agent.core.file import File
from besser.agent.core.message import Message, MessageType
from besser.agent.core.transition.event import Event
from besser.agent.exceptions.logger import logger
from besser.agent.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

if TYPE_CHECKING:
    from besser.agent.core.session import Session


class DummyEvent(Event):
    """Represents a placeholder event."""

    def __init__(self):
        super().__init__(name='dummy_event', timestamp=datetime.now())


class WildcardEvent(Event):
    """Wildcard event. Can be used to match any event in a transition."""

    def __init__(self):
        super().__init__(name='any_event', timestamp=datetime.now())

    def is_matching(self, event: 'Event') -> bool:
        """Check whether an event matches another one.

        Args:
            event (Event): the target event to compare

        Returns:
            bool: always true
        """
        if isinstance(event, Event):
            return True


class ReceiveMessageEvent(Event):
    """Base event for receiving messages.

    Args:
        message (str): the received message content
        session_id (str): the id of the session the event was sent to (can be none)
        human (bool): indicates if the sender is human. Defaults to True

    Attributes:
        message (str): the received message content
        human (bool): indicates if the sender is human. Defaults to True
    """

    @staticmethod
    def create_event_from(message: str = None, session: 'Session' = None, human: bool = True) -> 'ReceiveMessageEvent':
        """Creates an event from a received message, determining if it's JSON or text.

        Args:
            message (str): the received message content
            session (Session): the current session
            human (bool): indicates if the sender is human. Defaults to True

        Returns:
            ReceiveMessageEvent: a specific event instance based on message type.
        """
        event = None
        if session is None:
            session_id = None
        else:
            session_id = session.id
        message = session._agent.process(session=session, message=message, is_user_message=human)
        try:
            payload = json.loads(message)
            event = ReceiveJSONEvent(payload, session_id, human)
        except json.JSONDecodeError:
            event = ReceiveTextEvent(message, session_id, human)
        finally:
            return event

    def __init__(self, message: Any = None, session_id: str = None, human: bool = True):
        super().__init__(name='receive_message', session_id=session_id, timestamp=datetime.now())
        self.message: Any = message
        self.human: bool = human

    def is_matching(self, event: 'Event') -> bool:
        if isinstance(event, self.__class__):
            return event._name.startswith(self._name)


class ReceiveTextEvent(ReceiveMessageEvent):
    """Event for receiving text messages. Supports intent prediction.

    Args:
        text (str): the received message content
        session_id (str): the id of the session the event was sent to (can be none)
        human (bool): indicates if the sender is human. Defaults to True

    Attributes:
        _name (str): the name of the event
        predicted_intent (IntentClassifierPrediction): the predicted intent for the event message
    """

    def __init__(self, text: str = None, session_id: str = None, human: bool = False):
        super().__init__(message=text, session_id=session_id, human=human)
        self._name = 'receive_message_text'
        self.predicted_intent: IntentClassifierPrediction = None

    def log(self):
        return f'{self._name} ({self.message})'

    def predict_intent(self, session: 'Session') -> None:
        """Predict the intent of the event message, only if it has not been done yet or if the session moved to another
        agent state.

        Args:
            session (Session): the user session
        """
        if self.predicted_intent is None or self.predicted_intent.state != session.current_state.name:
            self.predicted_intent = session._agent._nlp_engine.predict_intent(session)
            logger.info(f'Detected intent: {self.predicted_intent.intent.name}')
            for parameter in self.predicted_intent.matched_parameters:
                logger.info(f"Parameter '{parameter.name}': {parameter.value}, info = {parameter.info}")


class ReceiveJSONEvent(ReceiveMessageEvent):
    """Event for receiving JSON messages.

    Args:
        payload (dict): the received message content
        session_id (str): the id of the session the event was sent to (can be none)
        human (bool): indicates if the sender is human. Defaults to False

    Attributes:
        _name (str): the name of the event
    """

    def __init__(self, payload: dict = None, session_id: str = None, human: bool = False):
        if payload is None:
            payload = {}
        super().__init__(message=json.dumps(payload), session_id=session_id, human=human)
        self._name = 'receive_message_json'


class ReceiveFileEvent(Event):
    """Event for receiving files.

    Args:
        file (File): the received file
        session_id (str): the id of the session the event was sent to (can be none)
        human (bool): indicates if the sender is human. Defaults to True

    Attributes:
        file (File): the received file
        human (bool): indicates if the sender is human. Defaults to True
    """

    def __init__(self, file: File = None, session_id: str = None, human: bool = True):
        super().__init__(name='receive_file', session_id=session_id, timestamp=datetime.now())
        self.file: File = file
        self.human: bool = human
