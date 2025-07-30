"""
The collection of preexisting condition functions.

Functions embedded in :class:`~besser.agent.core.transition.condition.Condition` that, when called and return a `True`
value, trigger the transitions.
"""

from typing import Any, Callable, TYPE_CHECKING

from besser.agent.core.intent.intent import Intent

if TYPE_CHECKING:
    from besser.agent.core.session import Session


def intent_matched(session: 'Session', params: dict) -> bool:
    """This function checks if 2 intents are the same, used for intent matching checking.

    Args:
        session (Session): the current user session
        params (dict): the function parameters

    Returns:
        bool: True if the 2 intents are the same, false otherwise
    """
    target_intent: Intent = params['intent']
    predicted_intent = session.event.predicted_intent
    if predicted_intent is not None:
        matched_intent: Intent = predicted_intent.intent
        return target_intent.name == matched_intent.name
    return False


def variable_matches_operation(session: 'Session', params: dict) -> bool:
    """This function checks if for a specific comparison operation, using a stored session value
    and a given target value, returns true.

    Args:
        session (Session): the current user session
        params (dict): the function parameters

    Returns:
        bool: True if the comparison operation of the given values returns true
    """
    var_name: str = params['var_name']
    target_value: Any = params['target']
    operation: Callable[[Any, Any], bool] = params['operation']
    current_value: Any = session.get(var_name)
    return operation(current_value, target_value)


def file_type(session: 'Session', params: dict) -> bool:
    """This function only returns True if a user sent a file of an allowed type.

    Args:
        session (Session): the current user session
        params (dict): the function parameters

    Returns:
        bool: True if the user has sent a file and the received file type corresponds to the allowed
        types as defined in "allowed_types"
    """
    if "allowed_types" in params.keys():
        if session.event.file.type in params["allowed_types"] or session.event.file.type == params["allowed_types"]:
            return True
        return False
    return True
