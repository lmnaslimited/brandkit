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

			// Whether dialog has been created.
			this.lInitialized = false;

			// Polling interval handle (fallback delivery path).
			this.lPollTimer = null;

			// Prevents success()/error() firing twice if both the
			// realtime push and a poll tick land close together.
			this.lFinished = false;
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
						options: this.getHtml(),
					},
				],
				primary_action_label: __("Close"),
				primary_action: () => {
					this.hide();
				},
			});

			this.ldDialog.show();

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
					${__("Preparing installation...")}
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
		// Update Progress
		//
		// NOTE: Elements are looked up live from the dialog wrapper on every
		// call instead of being cached once in cacheElements(). Caching them
		// is fragile -- if the Dialog's HTML field re-renders for any reason
		// (responsive re-layout, a second set_df_property, etc.) the cached
		// jQuery objects go stale and silently no-op, which looks exactly
		// like "progress stuck at 0%" even though events are arriving fine.
		// ---------------------------------------------------------------------

		update(iProgress, iMessage) {

			if (!this.lInitialized || !this.ldDialog) {
				return;
			}

			iProgress = Math.max(
				0,
				Math.min(iProgress, 100)
			);

			// Always query live -- never cache.
			const $lWrapper = this.ldDialog.$wrapper;

			$lWrapper
				.find(".brandkit-progress-fill")
				.css("width", `${iProgress}%`);

			$lWrapper
				.find(".brandkit-progress-percent")
				.text(`${iProgress}%`);

			if (iMessage) {
				$lWrapper
					.find(".brandkit-progress-message")
					.text(iMessage);
			}
		}

		// ---------------------------------------------------------------------
		// Success
		// ---------------------------------------------------------------------

		success(iMessage = __("Demo installation completed.")) {

			if (this.lFinished) {
				return;
			}
			this.lFinished = true;
			this.stopPolling();

			this.update(
				100,
				iMessage
			);

			this.ldDialog.$wrapper
				.find(".brandkit-progress-fill")
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

			if (!this.ldDialog) {
				return;
			}

			if (this.lFinished) {
				return;
			}
			this.lFinished = true;
			this.stopPolling();

			this.ldDialog.$wrapper
				.find(".brandkit-progress-fill")
				.removeClass("success")
				.addClass("error");

			const l_current = this.ldDialog.$wrapper
				.find(".brandkit-progress-percent")
				.text()
				.replace("%", "") || 0;

			this.update(
				Number(l_current),
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
			this.stopPolling();
		}

		// ---------------------------------------------------------------------
		// Poll Progress (fallback delivery path)
		//
		// The realtime push is best-effort: it depends on the browser's
		// websocket finishing its connect/auth/room-join handshake before
		// the backend publishes an update. On a fast install (common in
		// production) or behind a proxy that's slow to establish
		// websockets, that handshake can lose the race entirely and no
		// realtime event ever arrives -- even though the job succeeds.
		//
		// Polling a plain HTTP endpoint backed by a cached snapshot has
		// no such race: whatever the backend last wrote is always
		// readable on the next tick, regardless of socket state.
		// ---------------------------------------------------------------------

		startPolling() {

			this.stopPolling();

			this.lPollTimer = setInterval(async () => {

				if (this.lFinished) {
					this.stopPolling();
					return;
				}

				try {
					const LdResponse = await frappe.call({
						method: "brandkit.api.demo.get_demo_progress",
					});

					const IdData = LdResponse.message;

					if (!IdData) {
						return;
					}

					this.update(
						IdData.progress,
						IdData.message
					);

					if (IdData.progress >= 100) {
						this.success(IdData.message);
					}
					else if (IdData.progress < 0) {
						this.error(IdData.message);
					}
				}
				catch (LError) {
					console.error(
						"BrandKit progress poll failed:",
						LError
					);
				}

			}, 1500);
		}

		stopPolling() {

			if (this.lPollTimer) {
				clearInterval(this.lPollTimer);
				this.lPollTimer = null;
			}
		}

		// ---------------------------------------------------------------------
		// Subscribe to Realtime Progress
		//
		// This dialog is the SINGLE owner of the "brandkit_demo_progress"
		// listener. Nothing else in the app (e.g. demo_banner.js) should
		// call frappe.realtime.on/off for this event -- two owners racing
		// to add/remove the same named listener is what let progress
		// updates get silently dropped before.
		//
		// This is now a bonus fast-path only -- polling above is the
		// guaranteed delivery mechanism. If the socket happens to be
		// ready, updates feel instant; if not, the next poll tick
		// (<=1.5s later) catches up regardless.
		// ---------------------------------------------------------------------

		listen() {

			frappe.realtime.off("brandkit_demo_progress");

			frappe.realtime.on(
				"brandkit_demo_progress",
				(idData) => {

					// Uncomment while debugging delivery issues:
					// console.log("brandkit_demo_progress", idData);

					this.update(
						idData.progress,
						idData.message
					);

					if (idData.progress >= 100) {
						this.success(idData.message);
						return;
					}

					if (idData.progress < 0) {
						this.error(idData.message);
					}
				}
			);
		}

		// ---------------------------------------------------------------------
		// Public API
		// ---------------------------------------------------------------------

		start() {

			this.lFinished = false;
			this.show();
			this.listen();
			this.startPolling();
			this.update(
				0,
				__("Preparing installation...")
			);
		}
	};
});