from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def api_handler():
    data = request.json
    action = data.get('action')
    access = data.get('access')
    email = data.get('email', '')
    otp = data.get('otp', '')

    try:
        # 1. CHECK BIND INFO
        if action == "check":
            url = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
            r = requests.get(url, params={'app_id': "100067", 'access_token': access}, headers=HEADERS)
            return jsonify(r.json())

        # 2. SEND OTP
        elif action == "send_otp":
            url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
            pyl = {'app_id': "100067", 'access_token': access, 'email': email, 'locale': "en_MA"}
            r = requests.post(url, data=pyl, headers=HEADERS)
            return jsonify(r.json())

        # 3. VERIFY OTP & ADD EMAIL
        elif action == "verify_otp":
            # Verify OTP first
            v_url = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
            v_pyl = {'app_id': "100067", 'access_token': access, 'otp': otp, 'email': email}
            v_rsp = requests.post(v_url, data=v_pyl, headers=HEADERS)
            
            if v_rsp.status_code == 200:
                auth_token = v_rsp.json().get("verifier_token")
                # Cancel existing first (as per your script)
                requests.post("https://100067.connect.garena.com/game/account_security/bind:cancel_request", data={'app_id':"100067",'access_token':access}, headers=HEADERS)
                # Now Add/Bind
                a_url = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
                a_pyl = {'app_id': "100067", 'access_token': access, 'verifier_token': auth_token, 'secondary_password': "91B4D142823F7D20C5F08DF69122DE43F35F057A988D9619F6D3138485C9A203", 'email': email}
                a_rsp = requests.post(a_url, data=a_pyl, headers=HEADERS)
                return jsonify(a_rsp.json())
            return jsonify(v_rsp.json())

        # 4. CHECK LINKS
        elif action == "platforms":
            url = "https://100067.connect.garena.com/bind/app/platform/info/get"
            r = requests.get(url, params={'access_token': access}, headers=HEADERS)
            return jsonify(r.json())

        # 5. CANCEL
        elif action == "cancel":
            url = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
            r = requests.post(url, data={'app_id': "100067", 'access_token': access}, headers=HEADERS)
            return jsonify(r.json())

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
