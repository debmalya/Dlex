exports.handler = (event, context, callback) => {
    console.log("event :",event);
    var status = "";
    
    var num = Number(event.currentIntent.slots.Integer);
    status = status.concat(num);
    console.log("number :", num);
    if (num < 0){
        callback(null, "Please enter a positive number.");
    }
    var square_root = Math.sqrt(num);
    var prime = true;
    if (num === 1){
        prime = false;
    } else {
        for (var i = 2; i <= square_root; i++){
            if (num % i === 0){
                prime = false;
                break;
            }
        }
    }
    
    if (!prime){
        console.log(num, " is not prime");
        status = status.concat(" is not a prime number");
    } else {
        console.log(num, " is prime");
        status = status.concat(" is a prime number");
    }
    
    console.log("status",status);
    callback(null, {
        "dialogAction": {
          "type": "Close",
          "fulfillmentState": "Fulfilled", // <-- Required
          "message": {
            "contentType": "PlainText",
            "content": status
          }
        }} );
};
