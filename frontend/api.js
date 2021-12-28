API_URL = "http://localhost:8000"

function isLoggedIn() {
    const token = localStorage.getItem("token");
    if (!token) {
        return false
    }
    else {
        return true
    }
}

function logout() {
    localStorage.removeItem("token");
    redirectToLoginPage();
}

function makeRequest(method, url, data = null, headers = {}) {
    let req = new XMLHttpRequest();
    req.open(method, url, false);
    req.setRequestHeader("Content-Type", "application/json")
    for (let headerName in headers) {
        req.setRequestHeader(headerName, headers[headerName])
    }
    req.send(JSON.stringify(data));
    if (req.status == 200) {
        return JSON.parse(req.responseText);
    } else if (req.status == 400) {
        alert(`Invalid request data: ${JSON.parse(req.responseText).detail}`)
    } else if (req.status == 401) {
        alert("Not authorized");
        redirectToLoginPage();
    } else if (req.status == 403) {
        alert("Insufficient permissions");
    } else if (req.status == 404) {
        alert("Not found");
    } else {
        alert("Internal error, please try again later");
    }
}

function makeSecureRequest(method, url, data, headers = {}) {
    if (isLoggedIn()) {
        const token = localStorage.getItem("token")
        let resp = makeRequest(method, url, data, Object.assign(headers, {"Authorization": `Bearer ${token}`}));
        return resp
    } else {
        alert("User is not authorized to do this action");
        redirectToLoginPage();
    }
}

function redirectToLoginPage() {
    window.location.replace("login.html")
}

function login(username, password) {
    const tokenData = makeRequest("POST", `${API_URL}/login`, {"username": username, "password": password});
    localStorage.setItem("token", tokenData.token)
    window.location.replace("index.html")
}

function fetchUsers() {
    return makeSecureRequest("GET", `${API_URL}/users`);
}

function updateUser(userId, data) {
    makeSecureRequest("PUT", `${API_URL}/users/${userId}`, data)
}

function deleteUser(userId) {
    makeSecureRequest("DELETE", `${API_URL}/users/${userId}`)
}

function createUser(data) {
    return makeSecureRequest("POST", `${API_URL}/users`, data)
}