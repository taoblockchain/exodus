function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function loginWithSignature(address, signature, login_url, onLoginRequestError, onLoginFail, onLoginSuccess) {
    var request = new XMLHttpRequest();
    request.open('POST', login_url, true);
    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {
            // Success!
            var resp = JSON.parse(request.responseText);
            if (resp.success) {
                if (typeof onLoginSuccess == 'function') {
                    onLoginSuccess(resp);
                }
            } else {
                if (typeof onLoginFail == 'function') {
                    //onLoginFail(resp);
                    // extract address and place into form
                    //{success: false, error: "Can't find a user for the provided signature with address 0x3c260ace69040ca4a95a16638bc17ad458e9553e"}
                    let address = resp.error.substring(0, resp.error.length - 1);
                    console.log(address);
                    var url = window.location.href;
                    var arr = url.split("/");
                    var domain = arr[0] + "//" + arr[2]
                    window.location.replace(domain + "/signup/");
                }
            }
        } else {
            // We reached our target server, but it returned an error
            console.log("Autologin failed - request status " + request.status);
            if (typeof onLoginRequestError == 'function') {
                onLoginRequestError(request);
            }
        }
    };

    request.onerror = function () {
        console.log("Autologin failed - there was an error");
        if (typeof onLoginRequestError == 'function') {
            onLoginRequestError(request);
        }
        // There was a connection error of some sort
    };
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
    request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    var formData = 'address=' + address + '&signature=' + signature;
    request.send(formData);
}

function checkWeb3(callback) {
    if (window.ethereum) {
        window.ethereum.enable();
    }
    web3.eth.getAccounts((err, accounts) => { // Check for wallet being locked
        if (err) {
            throw err;
        }
        callback(accounts.length !== 0);
    });
}

function web3Login(login_url, onTokenRequestFail, onTokenSignFail, onTokenSignSuccess, // used in this function
                   onLoginRequestError, onLoginFail, onLoginSuccess) {
    // used in loginWithSignature

    // 1. Retrieve arbitrary login token from server
    // 2. Sign it using web3
    // 3. Send signed message & your eth address to server
    // 4. If server validates that you signature is valid
    // 4.1 The user with an according eth address is found - you are logged in
    // 4.2 The user with an according eth address is NOT found - you are redirected to signup page


    var request = new XMLHttpRequest();
    request.open('GET', login_url, true);

    request.onload = function () {
        if (request.status >= 200 && request.status < 400) {


            // Success!
            var resp = JSON.parse(request.responseText);
            var token = resp.data;
            console.log("Token: " + token);
            var msg = web3.toHex(token);
            var from = web3.eth.accounts[0];
            console.log(from);
            web3.personal.sign(msg, from, (err, result) => {
                if (err) {
                    if (typeof onTokenSignFail == 'function') {
                        onTokenSignFail(err);
                    }
                    console.log("Failed signing message \n" + msg + "\n - " + err);
                    let address = resp.error.substring(0, resp.error.length - 1);
                    console.log(address);
                    var url = window.location.href;
                    var arr = url.split("/");
                    var domain = arr[0] + "//" + arr[2]
                    window.location.replace(domain);
                } else {
                    console.log("Signed message: " + result);
                    if (typeof onTokenSignSuccess == 'function') {
                        onTokenSignSuccess(result);
                    }
                    loginWithSignature(from, result, login_url, onLoginRequestError, onLoginFail, onLoginSuccess);
                }
            });

        } else {
            // We reached our target server, but it returned an error
            console.log("Autologin failed - request status " + request.status);
            if (typeof onTokenRequestFail == 'function') {
                onTokenRequestFail(request);
            }
        }
    };

    request.onerror = function () {
        // There was a connection error of some sort
        console.log("Autologin failed - there was an error");
        if (typeof onTokenRequestFail == 'function') {
            onTokenRequestFail(request);
        }
    };
    request.send();
}



