// THIS IS FOR THE HAMBURGER MENU TOGGLING
if (document.querySelector("#menu-toggle-icon")) {
  const toggleMenu = document.querySelector("#menu-toggle-icon");
  const openAside = document.querySelector('#aside');

  function toggleFunction() {
    toggleMenu.classList.toggle("activated");
    openAside.classList.toggle("hidden");
  }

  toggleMenu.addEventListener('click', toggleFunction);
}

// THIS IS FOR POP UP MESSAGE DISAPPEAR
if (document.getElementById("pop-up")) {
  window.onload = () => {
    popUp = document.getElementById("pop-up");
    setTimeout(() => {
      popUp.style.display = "none"
    }, 1700)
  }
}