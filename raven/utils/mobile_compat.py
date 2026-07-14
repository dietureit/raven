import json

import frappe


def as_mobile_string(value) -> str:
	"""Coerce API values to strings for legacy Raven mobile clients."""
	if value is None:
		return ""
	if isinstance(value, str):
		return value
	return str(value)


def sanitize_preview_data(preview_data: dict | None) -> dict | None:
	"""
	Ensure document preview fields are strings.

	Legacy Raven mobile calls .replace() on preview values; numbers crash Hermes.
	"""
	if not preview_data:
		return preview_data

	return {key: as_mobile_string(val) for key, val in preview_data.items()}


def sanitize_message_reactions(reactions) -> str | None:
	"""Normalize reaction JSON so mobile clients always get a users array."""
	if not reactions:
		return None

	if isinstance(reactions, str):
		try:
			data = json.loads(reactions)
		except (json.JSONDecodeError, TypeError):
			return None
	elif isinstance(reactions, dict):
		data = reactions
	else:
		return None

	if not isinstance(data, dict):
		return None

	sanitized = {}
	for key, value in data.items():
		if not isinstance(value, dict):
			continue

		users = value.get("users")
		if not isinstance(users, list):
			users = []

		count = value.get("count")
		if not isinstance(count, int):
			count = len(users)

		sanitized[key] = {
			**value,
			"reaction": value.get("reaction") or key,
			"users": users,
			"count": count,
		}

	return json.dumps(sanitized) if sanitized else None


def sanitize_message_for_mobile(message: dict | None) -> dict | None:
	"""Normalize a Raven message payload for legacy mobile clients."""
	if not message:
		return message

	sanitized = dict(message)

	if sanitized.get("hide_link_preview") is None:
		sanitized["hide_link_preview"] = 0

	if sanitized.get("is_bot_message") is None:
		sanitized["is_bot_message"] = 0

	if "message_reactions" in sanitized:
		sanitized["message_reactions"] = sanitize_message_reactions(sanitized.get("message_reactions"))

	if sanitized.get("content") is not None:
		sanitized["content"] = as_mobile_string(sanitized.get("content"))

	return sanitized


def sanitize_messages_for_mobile(messages: list[dict] | None) -> list[dict]:
	if not messages:
		return messages or []

	return [sanitize_message_for_mobile(message) for message in messages]
