(function (global) {
  global.MakeQueryParser = function () {
    const QueryParser = function () {
      return QueryParser.parseQuery.apply(QueryParser, arguments);
    };

    QueryParser.parseQuery = function (input = "") {
      const replacePlus = s => s.replace(/\+/g, " ");
      const safeDecode = s => { try { return decodeURIComponent(s); } catch { return s; } };
      const obj = {};
      let q = String(input || "");
      if (q.includes("?")) q = q.split("?")[1];
      if (q.includes("#")) q = q.split("#")[0];
      if (!q) return obj;

      const out = obj;

      for (const pair of q.split("&")) {
        if (!pair) continue;
        const [rawKey, ...rest] = pair.split("=");
        const rawVal = rest.join("=");

        const key = safeDecode(replacePlus(rawKey || ""));
        const val = safeDecode(replacePlus(rawVal || ""));
        if (!key) continue;

        const tokens = QueryParser.parseKey(key);
        QueryParser.assign(out, tokens, val);
      }
      return out;
    };

    QueryParser.parseKey = function (k) {
      const first = k.indexOf("[");
      if (first === -1) return [k];
      const head = k.slice(0, first);
      const tail = k.slice(first);
      const parts = [head];
      const re = /\[([^\]]*)\]/g;
      let m;
      while ((m = re.exec(tail)) !== null) parts.push(m[1]);
      return parts;
    };

    QueryParser.isNumericKey = function (s) { return /^\d+$/.test(s); };
    QueryParser.isArrayishToken = function (s) { return s === "" || QueryParser.isNumericKey(s) || s === "*"; };

    QueryParser.ensureArray = function (obj, key) {
      if (key == null) return obj;
      const cur = obj[key];
      if (Array.isArray(cur)) return cur;
      if (cur === undefined) { obj[key] = []; return obj[key]; }
      obj[key] = [cur];
      return obj[key];
    };

    QueryParser.setValue = function (obj, key, value) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        const cur = obj[key];
        if (Array.isArray(cur)) cur.push(value);
        else obj[key] = [cur, value];
      } else {
        obj[key] = value;
      }
    };

    QueryParser.assign = function (root, tokens, value) {
      let parent = root;
      let prevKey = null;

      for (let i = 0; i < tokens.length; i++) {
        let token = tokens[i];
        const last = i === tokens.length - 1;

        if (last) {
          if (token === "") {
            if (Array.isArray(parent)) parent.push(value);
            else if (prevKey != null) QueryParser.ensureArray(parent, prevKey).push(value);
          } else if (Array.isArray(parent) && QueryParser.isNumericKey(token)) {
            const idx = Number(token);
            if (parent[idx] === undefined) parent[idx] = value;
            else if (Array.isArray(parent[idx])) parent[idx].push(value);
            else parent[idx] = [parent[idx], value];
          } else {
            QueryParser.setValue(parent, token, value);
          }
          return;
        }

        const next = tokens[i + 1];
        const nextIsArrayish = QueryParser.isArrayishToken(next);

        if (Array.isArray(parent) && QueryParser.isNumericKey(token)) {
          const idx = Number(token);
          if (parent[idx] === undefined || typeof parent[idx] !== "object") {
            parent[idx] = nextIsArrayish ? [] : {};
          }
          parent = parent[idx];
          prevKey = null;
          continue;
        }

        if (token === "") {
          if (prevKey != null) {
            const arr = QueryParser.ensureArray(parent, prevKey);
            if (!arr.length || typeof arr[arr.length - 1] !== "object") arr.push(nextIsArrayish ? [] : {});
            parent = arr[arr.length - 1];
            prevKey = null;
          } else {
            if (!Array.isArray(parent)) return;
          }
          continue;
        }

        const cur = parent[token];
        if (typeof cur !== "object" || cur === null) parent[token] = nextIsArrayish ? [] : {};
        prevKey = token;
        parent = parent[token];
      }
    };

    return QueryParser;
  };

  if (typeof define === 'function' && define.amd) {
    define(function () { return global.MakeQueryParser(); });
  } else if (typeof module === 'object' && module.exports) {
    module.exports = global.MakeQueryParser();
  } else {
    global.QueryParser = global.MakeQueryParser();
  }
})(window);
