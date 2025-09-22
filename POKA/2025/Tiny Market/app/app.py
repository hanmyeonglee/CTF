import base64
import hashlib
import json
import os
import uuid
import requests
import secrets
import re
import ipaddress
import unicodedata
from urllib.parse import urlparse
from flask import Flask, render_template, g, request, jsonify, send_from_directory, redirect, url_for, session, make_response
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['JSON_AS_ASCII'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'TBD')
    app.config['PERMANENT_SESSION_LIFETIME'] = 1500  # 25 minutes

    ALLOWED_CIDRS = [ipaddress.ip_network(c.strip()) for c in os.environ["ALLOWED_CIDR"].split(",")]
    DENY_GW = ipaddress.ip_network(os.environ["DENY_GW"])

    PRODUCT_ID_RE = re.compile(r"^prd_[0-9]{5}$", re.ASCII)
    ORDER_ID_RE = re.compile(r"^ord_[0-9]{5}$", re.ASCII)
    UUID_IMG_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\.(?:png|jpe?g)$", re.IGNORECASE | re.ASCII)
    GATEWAY_PATH_RE = re.compile(r'^[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*$', re.ASCII)
    PATH_RE = re.compile(r'^/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*$', re.ASCII)

    # Ensure uploads directory exists
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    @app.before_request
    def _issue_nonce():
        g.csp_nonce = base64.b64encode(os.urandom(16)).decode("ascii")

    @app.after_request
    def _set_security_headers(resp):
        nonce = getattr(g, "csp_nonce", "")

        report_url = os.environ.get('CSP_REPORT_URL', '/reports')

        csp = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic'; "
            f"style-src * 'nonce-{nonce}'; "
            f"style-src-elem * 'nonce-{nonce}'; "
            "font-src * data:; "
            "img-src * data:; "
            "style-src-attr 'unsafe-inline'; "
            "form-action 'self'; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'none'; "
            "frame-ancestors 'none'; "
            f"report-uri {report_url}; "
        )
        resp.headers.setdefault("Content-Security-Policy", csp)
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        
        # Disable caching only for static files (CSS, JS, images)
        if (request.endpoint == 'static' or 
            (resp.content_type and (
                resp.content_type.startswith('text/javascript') or
                resp.content_type.startswith('text/css') or
                resp.content_type.startswith('image/')
            ))):
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
        
        if resp.content_type and resp.content_type.startswith('application/json'):
            resp.content_type = 'application/json; charset=utf-8'
        
        return resp
    
    def call_api(path, method="GET", json=None, params=None):
        try:
            token = request.cookies.get("apiKey")
            headers = {"Accept": "application/json; charset=utf-8"}

            if token:
                headers["X-API-Key"] = token

            headers["X-CLIENT-IP"] = request.remote_addr

            url = f"http://api-server:8000/api/v1/{path.lstrip('/')}"

            resp = requests.request(method, url, headers=headers, json=json, params=params, timeout=8)
            resp.encoding = 'utf-8'

            if resp.status_code == 401:
                return {"error": "Unauthorized"}
            elif resp.status_code == 403:
                return {"error": "Forbidden"}
            elif resp.status_code == 400:
                return {"error": "Bad request"}
            elif resp.status_code == 409:
                return {"error": "Conflict"}
            elif resp.status_code == 422:
                return {"error": "Unprocessable entity"}
            elif resp.status_code == 404:
                return {"error": "Not found"}
            elif resp.status_code == 429:
                return {"error": "Rate limited"}
            elif resp.status_code == 500:
                return {"error": "Internal server error"}

            if resp.ok:
                try:
                    response = resp.json()

                    if response.get("error"):
                        return {"error": response.get("error")}

                    return response
                except ValueError:
                    try:
                        response = resp.text
                        return response
                    except ValueError:
                        return {"error": "Parsing error"}
            
            return {"error": "Unknown error"}
        except ConnectionError:
            return {"error": "Connection error to API server"}
        except Timeout:
            return {"error": "Request timeout"}
        except RequestException as e:
            return {"error": "Request error"}
        except Exception as e:
            return {"error": "Unexpected error"}

    def api_call_with_error_handling(path, method="GET", json=None, params=None):
        response = call_api(path, method, json, params)
        
        if isinstance(response, dict) and response.get("error"):
            error_message = response.get("error")

            if error_message == "Unauthorized":
                return "REDIRECT_LOGIN"
            elif error_message in ["Forbidden", "Not found", "Internal server error", "Unknown error"]:
                return "RENDER_404"
            else:
                return "RENDER_404"
        
        return response
    
    def generate_etag(data):
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        else:
            data_str = str(data)
    
        etag_value = hashlib.md5(data_str.encode('utf-8')).hexdigest()
        return f'"{etag_value}"'
    
    def check_etag_and_cache(data):
        etag = generate_etag(data)
        
        # Check if client has the same ETag (Strong ETag comparison)
        client_etag = (request.headers.get('If-None-Match') or '').strip()
        if client_etag and client_etag == etag:
            response = make_response('', 304)
            response.headers['ETag'] = etag
            response.headers['Cache-Control'] = 'max-age=600, must-revalidate'
            return response, True
        
        return None, bool(client_etag)

    def only_local_ip(ip_str):
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False

        if ip == DENY_GW:
            return False

        return any(ip in net for net in ALLOWED_CIDRS)

    def is_valid_id(raw, id_re):
        if not isinstance(raw, str):
            return False
        s = unicodedata.normalize("NFKC", raw)
        if not s.isascii():
            return False
        if not id_re.fullmatch(s):
            return False
        return True

    def extension_is_valid(extension):
        for ext in ["jpg", "jpeg", "png"]:
            if extension == ext:
                return True
        return False
    
    @app.route("/", methods=["GET"])
    def home():
        page = int(request.args.get("page", 0))
        pageSize = int(request.args.get("pageSize", 20))
        
        products = api_call_with_error_handling(method="GET", path=f"products", params={"page": page, "pageSize": pageSize})

        if products == "REDIRECT_LOGIN":
            return redirect(url_for("login"))
        elif products == "RENDER_404":
            return render_template("404.html"), 404
        elif not products or not isinstance(products, dict):
            return redirect(url_for("login"))

        return render_template("index.html", products=products.get("data", []))

    @app.route("/products/<string:product_id>", methods=["GET"])
    def product_detail(product_id: str):
        if not is_valid_id(product_id, PRODUCT_ID_RE):
            return render_template("404.html"), 404

        product = api_call_with_error_handling(f"products/{product_id}")

        if product == "REDIRECT_LOGIN":
            return redirect(url_for("login"))
        elif product == "RENDER_404" or not product:
            return render_template("404.html"), 404

        return render_template("product_detail.html", product=product, product_id=product_id)
    
    @app.route("/products/<string:product_id>/checkout", methods=["GET"])
    def checkout(product_id: str):
        if not is_valid_id(product_id, PRODUCT_ID_RE):
            return render_template("404.html"), 404

        product = api_call_with_error_handling(method="GET", path=f"products/{product_id}")
        profile = api_call_with_error_handling(method="GET", path="me/profile")

        if product == "REDIRECT_LOGIN" or profile == "REDIRECT_LOGIN":
            return redirect(url_for("login"))
        elif product == "RENDER_404" or profile == "RENDER_404" or not product or not profile:
            return render_template("404.html"), 404
        
        return render_template("checkout.html", product=product, profile=profile, product_id=product_id)
    
    @app.route("/products/<string:product_id>/orders", methods=["GET"])
    def orders(product_id: str):
        page = int(request.args.get("page", 0))
        pageSize = int(request.args.get("pageSize", 20))

        if not is_valid_id(product_id, PRODUCT_ID_RE):
            return render_template("404.html"), 404

        orders = api_call_with_error_handling(method="GET", path=f"products/{product_id}/orders", params={"page": page, "pageSize": pageSize})

        if orders == "REDIRECT_LOGIN":
            return redirect(url_for("login"))
        elif orders == "RENDER_404":
            return render_template("404.html"), 404
        elif not orders or not isinstance(orders, dict):
            return render_template("orders.html", orders=[], product_id=product_id)

        return render_template("orders.html", orders=orders.get("data", []), product_id=product_id)
    
    @app.route("/products/<string:product_id>/orders/<string:order_id>", methods=["GET"])
    def order_detail(product_id: str, order_id: str):
        if not is_valid_id(product_id, PRODUCT_ID_RE):
            return render_template("404.html"), 404

        if not is_valid_id(order_id, ORDER_ID_RE):
            return render_template("404.html"), 404

        product = api_call_with_error_handling(method="GET", path=f"products/{product_id}")
        order = api_call_with_error_handling(method="GET", path=f"products/{product_id}/orders/{order_id}")

        if product == "REDIRECT_LOGIN" or order == "REDIRECT_LOGIN":
            return redirect(url_for("login"))
        elif product == "RENDER_404" or order == "RENDER_404" or not product or not order:
            return render_template("404.html"), 404
        
        if order.get("status") != "PENDING":
            return render_template("404.html"), 404

        # Combine product and order data for ETag generation
        combined_data = {"product": product, "order": order}
        
        etag_response, revalidated = check_etag_and_cache(combined_data)
        if etag_response:
            return etag_response

        cache_settings = {"cache": True, "refresh": revalidated, "apiKey": request.cookies.get("apiKey")}

        response = make_response(render_template("order_detail.html", product=product, order=order, product_id=product_id, order_id=order_id, cache_settings=cache_settings))
        response.headers['ETag'] = generate_etag(combined_data)
        response.headers['Cache-Control'] = 'max-age=600, must-revalidate'
        return response
    
    @app.route("/profile", methods=["GET"])
    def profile():
        profile_data = api_call_with_error_handling(method="GET", path="me/profile")

        if profile_data == "REDIRECT_LOGIN" or not profile_data:
            return redirect(url_for("login"))
        elif profile_data == "RENDER_404":
            return render_template("404.html"), 404

        return render_template("profile.html", profile=profile_data)

    @app.route("/login", methods=["GET"])
    def login():
        return render_template("login.html")
    
    @app.route("/register", methods=["GET"])
    def register():
        return render_template("register.html")
    
    @app.route("/auth/session", methods=["POST"])
    def set_session_token():
        try:
            payload = request.get_json(silent=True) or {}
        except Exception:
            payload = {}
        token = payload.get("apiKey") or payload.get("token")
        if not token:
            return jsonify({"message": "Missing token"}), 400, {"Content-Type": "application/json"}

        # Generate gateway key and store in session
        gateway_key = secrets.token_urlsafe(32)
        session['gateway_key'] = gateway_key
        session.permanent = True

        resp = jsonify({"ok": True, "gateway_key": gateway_key})
        resp.set_cookie(
            "apiKey",
            token,
            httponly=True,
            secure=False,
            max_age=1800,
            samesite="Lax",
            path="/",
        )
        return resp
    
    @app.route("/gateway/<path:path>", methods=["GET", "POST", "PUT", "PATCH"])
    def gateway(path: str):
        if request.method not in ["GET", "POST", "PUT", "PATCH"]:
            return jsonify({"error": "Invalid method"}), 400, {"Content-Type": "application/json"}

        if (not path) or (not path.isascii()) or (not GATEWAY_PATH_RE.fullmatch(path)):
            return jsonify({"error": "Invalid path"}), 400, {"Content-Type": "application/json"}

        # Skip gateway key verification for auth endpoints
        auth_endpoints = ["auth/login", "auth/register"]
        if path not in auth_endpoints:
            # Verify gateway key for other endpoints
            client_gateway_key = request.headers.get("X-Gateway-Key")
            session_gateway_key = session.get("gateway_key")
            
            if not client_gateway_key or not session_gateway_key or client_gateway_key != session_gateway_key:
                return jsonify({"error": "Invalid or missing gateway key"}), 403, {"Content-Type": "application/json"}

        body = request.get_json(silent=True) or {}

        resp = api_call_with_error_handling(method=request.method, path=path, json=body, params=request.args.to_dict(flat=False))

        if resp == "REDIRECT_LOGIN":
            return jsonify({"error": "Unauthorized"}), 401, {"Content-Type": "application/json"}
        elif resp == "RENDER_404":
            return jsonify({"error": "Not found"}), 404, {"Content-Type": "application/json"}
        
        return jsonify(resp), 200, {"Content-Type": "application/json"}
    
    @app.route("/uploads", methods=["POST"])
    def uploads():
        file = request.files.get("image") or request.files.get("file")

        if file:
            filename = str(uuid.uuid4())
            extension = file.filename.split(".")[-1]

            if not extension_is_valid(extension):
                return jsonify({"message": "Invalid file extension"}), 400, {"Content-Type": "application/json"}

            filename = f"{filename}.{extension}"
            file.save(os.path.join(uploads_dir, filename))

            return jsonify({"message": "File uploaded successfully", "url": f"/uploads/{filename}"}), 200
        
        return jsonify({"message": "No file uploaded"}), 400, {"Content-Type": "application/json"}
    
    @app.route("/uploads/<string:filename>", methods=["GET"])
    def get_file(filename: str):
        if not UUID_IMG_RE.fullmatch(filename):
            return jsonify({"message": "Invalid filename"}), 400, {"Content-Type": "application/json"}
        
        if not os.path.exists(os.path.join(uploads_dir, filename)):
            return jsonify({"message": "File not found"}), 404, {"Content-Type": "application/json"}

        return send_from_directory(uploads_dir, filename)

    @app.route("/reports", methods=["POST"])
    def csp_reports():
        request_body = request.get_data(as_text=True)
        request_body = json.loads(request_body)

        if not request_body.get("csp-report"):
            return jsonify({"message": "Report not received"}), 400, {"Content-Type": "application/json"}

        print(request_body.get("csp-report"))

        return jsonify({"message": "Report received"}), 200, {"Content-Type": "application/json"}

    # only for admin
    @app.route("/health", methods=["GET", "POST"])
    def health_checker():
        if request.method == "POST":
            return "METHOD_NOT_ALLOWED", 405
        
        if not only_local_ip(request.remote_addr):
            return "FORBIDDEN", 403
        
        method = request.args.get("method", "GET")
        path = request.args.get("path", "")
        body = request.args.get("body", "")
        submit = request.args.get("submit", "submitBtn")

        if method not in ["GET", "POST"]:
            return "INVALID_METHOD", 400

        if "<" in body or ">" in body:
            return "INVALID_BODY", 400
        
        if path and not PATH_RE.fullmatch(path):
            return "INVALID_PATH", 400
        
        return render_template("health_checker.html", method=method, path=path, body=body, submit=submit)

    # only for admin
    @app.route("/settings", methods=["PATCH"])
    def update_settings():
        if not only_local_ip(request.remote_addr):
            return "FORBIDDEN", 403

        request_body = request.get_json(silent=True) or {}

        setting_type = request_body.get("type")
        setting_value = request_body.get("value")

        if not isinstance(setting_value, str) or not setting_value:
            return jsonify({"message": "Invalid type or value"}), 400, {"Content-Type": "application/json"}

        if setting_type == "changeReportURL":
            report_url = setting_value.strip()

            if any(ch in report_url for ch in (";", "'", '"', "\\", "`", " ", "\t", "\r", "\n", "..")):
                return jsonify({"message": "Invalid characters"}), 400, {"Content-Type": "application/json"}

            allowed_relative_paths = {"/reports", "/csp/reports"}
            path_regex = re.compile(r"^/[a-z0-9/_\-.]{1,200}$")

            if report_url.startswith("/"):
                if not path_regex.fullmatch(report_url):
                    return jsonify({"message": "Invalid path"}), 400, {"Content-Type": "application/json"}
                if report_url not in allowed_relative_paths:
                    return jsonify({"message": "Path not allowed"}), 400, {"Content-Type": "application/json"}
                new_report_url = report_url
            else:
                parsed_url = urlparse(report_url)

                if not parsed_url.hostname or parsed_url.username or parsed_url.password or parsed_url.fragment:
                    return jsonify({"message": "Invalid URL"}), 400, {"Content-Type": "application/json"}

                hostname = parsed_url.hostname.lower()
                request_path = parsed_url.path or "/"

                if any(ch in request_path for ch in (";", "'", '"', "\\", "`", " ", "\t", "\r", "\n")):
                    return jsonify({"message": "Invalid characters in path"}), 400, {"Content-Type": "application/json"}
                if not path_regex.fullmatch(request_path):
                    return jsonify({"message": "Invalid path"}), 400, {"Content-Type": "application/json"}
                if parsed_url.query:
                    return jsonify({"message": "Query not allowed"}), 400, {"Content-Type": "application/json"}

                new_report_url = f"https://{hostname}{request_path}"

            os.environ["CSP_REPORT_URL"] = new_report_url

            return jsonify({"message": "Report changed", "url": new_report_url}), 200
        elif setting_type == "changeRequestTimeout":
            setting_value = setting_value.lower().strip()

            if not setting_value.isdigit():
                return jsonify({"message": "Invalid request timeout"}), 400, {"Content-Type": "application/json"}
            
            os.environ["REQUEST_TIMEOUT_MS"] = setting_value

            return jsonify({"message": "Request timeout changed", "timeout": setting_value}), 200
        else:
            return jsonify({"message": "Invalid type"}), 400, {"Content-Type": "application/json"}

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)


