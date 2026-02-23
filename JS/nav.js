// I wrote this so the hamburger button can open and close the menu on mobile.
document.addEventListener("DOMContentLoaded", () => {
  const nav = document.querySelector("nav");
  const button = document.querySelector(".nav-toggle");
  const menu = document.querySelector("#nav-menu");

  // I added this check so nothing breaks if a page is missing nav pieces.
  if (!nav || !button || !menu) return;

  // I made a helper function so I can open/close the menu in one place.
  const setOpen = (open) => {
    nav.classList.toggle("open", open);
    menu.classList.toggle("open", open);
    button.setAttribute("aria-expanded", String(open));
  };

  // I toggle the menu when I click the hamburger button.
  button.addEventListener("click", () => {
    const isOpen = button.getAttribute("aria-expanded") === "true";
    setOpen(!isOpen);
  });

  // I close the menu after I click a link (this feels better on mobile).
  menu.addEventListener("click", (e) => {
    if (e.target.tagName === "A") setOpen(false);
  });

  // I close the menu if the screen gets resized back to desktop size.
  window.addEventListener("resize", () => {
    if (window.innerWidth > 768) setOpen(false);
  });
});