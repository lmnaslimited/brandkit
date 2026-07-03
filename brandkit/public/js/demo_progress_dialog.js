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
$(() => {
	frappe.provide("brandkit.demo");

	/**
	 * Progress Dialog
	 */
	brandkit.demo.clProgressDialog = class clProgressDialog {

		/**
		 * Constructor
		 */
		constructor() {

			// Frappe Dialog instance.
			this.ldDialog = null;

			// Progress bar element.
			this.$lProgressFill = null;

			// Percentage label.
			this.$lProgressPercent = null;

			// Current status message.
			this.$lMessage = null;

			// Whether dialog has been created.
			this.lInitialized = false;
		}

		// ---------------------------------------------------------------------
		// Create Dialog
		// ---------------------------------------------------------------------

		show() {

			if (this.lInitialized) {
				return;
			}

			this.ldDialog = new frappe.ui.Dialog({
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
					this.hide();
				},
			});

			this.ldDialog.show();

			this.ldDialog.set_df_property(
				"progress_html",
				"options",
				this.getHtml()
			);

			this.cacheElements();

			this.lInitialized = true;
		}

		// ---------------------------------------------------------------------
		// HTML Template
		// ---------------------------------------------------------------------

		getHtml() {

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

		cacheElements() {

			const LdWrapper =
				this.ldDialog.fields_dict
					.progress_html
					.$wrapper;

			this.$lProgressFill =
				LdWrapper.find(
					".brandkit-progress-fill"
				);

			this.$lProgressPercent =
				LdWrapper.find(
					".brandkit-progress-percent"
				);

			this.$lMessage =
				LdWrapper.find(
					".brandkit-progress-message"
				);
		}

		// ---------------------------------------------------------------------
		// Update Progress
		// ---------------------------------------------------------------------

		update(iProgress, iMessage) {

			if (!this.lInitialized) {
				return;
			}

			iProgress = Math.max(
				0,
				Math.min(iProgress, 100)
			);

			this.$lProgressFill.css(
				"width",
				`${iProgress}%`
			);

			this.$lProgressPercent.text(
				`${iProgress}%`
			);

			this.$lMessage.text(
				iMessage
			);
		}

		// ---------------------------------------------------------------------
		// Success
		// ---------------------------------------------------------------------

		success(iMessage = __("Demo installation completed.")) {

			this.update(
				100,
				iMessage
			);
			this.$lProgressFill
				.removeClass("error")
				.addClass("success");

			frappe.show_alert({
				message: iMessage,
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

		error(iMessage) {

			this.$lProgressFill
				.removeClass("success")
				.addClass("error");
		
			this.update(
				this.$lProgressPercent.text().replace("%", ""),
				__("Installation failed")
			);
		
			frappe.msgprint({
				title: __("Installation Failed"),
				message: iMessage,
				indicator: "red",
			});
		
			this.ldDialog.get_primary_btn().prop("disabled", false);
		}

		// ---------------------------------------------------------------------
		// Hide Dialog
		// ---------------------------------------------------------------------

		hide() {

			if (!this.lInitialized) {
				return;
			}

			this.ldDialog.hide();

			this.lInitialized = false;
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
				(idData) => {

					this.update(
						idData.progress,
						idData.message
					);

					/*
					* Installation completed.
					*/

					if (idData.progress >= 100) {

						this.success(
							idData.message
						);

						return;
					}

					/*
					* Backend reports failure.
					*
					* Convention:
					* progress < 0
					*/

					if (idData.progress < 0) {

						this.error(
							idData.message
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
});