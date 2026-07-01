// /*
//  * BrandKit Demo Banner
//  *
//  * Displays a banner inside the ERPNext Desk that allows
//  * System Managers to install industry-specific demo data.
//  *
//  * The banner is shown only when:
//  *
//  *  • User is a System Manager
//  *  • Demo data has not been installed
//  *
//  * The backend decides whether the banner should be shown.
//  */

// frappe.provide("brandkit.demo");

// /**
//  * BrandKit Demo Banner
//  */
// brandkit.demo.Banner = class Banner {

// 	//------------------------------------------------------------------
// 	// Constructor
// 	//------------------------------------------------------------------

// 	constructor() {

// 		/**
// 		 * Backend response.
// 		 */
// 		this.state = null;

// 		/**
// 		 * Root banner element.
// 		 */
// 		this.$banner = null;

// 		/**
// 		 * Progress dialog.
// 		 */
// 		this.progress_dialog = null;

// 		/**
// 		 * Prevent duplicate rendering.
// 		 */
// 		this.rendered = false;
// 	}

// 	//------------------------------------------------------------------
// 	// Entry Point
// 	//------------------------------------------------------------------

// 	/**
// 	 * Initialize banner.
// 	 */
// 	async init() {

// 		/*
// 		 * Wait until the Desk layout exists.
// 		 */
// 		if (!$(".layout-main-section").length) {
// 			return;
// 		}

// 		/*
// 		 * Prevent duplicate banners after
// 		 * workspace navigation.
// 		 */
// 		if (this.rendered) {
// 			return;
// 		}

// 		/*
// 		 * Ask backend whether banner
// 		 * should be shown.
// 		 */
// 		await this.load_state();

// 		if (!this.state.show_banner) {
// 			return;
// 		}

// 		this.render();

// 		this.bind_events();

// 		this.rendered = true;
// 	}

// 	//------------------------------------------------------------------
// 	// Load Banner State
// 	//------------------------------------------------------------------

// 	/**
// 	 * Load banner configuration from backend.
// 	 *
// 	 * Returns
// 	 * -------
// 	 * {
// 	 *      show_banner,
// 	 *      installed,
// 	 *      industries
// 	 * }
// 	 */
// 	async load_state() {

// 		const response = await frappe.call({
// 			method:
// 				"brandkit.api.demo.get_demo_banner_state",
// 		});

// 		this.state = response.message;
// 	}

// 	//------------------------------------------------------------------
// 	// Render Banner
// 	//------------------------------------------------------------------

// 	/**
// 	 * Render the banner.
// 	 */

//     render() {

//         // Remove any previous banner
//         $("#brandkit-demo-banner").remove();

//         /*
//         * Build Industry dropdown.
//         */
//         const options = this.state.industries
//             .map(industry => `
//                 <option value="${industry.id}">
//                     ${industry.title}
//                 </option>
//             `)
//             .join("");

//             const html = `
//                 <div class="brandkit-demo-header">

//                 <div class="brandkit-demo-title">
//                     ✨ Setup Demo Data
//                 </div>

//                 <div class="brandkit-demo-actions">

//                     <button
//                         id="brandkit-demo-minimize"
//                         class="brandkit-demo-action"
//                         title="Minimize">

//                         <i class="fa fa-window-minimize"></i>

//                     </button>

//                     <button
//                         id="brandkit-demo-close"
//                         class="brandkit-demo-action"
//                         title="Close">

//                         <i class="fa fa-times"></i>

//                     </button>

//                 </div>

//             </div>

//             <div class="brandkit-demo-body">

//                 <div class="brandkit-demo-description">

//                     Install sample data for a selected industry.

//                 </div>
                
//                     <select
//                         class="form-control mt-3"
//                         id="brandkit-demo-industry">
                
//                         <option value="">
//                             Select Industry
//                         </option>
                
//                         ${options}
                
//                     </select>
                
//                     <button
//                         id="brandkit-demo-install"
//                         class="btn btn-primary btn-block mt-3">

//                         Setup Demo Data

//                     </button>

//                 </div>
//                 `;

//         this.$banner = $(html);

//         // Floating card (doesn't disturb the Desk layout)
//         $("body").append(this.$banner);

//         this.progress_dialog =
//             new brandkit.demo.ProgressDialog();
//     }

// 		//------------------------------------------------------------------
// 	// Bind Events
// 	//------------------------------------------------------------------

// 	/**
// 	 * Bind click handlers.
// 	 */
// 	bind_events() {

// 		/*
// 		 * Setup Demo button.
// 		 */

// 		this.$banner.on(
// 			"click",
// 			"#brandkit-demo-install",
// 			() => {

// 				this.setup_demo_data();

// 			},
// 		);

//         this.$banner.on(
//             "click",
//             "#brandkit-demo-minimize",
//             () => {
        
//                 this.$banner.toggleClass("minimized");
        
//                 const icon = this.$banner
//                     .find("#brandkit-demo-minimize i");
        
//                 if (
//                     this.$banner.hasClass("minimized")
//                 ) {
        
//                     icon.removeClass("fa-window-minimize");
        
//                     icon.addClass("fa-window-maximize");
        
//                 } else {
        
//                     icon.removeClass("fa-window-maximize");
        
//                     icon.addClass("fa-window-minimize");
        
//                 }
        
//             }
//         );

//         this.$banner.on(
//             "click",
//             "#brandkit-demo-close",
//             () => {
        
//                 this.$banner.fadeOut(150, () => {
        
//                     this.$banner.remove();
        
//                 });
        
//             }
//         );
// 	}

// 	//------------------------------------------------------------------
// 	// Install Demo Data
// 	//------------------------------------------------------------------

// 	/**
// 	 * Starts the demo installation.
// 	 */
// 	async setup_demo_data() {

// 		const industry = this.$banner
// 			.find("#brandkit-demo-industry")
// 			.val();

// 		/*
// 		 * Industry is mandatory.
// 		 */

// 		if (!industry) {

// 			frappe.msgprint({
// 				title: __("Industry Required"),
// 				message: __("Please select an industry."),
// 				indicator: "orange",
// 			});

// 			return;
// 		}

// 		/*
// 		 * Disable controls so the user
// 		 * cannot start another installation.
// 		 */

// 		this.$banner
// 			.find("button")
// 			.prop("disabled", true);

// 		this.$banner
// 			.find("select")
// 			.prop("disabled", true);

// 		/*
// 		 * Open progress dialog.
// 		 */

// 		this.progress_dialog.start();

// 		try {

// 			/*
// 			 * Call backend.
// 			 *
// 			 * The backend immediately enqueues
// 			 * a background job and returns.
// 			 *
// 			 * Progress updates are received
// 			 * through realtime events.
// 			 */

// 			await frappe.call({

// 				method:
// 					"brandkit.api.demo.setup_demo_data",

// 				args: {
// 					industry: industry,
// 				},

// 			});

// 		}
// 		catch (error) {

// 			console.error(error);

// 			this.progress_dialog.error(
// 				__("Failed to start demo installation.")
// 			);

// 			this.enable_controls();
// 		}
// 	}

// 	//------------------------------------------------------------------
// 	// Enable Controls
// 	//------------------------------------------------------------------

// 	/**
// 	 * Enable banner controls.
// 	 */
// 	enable_controls() {

// 		if (!this.$banner) {
// 			return;
// 		}

// 		this.$banner
// 			.find("button")
// 			.prop("disabled", false);

// 		this.$banner
// 			.find("select")
// 			.prop("disabled", false);
// 	}

// };
// // ---------------------------------------------------------------------
// // Global Banner Instance
// // ---------------------------------------------------------------------

// /*
//  * Keep a single banner instance for the entire Desk.
//  */

// brandkit.demo.banner = null;

// // ---------------------------------------------------------------------
// // Initialize Banner
// // ---------------------------------------------------------------------

// /**
//  * Create the banner if it has not already been created.
//  */
// brandkit.demo.initialize = async function () {

// 	/*
// 	 * Wait until the Desk layout is available.
// 	 */

// 	if (!$(".layout-main-section").length) {

// 		setTimeout(() => {

// 			brandkit.demo.initialize();

// 		}, 500);

// 		return;
// 	}

// 	/*
// 	 * Create banner instance only once.
// 	 */

// 	if (!brandkit.demo.banner) {

// 		brandkit.demo.banner =
// 			new brandkit.demo.Banner();
// 	}

// 	/*
// 	 * If the banner element still exists,
// 	 * don't render it again.
// 	 */

// 	if (
// 		brandkit.demo.banner.$banner &&
// 		brandkit.demo.banner.$banner.closest("body").length
// 	) {
// 		return;
// 	}

// 	/*
// 	 * Allow rendering again.
// 	 */

// 	brandkit.demo.banner.rendered = false;

// 	try {

// 		await brandkit.demo.banner.init();

// 	}
// 	catch (error) {

// 		console.error(
// 			"BrandKit Demo Banner",
// 			error,
// 		);

// 	}
// };

// // ---------------------------------------------------------------------
// // Initial Load
// // ---------------------------------------------------------------------

// $(document).ready(() => {

// 	brandkit.demo.initialize();

// });

// // ---------------------------------------------------------------------
// // Desk Route Changes
// // ---------------------------------------------------------------------

// /*
//  * ERPNext is a Single Page Application.
//  *
//  * When users navigate between Workspaces,
//  * List Views,
//  * Reports,
//  * Forms,
//  * etc.,
//  * the page content changes without a full
//  * browser reload.
//  *
//  * Re-check whether the banner should be
//  * displayed whenever the route changes.
//  */

// frappe.router.on("change", () => {

// 	setTimeout(() => {

// 		brandkit.demo.initialize();

// 	}, 300);

// });

/*
 * BrandKit Demo Banner
 *
 * Floating onboarding-style card that allows System Managers
 * to install BrandKit demo data.
 *
 * The banner:
 *  - appears only once
 *  - floats above Desk
 *  - can be collapsed
 *  - can be closed
 *  - listens for realtime progress events
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

		/**
		 * Banner collapsed?
		 */
		this.collapsed = false;
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
						id="brandkit-demo-collapse"
						title="Collapse"
					>

						−

					</button>

					<button
						type="button"
						id="brandkit-demo-close"
						title="Close"
					>

						×

					</button>

				</div>

			</div>

			<div class="brandkit-demo-body">

				<div class="brandkit-demo-description">

					Install sample ERPNext data
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
		// Collapse / Expand
		//--------------------------------------------------------------

		this.$banner.on(
			"click",
			"#brandkit-demo-collapse",
			() => {

				this.toggle();

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
	// Toggle
	//------------------------------------------------------------------

	toggle() {

		this.collapsed = !this.collapsed;

		if (this.collapsed) {

			this.$banner.addClass("collapsed");

			this.$banner
				.find("#brandkit-demo-collapse")
				.text("+")
				.attr("title", "Expand");

		}
		else {

			this.$banner.removeClass("collapsed");

			this.$banner
				.find("#brandkit-demo-collapse")
				.text("−")
				.attr("title", "Collapse");

		}

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