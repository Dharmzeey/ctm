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
if (document.getElementById("flash-message")) {
  window.onload = () => {
    popUp = document.getElementById("flash-message");
    setTimeout(() => {
      popUp.style.display = "none"
    }, 1700)
  }
}

// this is for location filter and set

$('#toggle-location').click(function(){
  $('#set-location').toggleClass('scale-y-0');
})

$('#id_state').change(function () {
  let url = $("#data-form").attr("data-url");
  let state = $(this).val();
  $.ajax({
    url: url,
    data: {
      'state': state
    },
    success: function (data) {
      $("#id_location").html(data);
      $("#id_institution").html('<option value="">---------</option>');

      // let productUrl = "{% url 'filter_load' %}"
      $.ajax({
        url: productUrl,
        success: function (data) {
          $("#recent-and-products").html(data)
        }
      })
    }
  })
})

$("#id_location").change(function () {
  let url = $("#data-form").attr("data-url");
  let location = $(this).val();
  $.ajax({
    url: url,
    data: {
      'location': location
    }, success: function (data) {
      $("#id_institution").html(data)

      // let productUrl = "{% url 'filter_load' %}"
      $.ajax({
        url: productUrl,
        success: function (data) {
          $("#recent-and-products").html(data)
        }
      })
    }
  })
})


$("#id_institution").change(function () {
  let storeUrl = $("#data-form").attr("data-url");
  let institution = $(this).val();
  $.ajax({
    url: storeUrl,
    data: {
      'institution': institution
    },
    success: function (data) {
      $("#store-list").html(data);

      // let productUrl = "{% url 'filter_load' %}"
      $.ajax({
        url: productUrl,
        success: function (data) {
          $("#recent-and-products").html(data)
        }
      })
    }
  })
})

$("#reset").click(function () {
  // let buttonUrl = "{% url 'reset_general' %}"
  $.ajax({
    url: buttonUrl,
    data: {
      'reset': true
    }, success() {
      location.reload()
    }
  })
})

$("#general").click(function () {
  // let buttonUrl = "{% url 'reset_general' %}"
  $.ajax({
    url: buttonUrl,
    data: {
      'general': true
    }, success() {
      location.reload()
    }
  })
})
