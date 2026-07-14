import frappe


def execute():
	"""Ensure Raven Channel has standard Frappe columns used by desk list joins."""
	standard_columns = {
		"owner": "varchar(140)",
		"creation": "datetime(6)",
		"modified": "datetime(6)",
		"modified_by": "varchar(140)",
		"docstatus": "int(1) not null default 0",
		"idx": "int(8) not null default 0",
		"_user_tags": "text",
		"_comments": "text",
		"_assign": "text",
		"_liked_by": "text",
	}

	for column, definition in standard_columns.items():
		if not frappe.db.has_column("Raven Channel", column):
			frappe.db.sql_ddl(f"ALTER TABLE `tabRaven Channel` ADD COLUMN `{column}` {definition}")
