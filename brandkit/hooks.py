app_name = "brandkit"
app_title = "Brandkit"
app_publisher = "Fathima Irfana"
app_description = "Applies and manages Lens branding across Frappe sites, including logos, icons, titles, and UI customization."
app_email = "fathima.irfana@lmnas.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "brandkit",
# 		"logo": "/assets/brandkit/logo.png",
# 		"title": "Brandkit",
# 		"route": "/brandkit",
# 		"has_permission": "brandkit.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/brandkit/css/brandkit.css"
# app_include_js = "/assets/brandkit/js/brandkit.js"

# include js, css files in header of web template
# web_include_css = "/assets/brandkit/css/brandkit.css"
# web_include_js = "/assets/brandkit/js/brandkit.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "brandkit/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "brandkit/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "brandkit.utils.jinja_methods",
# 	"filters": "brandkit.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "brandkit.install.before_install"
# after_install = "brandkit.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "brandkit.uninstall.before_uninstall"
# after_uninstall = "brandkit.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "brandkit.utils.before_app_install"
# after_app_install = "brandkit.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "brandkit.utils.before_app_uninstall"
# after_app_uninstall = "brandkit.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "brandkit.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "brandkit.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"brandkit.tasks.all"
# 	],
# 	"daily": [
# 		"brandkit.tasks.daily"
# 	],
# 	"hourly": [
# 		"brandkit.tasks.hourly"
# 	],
# 	"weekly": [
# 		"brandkit.tasks.weekly"
# 	],
# 	"monthly": [
# 		"brandkit.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "brandkit.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "brandkit.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "brandkit.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "brandkit.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["brandkit.utils.before_request"]
# after_request = ["brandkit.utils.after_request"]

# Job Events
# ----------
# before_job = ["brandkit.utils.before_job"]
# after_job = ["brandkit.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"brandkit.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

