export default function initializeCollapsibleMenus() {
	document.addEventListener("DOMContentLoaded", () => {
		document.querySelectorAll('header > nav > button').forEach(
			button => button.addEventListener("click",
				e => {
					const menuId = button.getAttribute("aria-controls");
					const shouldShowMenu = document.getElementById(menuId).hidden;

					// Update aria-expanded on all buttons
					document.querySelectorAll('header > nav > button').forEach(
						b => b.setAttribute('aria-expanded', b.getAttribute('aria-controls') === menuId && shouldShowMenu)
					);

					// Show the correct submenu
					document.querySelectorAll('.submenu').forEach(m => m.hidden = !shouldShowMenu || m.id !== menuId);
				}
			)
		);
	});
}
