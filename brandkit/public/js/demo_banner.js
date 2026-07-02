/*
 * BrandKit Demo Banner
 *
 * Floating onboarding-style card that allows System Managers
 * to install BrandKit demo data.
 */

frappe.provide("brandkit.demo");

/**
 * Demo Banner
 */
brandkit.demo.Banner = class Banner {

	//------------------------------------------------------------------
	// Constructor
	//------------------------------------------------------------------

	constructor() {

		/**
		 * Backend state.
		 */
		this.state = null;

		/**
		 * Banner DOM.
		 */
		this.$banner = null;

		/**
		 * Progress dialog.
		 */
		this.progress_dialog = null;

		/**
		 * Prevent duplicate rendering.
		 */
		this.rendered = false;
	}

	//------------------------------------------------------------------
	// Initialize
	//------------------------------------------------------------------

	async init() {

		/*
		 * Already rendered?
		 */

		if ($("#brandkit-demo-toast").length) {

			this.rendered = true;

			return;

		}
		if (
			sessionStorage.getItem(
				"brandkit_demo_banner_closed"
			)
		) {
			return;
		}

		await this.load_state();

		if (!this.state.show_banner) {
			return;
		}

		this.render();

		this.bind_events();

		this.rendered = true;
	}

	//------------------------------------------------------------------
	// Load Banner State
	//------------------------------------------------------------------

	async load_state() {

		const response = await frappe.call({

			method:
				"brandkit.api.demo.get_demo_banner_state",

		});

		this.state = response.message;
	}

	//------------------------------------------------------------------
	// Render Banner
	//------------------------------------------------------------------

	render() {

		/*
		 * Prevent duplicate DOM.
		 */

		if ($("#brandkit-demo-toast").length) {
			return;
		}

		/*
		 * Build Industry options.
		 */

		const options = this.state.industries
			.map(industry => {

				return `
					<option value="${industry.id}">
						${industry.title}
					</option>
				`;

			})
			.join("");

		/*
		 * Floating card.
		 */

		const html = `

		<div
			id="brandkit-demo-toast"
			class="brandkit-demo-toast"
		>

			<div class="brandkit-demo-header">

				<div class="brandkit-demo-title">

					✨ Setup Demo Data

				</div>

				<div class="brandkit-demo-actions">

					<button
						type="button"
						id="brandkit-demo-close"
						title="Close"
					>

						x

					</button>

				</div>

			</div>

			<div class="brandkit-demo-body">

				<div class="brandkit-demo-description">

					Install sample data
					for a selected industry.

				</div>

				<select
					class="form-control"
					id="brandkit-demo-industry"
				>

					<option value="">

						Select Industry

					</option>

					${options}

				</select>

				<button
					class="btn btn-primary btn-block"
					id="brandkit-demo-install"
				>

					Setup Demo Data

				</button>

			</div>

		</div>

		`;

		this.$banner = $(html);

		/*
		 * Append directly to BODY.
		 *
		 * This makes the banner float above
		 * the Desk exactly like ERPNext's
		 * onboarding widget.
		 */

		$("body").append(this.$banner);

		/*
		 * Progress dialog.
		 */

		this.progress_dialog =
			new brandkit.demo.ProgressDialog();
	}

	//------------------------------------------------------------------
	// Bind Events
	//------------------------------------------------------------------

	bind_events() {
		//--------------------------------------------------------------
		// Setup Demo
		//--------------------------------------------------------------

		this.$banner.on(
			"click",
			"#brandkit-demo-install",
			() => {

				this.setup_demo_data();

			},
		);

		//--------------------------------------------------------------
		// Close
		//--------------------------------------------------------------

		this.$banner.on(
			"click",
			"#brandkit-demo-close",
			() => {

				this.close();

			},
		);

	}

	//------------------------------------------------------------------
	// Close
	//------------------------------------------------------------------

	close() {

		if (!this.$banner) {
			return;
		}

		this.$banner.remove();

		this.$banner = null;

		this.rendered = false;
		sessionStorage.setItem(
			"brandkit_demo_banner_closed",
			"1",
		);

	}

	//------------------------------------------------------------------
	// Setup Demo
	//------------------------------------------------------------------

	async setup_demo_data() {

		const industry = this.$banner
			.find("#brandkit-demo-industry")
			.val();

		if (!industry) {

			frappe.msgprint({

				title: __("Industry Required"),

				message: __("Please select an industry."),

				indicator: "orange",

			});

			return;

		}

		this.disable_controls();

		this.progress_dialog.start();

		try {

			await frappe.call({

				method:
					"brandkit.api.demo.setup_demo_data",

				args: {
					industry: industry,
				},

			});

		}
		catch (error) {

			console.error(error);

			this.progress_dialog.error(
				__("Unable to start demo installation.")
			);

			this.enable_controls();

		}

	}

	//------------------------------------------------------------------
	// Disable Controls
	//------------------------------------------------------------------

	disable_controls() {

		if (!this.$banner) {
			return;
		}

		this.$banner
			.find("button")
			.prop("disabled", true);

		this.$banner
			.find("select")
			.prop("disabled", true);

	}

	//------------------------------------------------------------------
	// Enable Controls
	//------------------------------------------------------------------

	enable_controls() {

		if (!this.$banner) {
			return;
		}

		this.$banner
			.find("button")
			.prop("disabled", false);

		this.$banner
			.find("select")
			.prop("disabled", false);

	}
};

// ---------------------------------------------------------------------
// Global Banner Instance
// ---------------------------------------------------------------------

brandkit.demo.banner = null;

// ---------------------------------------------------------------------
// Initialize Banner
// ---------------------------------------------------------------------

brandkit.demo.initialize = async function () {

	/*
	 * Create only one Banner instance
	 * during the lifetime of Desk.
	 */

	if (!brandkit.demo.banner) {

		brandkit.demo.banner =
			new brandkit.demo.Banner();

	}

	/*
	 * Banner already exists in DOM.
	 */

	if ($("#brandkit-demo-toast").length) {
		return;
	}

	try {

		await brandkit.demo.banner.init();

	}
	catch (error) {

		console.error(
			"BrandKit Demo Banner",
			error,
		);

	}

};

// ---------------------------------------------------------------------
// Realtime Progress Listener
// ---------------------------------------------------------------------

frappe.realtime.on(
	"brandkit_demo_progress",
	(data) => {

		const banner = brandkit.demo.banner;

		if (
			!banner ||
			!banner.progress_dialog
		) {
			return;
		}

		/*
		 * Update Progress Dialog.
		 */

		banner.progress_dialog.update(

			data.progress,

			data.message,

		);

		/*
		 * Installation finished.
		 */

		if (data.progress >= 100) {

			setTimeout(() => {

				/*
				 * Hide progress dialog.
				 */

				banner.progress_dialog.hide();

				/*
				 * Remove banner.
				 */

				banner.close();

				frappe.show_alert({

					message: __(
						"Demo data installed successfully."
					),

					indicator: "green",

				});

			}, 1200);

		}

	},
);

// ---------------------------------------------------------------------
// Initial Load
// ---------------------------------------------------------------------

$(document).ready(() => {

	setTimeout(() => {

		brandkit.demo.initialize();

	}, 300);

});

// ---------------------------------------------------------------------
// Route Changes
// ---------------------------------------------------------------------

frappe.router.on(
	"change",
	() => {

		setTimeout(() => {

			brandkit.demo.initialize();

		}, 300);

	},
);

// ---------------------------------------------------------------------
// AJAX Page Loads
// ---------------------------------------------------------------------

$(document).ajaxComplete(() => {

	setTimeout(() => {

		brandkit.demo.initialize();

	}, 300);

});