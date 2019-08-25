
/* for page sign_in to chech password  */
function check() {

    var password = $("#password")
    var confirmPasssWord = $("#confirmPasssWord")
    var buttonSubmit = $("#buttonSubmit")
    var messageOne = $("#confirm-message1")
    var messageTwo = $("#confirm-message2")
    if (password.val() === "") {
        console.log("gsd")
        confirmPasssWord.removeAttr("style")
        messageOne.prop("hidden", true)
        messageTwo.prop("hidden", true)
    } else {
        if (password.val() === confirmPasssWord.val()) {

            confirmPasssWord.css("backgroundColor", "#23b467")
            buttonSubmit.prop("disabled", false)
            messageOne.prop("hidden", false)
            messageTwo.prop("hidden", true)
        } else {
            confirmPasssWord.css("backgroundColor", "#FF4703")

            messageOne.prop("hidden", true)
            messageTwo.prop("hidden", false)
        }
    }

}