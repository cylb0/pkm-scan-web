document.addEventListener("DOMContentLoaded", function () {
  const supertypeSelect = document.querySelector("#id_supertype");

  if (supertypeSelect) {
    const supertypes = JSON.parse(
      supertypeSelect.getAttribute("data-supertypes"),
    );
    const pokemonFields = document.querySelectorAll(
      ".field-hp, .field-retreat_cost, " +
        ".field-weak_type, .field-weak_value, .field-resist_type, .field-resist_value, " +
        "#abilities-group, #attacks-group",
    );

    console.log("fields", pokemonFields);

    function toggleFields() {
      const isPokemon = supertypeSelect.value == supertypes.POKEMON;
      pokemonFields.forEach((row) => {
        if (row) row.style.display = isPokemon ? "block" : "none";
      });
    }

    supertypeSelect.addEventListener("change", toggleFields);
    toggleFields();
  }
});
