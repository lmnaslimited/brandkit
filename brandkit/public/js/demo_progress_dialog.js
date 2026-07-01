/*
 * BrandKit Demo Progress Dialog
 *
 * This dialog displays the realtime progress of the
 * BrandKit demo installation.
 *
 * Progress updates are received through
 * frappe.publish_realtime() events sent from the backend.
 *
 * Backend Event:
 *
 *      brandkit_demo_progress
 *
 * Message Format:
 *
 * {
 *      message: "Importing Customer...",
 *      progress: 55
 * }
 */

frappe.provide("brandkit.demo");

/**
 * Progress Dialog
 */
brandkit.demo.ProgressDialog = class ProgressDialog {

	/**
	 * Constructor
	 */
	constructor() {

		/**
		 * Frappe Dialog instance.
		 */
		this.dialog = null;

		/**
		 * Progress bar element.
		 */
		this.$progress_fill = null;

		/**
		 * Percentage label.
		 */
		this.$progress_percent = null;

		/**
		 * Current status message.
		 */
		this.$message = null;

		/**
		 * Whether dialog has been created.
		 */
		this.initialized = false;
	}

	// ---------------------------------------------------------------------
	// Create Dialog
	// ---------------------------------------------------------------------

	show() {

		if (this.initialized) {
			return;
		}

		this.dialog = new frappe.ui.Dialog({
			title: __("Installing Demo Data"),
			size: "small",
			static: true,
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "progress_html",
				},
			],
			primary_action_label: __("Close"),
			primary_action: () => {

				/*
				 * Prevent user from closing while
				 * installation is running.
				 */

			},
		});

		this.dialog.show();

		this.dialog.set_df_property(
			"progress_html",
			"options",
			this.get_html()
		);

		this.cache_elements();

		this.initialized = true;
	}

	// ---------------------------------------------------------------------
	// HTML Template
	// ---------------------------------------------------------------------

	get_html() {

		return `

			<div class="brandkit-progress-wrapper">

				<div
					class="brandkit-progress-message"
				>
					Preparing installation...
				</div>

				<div
					class="brandkit-progress-bar"
				>

					<div
						class="brandkit-progress-fill"
						style="width:0%"
					></div>

				</div>

				<div
					class="brandkit-progress-percent"
				>
					0%
				</div>

			</div>

		`;
	}

	// ---------------------------------------------------------------------
	// Cache DOM Elements
	// ---------------------------------------------------------------------

	cache_elements() {

		const wrapper =
			this.dialog.fields_dict
				.progress_html
				.$wrapper;

		this.$progress_fill =
			wrapper.find(
				".brandkit-progress-fill"
			);

		this.$progress_percent =
			wrapper.find(
				".brandkit-progress-percent"
			);

		this.$message =
			wrapper.find(
				".brandkit-progress-message"
			);
	}

	// ---------------------------------------------------------------------
	// Update Progress
	// ---------------------------------------------------------------------

	update(progress, message) {

		if (!this.initialized) {
			return;
		}

		progress = Math.max(
			0,
			Math.min(progress, 100)
		);

		this.$progress_fill.css(
			"width",
			`${progress}%`
		);

		this.$progress_percent.text(
			`${progress}%`
		);

		this.$message.text(
			message
		);
	}

	// ---------------------------------------------------------------------
	// Success
	// ---------------------------------------------------------------------

	success(message = __("Demo installation completed.")) {

		this.update(
			100,
			message
		);
        this.$progress_fill
            .removeClass("error")
            .addClass("success");

		frappe.show_alert({
			message: message,
			indicator: "green",
		});

		setTimeout(() => {

			this.hide();

			/*
			 * Reload Desk so the newly imported
			 * demo data becomes immediately visible.
			 */
			window.location.reload();

		}, 1500);
	}

	// ---------------------------------------------------------------------
	// Failure
	// ---------------------------------------------------------------------

	error(message) {
        this.$progress_fill
            .removeClass("success")
            .addClass("error");

		frappe.msgprint({
			title: __("Installation Failed"),
			message: message,
			indicator: "red",
		});

		this.hide();
	}

	// ---------------------------------------------------------------------
	// Hide Dialog
	// ---------------------------------------------------------------------

	hide() {

		if (!this.initialized) {
			return;
		}

		this.dialog.hide();

		this.initialized = false;
	}

	// ---------------------------------------------------------------------
	// Subscribe to Realtime Progress
	// ---------------------------------------------------------------------

	listen() {

		/*
		 * Remove any existing listener.
		 * Prevents duplicate events after
		 * multiple installations.
		 */

		frappe.realtime.off(
			"brandkit_demo_progress"
		);

		/*
		 * Listen for backend progress updates.
		 */

		frappe.realtime.on(
			"brandkit_demo_progress",
			(data) => {

				this.update(
					data.progress,
					data.message
				);

				/*
				 * Installation completed.
				 */

				if (data.progress >= 100) {

					this.success(
						data.message
					);

					return;
				}

				/*
				 * Backend reports failure.
				 *
				 * Convention:
				 * progress < 0
				 */

				if (data.progress < 0) {

					this.error(
						data.message
					);

				}

			}
		);
	}

	// ---------------------------------------------------------------------
	// Public API
	// ---------------------------------------------------------------------

	start() {

		this.show();

		this.listen();

		this.update(
			0,
			__("Preparing installation...")
		);
	}
};