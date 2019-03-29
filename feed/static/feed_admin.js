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
            $("#policy_pubkey").text('Policy Pub Key: ' + data.policy_pubkey);
          }
        }
    })

  });

  $("#create-post").click(function() {
    var post = $("#post").val();
    console.log('Saving Post: ' + post);

    $.ajax({
        type: "POST",
        url: 'add_post/',
        dataType: 'html',
        data: {'post': post},
        success: function (data) {
          $("#posts").prepend(data);
        }
    })
  });
});
