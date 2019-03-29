$(document).ready(function () {

  console.log('YO');

  $("#create-policy").click(function() {
    console.log('click');

    $.ajax({
        url: 'create_policy/',
        dataType: 'json',
        success: function (data) {
          if (data.policy_pubkey) {
            console.log(data.policy_pubkey);
            $("#policy_pubkey_hex").text(data.policy_pubkey);
            $("#enrico_pubkey_hex").text(data.enrico_pubkey);
          }
        }
    })

  });

  $("#create-post").click(function() {
    var post = $("#post").val();
    console.log('Saving Post: ' + post);
    var policy_pubkey_hex = $("#policy_pubkey_hex").text();
    var enrico_pubkey_hex = $("#enrico_pubkey_hex").text();

    $.ajax({
        type: "POST",
        url: 'add_post/',
        dataType: 'html',
        data: {
          'post': post,
          'policy_pubkey_hex': policy_pubkey_hex,
          'enrico_pubkey_hex': enrico_pubkey_hex
        },
        success: function (data) {
          $("#posts").append(data);
        }
    })
  });
});
