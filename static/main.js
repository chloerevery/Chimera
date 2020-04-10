$(document).ready(function() {
  console.log("ready!");

  // on form submission ...
  $('form').on('submit', function() {

    console.log("the form has beeen submitted");

    // grab values
    valueOne = $('input[name="translation"]').val();
    console.log(valueOne)

    $.ajax({
      type: "POST",
      url: "/",
      data : { 'untranslatedProse': valueOne },
      success: function(results) {
          console.log("Success");
      },
      error: function(error) {
        console.log(error)
      }
    });
    });
